import hashlib
import ipaddress
import json
import re
import socket
import time
from urllib.parse import urlsplit
import httpx
from .models import Job, SourceEvidence
from .normalization import plain_text

MAX_RESPONSE = 256000


class IngestionError(ValueError):
    pass


def parse_public_url(url: str):
    """Reject malformed HTTPS URLs before urllib can normalize or discard input."""
    try:
        if not url or re.search(r'[\s\x00-\x1f\x7f\\<>"{}|^`]', url) or re.search(r"%(?![0-9a-fA-F]{2})", url):
            raise ValueError("Invalid URL characters")
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port  # Access can raise for malformed or out-of-range ports.
        if parsed.scheme != "https" or not host or parsed.username is not None or parsed.password is not None:
            raise ValueError("Expected an absolute HTTPS URL without credentials")
        if parsed.netloc.endswith(":"):
            raise ValueError("Empty port")
        if ":" in host:
            ipaddress.IPv6Address(host)
            if not re.fullmatch(r"\[[0-9a-fA-F:.]+\](?::[0-9]+)?", parsed.netloc):
                raise ValueError("Invalid IPv6 authority")
        else:
            if len(host) > 253 or any(not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label) for label in host.split(".")):
                raise ValueError("Invalid hostname")
        return parsed
    except ValueError as error:
        raise IngestionError("Invalid posting URL. Use a well-formed public HTTPS URL or paste the job description.") from error


def resolve_url(url: str) -> tuple[str, str]:
    parsed = parse_public_url(url)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise IngestionError("Use a public HTTPS Greenhouse posting URL, or paste the job description.")
    if parsed.hostname not in {"boards.greenhouse.io", "job-boards.greenhouse.io"}:
        raise IngestionError("This slice supports public Greenhouse postings. Supply the employer's Greenhouse URL or paste the job description; authenticated sites will not be accessed.")
    match = re.fullmatch(r"/([A-Za-z0-9_-]+)/jobs/(\d+)/?", parsed.path)
    if not match:
        raise IngestionError("Use a Greenhouse URL containing /board/jobs/posting-id, or paste the description.")
    return match[1], match[2]


def validate_public_api_host():
    addresses = socket.getaddrinfo("boards-api.greenhouse.io", 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise IngestionError("Greenhouse resolved to a non-public address; fetch refused.")


class GreenhouseSource:
    def __init__(self, transport=None, check_host=validate_public_api_host):
        self.transport = transport
        self.check_host = check_host

    def fetch(self, url: str) -> Job:
        board, posting = resolve_url(url)
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{posting}?pay_transparency=true"
        started = time.monotonic()
        try:
            self.check_host()
            with httpx.Client(timeout=httpx.Timeout(10), follow_redirects=False, trust_env=False, transport=self.transport) as client:
                with client.stream("GET", api_url) as response:
                    if response.is_redirect:
                        raise IngestionError("Unexpected Greenhouse redirect; paste the description instead.")
                    response.raise_for_status()
                    chunks, size = [], 0
                    for chunk in response.iter_bytes():
                        if time.monotonic() - started > 20:
                            raise IngestionError("Source fetch exceeded its total time budget.")
                        size += len(chunk)
                        if size > MAX_RESPONSE:
                            raise IngestionError("Source response exceeds 256 KB limit; paste a shorter description.")
                        chunks.append(chunk)
                    payload = json.loads(b"".join(chunks))
        except (httpx.HTTPError, OSError, json.JSONDecodeError) as error:
            raise IngestionError("Unable to fetch this public posting; supply another employer URL or paste the description.") from error
        return normalize_greenhouse(payload, url, api_url, board, posting)


def normalize_greenhouse(payload, url, api_url, board, posting) -> Job:
    if not isinstance(payload, dict) or str(payload.get("id")) != posting or not isinstance(payload.get("content"), str):
        raise IngestionError("Invalid Greenhouse posting response.")
    description = plain_text(payload["content"])
    if not description or len(description) > 40000:
        raise IngestionError("Description is empty or exceeds 40,000 characters.")
    title, company = payload.get("title"), payload.get("company_name")
    if any(value is not None and (not isinstance(value, str) or len(value) > 500) for value in (title, company)):
        raise IngestionError("Invalid source title/company.")
    application = payload.get("absolute_url")
    try:
        if not isinstance(application, str):
            raise IngestionError("Missing application URL")
        parse_public_url(application)
    except IngestionError:
        application = url
    snapshot = json.dumps({key: payload.get(key) for key in ["id", "title", "company_name", "location", "first_published", "application_deadline", "absolute_url"]}, ensure_ascii=False)
    snapshot += "\n" + description
    digest = hashlib.sha256(snapshot.encode()).hexdigest()
    limitations = []
    if len(snapshot) > 40000:
        limitations.append("Source snapshot truncated to 40,000 characters; complete bounded description retained separately.")
    dates = {}
    from datetime import datetime
    for source, target in [("first_published", "posted_at"), ("application_deadline", "deadline")]:
        try:
            value = payload.get(source)
            date = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
            if date and date.tzinfo is None:
                raise ValueError()
            dates[target] = date
        except ValueError:
            dates[target] = None
            limitations.append(f"Invalid {source} retained in source snapshot; normalized date unknown.")
    location = payload.get("location")
    location = location.get("name") if isinstance(location, dict) else None
    if location is not None and (not isinstance(location, str) or len(location) > 1000):
        raise IngestionError("Invalid source location.")
    pay = payload.get("pay_input_ranges")
    salary = None
    if isinstance(pay, list):
        ranges = []
        for item in pay[:10]:
            if isinstance(item, dict) and isinstance(item.get("min_cents"), (int, float)) and isinstance(item.get("max_cents"), (int, float)):
                ranges.append(f"{str(item.get('currency_type', 'Unknown currency'))[:20]} {item['min_cents']/100:g}–{item['max_cents']/100:g} (source range; pay period unknown)")
        salary = "; ".join(ranges) or None
    return Job(id=f"greenhouse-{board}-{posting}", title=title, company=company, salary=salary,
               description=description, location=location, application_url=application, limitations=limitations,
               sources=[SourceEvidence(provider="Greenhouse", submitted_url=url, fetched_url=api_url, posting_id=posting,
                                       content_hash=digest, snapshot=snapshot[:40000])], **dates)
