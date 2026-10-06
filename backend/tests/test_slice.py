import json
import socket
from unittest.mock import patch
import httpx
import pytest
from fastapi.testclient import TestClient
from rolegrep.eligibility import evaluate_eligibility
from rolegrep.fixture import test_candidate as candidate_fixture
from rolegrep.greenhouse import GreenhouseSource, IngestionError, normalize_greenhouse, resolve_url, validate_public_api_host
from rolegrep.main import create_app
from rolegrep.matching import match_job
from rolegrep.normalization import DeterministicExtractor, text_job


def extracted(text, title="Junior Backend Developer"):
    job = text_job(text)
    job.title = title
    return DeterministicExtractor().extract(job)


@pytest.mark.parametrize("wording,status,adjustment", [
    ("0 years experience required", "eligible", 3),
    ("No experience required", "eligible", 3),
    ("1 year experience required", "eligible", 0),
    ("1+ year experience required", "eligible", 0),
    ("2 years experience required", "eligible", -10),
    ("2+ years experience required", "eligible", -10),
    ("3+ years experience required", "ineligible", 0),
    ("5+ years experience required", "ineligible", 0),
    ("3 years Python experience preferred", "eligible", 0),
    ("Several years experience", "uncertain", 0),
    ("2-4 years experience required", "uncertain", 0),
    ("3 years experience or equivalent required", "uncertain", 0),
])
def test_experience(wording, status, adjustment):
    result = evaluate_eligibility(extracted(wording), candidate_fixture())
    assert result.status == status
    assert result.experience_adjustment == adjustment


@pytest.mark.parametrize("title", ["Senior Developer", "Staff Engineer", "Principal Engineer"])
def test_senior(title):
    assert evaluate_eligibility(extracted("No experience required", title), candidate_fixture()).status == "ineligible"


def test_unknowns_and_conflicts():
    job = extracted("Remote role.\nMust work onsite.", title="Developer")
    assert job.posted_at is None and job.education is None and job.arrangement is None
    assert job.conflicts[0].values == ["Remote", "In-person"]
    assert evaluate_eligibility(job, candidate_fixture()).status == "uncertain"


def test_preferred_gap_and_qualification_dominance():
    profile = candidate_fixture()
    job = extracted("Requirements\nPython\nNo experience required\nPreferred\nReact\n3 years experience preferred")
    result = match_job(job, profile, evaluate_eligibility(job, profile))
    assert result.overall <= result.qualification
    assert any("Preferred React" in gap for gap in result.gaps)
    assert any("Preferred experience" in gap for gap in result.gaps)
    assert result.strong and "Synthetic" in result.strong[0]


def test_unscored_and_manual_preference_override():
    client = TestClient(create_app())
    decision = client.post("/jobs/ingest", json={"text": "Requirements\nUnity and C#\nNo experience required"}).json()
    assert decision["match"]["concerns"]
    assert decision["match"]["overall"] == 0
    assert client.post("/jobs/ingest", json={"text": "An unspecified opportunity"}).json()["match"]["overall"] is None


def payload():
    return {"id": 123, "title": "Junior Backend Developer", "company_name": "Synthetic Company", "content": "<h2>Requirements</h2><p>Python and FastAPI</p><p>1 year experience required</p>", "location": {"name": "Remote"}, "absolute_url": "https://job-boards.greenhouse.io/example/jobs/123", "updated_at": "2026-10-01T00:00:00Z"}


def source_for(handler):
    return GreenhouseSource(transport=httpx.MockTransport(handler), check_host=lambda: None)


def test_greenhouse_api_roundtrip_and_deduplication():
    seen = []
    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(200, json=payload())
    client = TestClient(create_app(source=source_for(handler)))
    body = {"url": "https://job-boards.greenhouse.io/example/jobs/123"}
    result = client.post("/jobs/ingest", json=body)
    assert result.status_code == 200
    decision = result.json()
    assert decision["job"]["posted_at"] is None # updated_at is not posted_at
    assert decision["job"]["company"] == "Synthetic Company"
    assert decision["eligibility"]["status"] == "eligible"
    assert "boards-api.greenhouse.io/v1/boards/example/jobs/123" in seen[0]
    for _ in range(7):
        assert client.post("/jobs/ingest", json=body).status_code == 200
    cards = client.get("/jobs").json()
    assert len(cards) == 1
    detail = client.get("/jobs/" + cards[0]["id"]).json()
    assert len(detail["job"]["sources"]) == 5
    assert detail["job"]["discovered_at"] == decision["job"]["discovered_at"]
    assert client.get("/jobs/no-such-job").status_code == 404
    assert client.get("/health").json()["storage"] == "in-memory"


@pytest.mark.parametrize("url", ["http://boards.greenhouse.io/a/jobs/1", "https://127.0.0.1/a/jobs/1", "https://localhost/a/jobs/1", "https://boards.greenhouse.io.evil.test/a/jobs/1", "https://user:secret@boards.greenhouse.io/a/jobs/1", "https://boards.greenhouse.io:8080/a/jobs/1", "https://www.linkedin.com/jobs/view/1", "https://boards.greenhouse.io/a/jobs/../1"])
def test_url_restrictions(url):
    with pytest.raises(IngestionError):
        resolve_url(url)


def test_private_dns():
    with patch("socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]):
        with pytest.raises(IngestionError):
            validate_public_api_host()


@pytest.mark.parametrize("response", [httpx.Response(302, headers={"location": "http://127.0.0.1"}), httpx.Response(200, content=b"x" * 256001), httpx.Response(200, content=b"not json"), httpx.Response(404), httpx.Response(200, json={"id": 123, "content": "x" * 40001})])
def test_fetch_limits(response):
    with pytest.raises(IngestionError):
        source_for(lambda request: response).fetch("https://boards.greenhouse.io/example/jobs/123")


def test_timeout():
    def timeout(request):
        raise httpx.ReadTimeout("timeout", request=request)
    with pytest.raises(IngestionError):
        source_for(timeout).fetch("https://boards.greenhouse.io/example/jobs/123")


def test_request_validation_and_fallback():
    client = TestClient(create_app())
    for body in [{}, {"url": "x", "text": "x"}, {"text": " "}, {"text": "x" * 40001}]:
        assert client.post("/jobs/ingest", json=body).status_code == 422
    error = client.post("/jobs/ingest", json={"url": "https://jobright.ai/jobs/1"})
    assert error.status_code == 422
    assert "next_action" in error.json()["detail"]


def test_profile_location_rules_and_html():
    job = extracted("No experience required\n<script>alert(1)</script>Python")
    assert "alert" not in job.description
    profile = candidate_fixture()
    profile.allowed_locations = ["Edmonton"]
    assert evaluate_eligibility(job, profile).status == "uncertain"
    job.location = "London"
    assert evaluate_eligibility(job, profile).status == "ineligible"


def test_source_dates_salary_and_invalid_date():
    data = payload()
    data.update(first_published="2026-10-01T00:00:00Z", application_deadline="not-a-date", pay_input_ranges=[{"min_cents":5000000,"max_cents":7500000,"currency_type":"USD"}])
    job = normalize_greenhouse(data, "https://boards.greenhouse.io/example/jobs/123", "https://boards-api.greenhouse.io", "example", "123")
    assert job.posted_at.year == 2026
    assert job.deadline is None
    assert "50000" in job.salary
    assert "not-a-date" in job.sources[0].snapshot
    assert job.limitations


def test_conflicting_classification_is_uncertain():
    job = extracted("Minimum 3 years experience required but preferred")
    assert job.experience[0].kind == "uncertain"
    assert evaluate_eligibility(job, candidate_fixture()).status == "uncertain"


def test_total_fetch_budget():
    with patch("rolegrep.greenhouse.time.monotonic", side_effect=[0, 21]):
        with pytest.raises(IngestionError, match="time budget"):
            source_for(lambda request: httpx.Response(200, json=payload())).fetch("https://boards.greenhouse.io/example/jobs/123")


def test_multiple_required_minimums_use_strictest():
    result = evaluate_eligibility(extracted("No experience required\n1 year Python experience required"), candidate_fixture())
    assert result.experience_adjustment == 0


@pytest.mark.parametrize("url", [
    "https://boards.greenhouse.io:bad/example/jobs/123",
    "https://boards.greenhouse.io:65536/example/jobs/123",
    "https://boards.greenhouse.io:-1/example/jobs/123",
    "https://boards.greenhouse.io:/example/jobs/123",
    "https://[invalid/example/jobs/123",
    "https://[invalid]/example/jobs/123",
    "https://boards.greenhouse.io]/example/jobs/123",
    "https://[::1]suffix/example/jobs/123",
    "https:///example/jobs/123",
    "https://:443/example/jobs/123",
    "https://boards..greenhouse.io/example/jobs/123",
    "https://-boards.greenhouse.io/example/jobs/123",
    "https://boards_.greenhouse.io/example/jobs/123",
    "https://boards.greenhouse.io／evil/example/jobs/123",
    " https://boards.greenhouse.io/example/jobs/123",
    "https://boards.greenhouse.io/exam\nple/jobs/123",
    "https://boards.greenhouse.io/example/jobs/123?x=\x00",
    "https://boards.greenhouse.io\\evil/example/jobs/123",
    "https://boards.greenhouse.io/example/jobs/123?x=%ZZ",
    "https://boards.greenhouse.io/example/jobs/123?x=%",
    "https://@boards.greenhouse.io/example/jobs/123",
])
def test_malformed_urls_return_structured_validation_without_fetch(url):
    with patch("rolegrep.greenhouse.validate_public_api_host") as check_host:
        source = GreenhouseSource(check_host=check_host)
        client = TestClient(create_app(source=source))
        response = client.post("/jobs/ingest", json={"url": url})
        assert response.status_code == 422
        assert "message" in response.json()["detail"]
        assert "next_action" in response.json()["detail"]
        check_host.assert_not_called()
        assert client.get("/jobs").json() == []


@pytest.mark.parametrize("url", [
    "https://boards.greenhouse.io/example/jobs/123",
    "https://job-boards.greenhouse.io:443/example/jobs/123/?gh_src=abc%20def#application",
    "https://BOARDS.GREENHOUSE.IO/example/jobs/123",
])
def test_valid_posting_urls_still_resolve(url):
    assert resolve_url(url) == ("example", "123")


@pytest.mark.parametrize("application", ["https://[invalid", "https://example.com:bad/apply", "https:///apply"])
def test_malformed_source_application_url_falls_back_safely(application):
    data = payload()
    data["absolute_url"] = application
    url = "https://boards.greenhouse.io/example/jobs/123"
    job = normalize_greenhouse(data, url, "https://boards-api.greenhouse.io", "example", "123")
    assert job.application_url == url
