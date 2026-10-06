import hashlib
import html
import re
from html.parser import HTMLParser
from .models import Job, ExperienceRequirement, FieldConflict, SourceEvidence

TECHNOLOGIES = ["Python", "FastAPI", "Docker", "PostgreSQL", "SQL", "Git", "React", "TypeScript", "JavaScript", "C++", "C#", ".NET", "Unity", "Godot", "Unreal", "Java", "Spring", "Rust", "Go"]


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"p", "li", "div", "br", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        if tag in {"p", "li", "div", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain_text(value: str) -> str:
    parser = TextParser()
    parser.feed(html.unescape(value))
    return "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())


def has_term(text: str, term: str) -> bool:
    return bool(re.search(r"(?<![\w])" + re.escape(term) + r"(?![\w+#])", text, re.I))


class DeterministicExtractor:
    def extract(self, job: Job) -> Job:
        section = "uncertain"
        for line in job.description.splitlines():
            lower = line.lower()
            if re.fullmatch(r"(?:required qualifications|requirements|qualifications|what you bring):?", lower):
                section = "required"
                continue
            if re.fullmatch(r"(?:preferred qualifications|preferred|nice to have|bonus):?", lower):
                section = "preferred"
                continue
            if re.fullmatch(r"(?:responsibilities|benefits|about us|what you.?ll do):?", lower):
                section = "uncertain"
            skills = [term for term in TECHNOLOGIES if has_term(line, term)]
            job.technologies = sorted(set(job.technologies + skills))
            kind = "preferred" if re.search(r"preferred|nice.to.have|bonus", lower) else "required" if re.search(r"required|minimum|at least|must have", lower) else section
            if re.search(r"required|minimum|must have", lower) and re.search(r"preferred|nice.to.have", lower):
                kind = "uncertain"
                job.conflicts.append(FieldConflict(field="requirement classification", values=["required", "preferred"], evidence=[line]))
            if re.search(r"\byears?\b", lower) and re.search(r"experience|\bexp\b", lower):
                number = re.search(r"\b(\d+)\s*(?:\+)?\s*years?\b", lower)
                ambiguous = bool(re.search(r"\d+\s*[-–]\s*\d+|\bor\b|equivalent|up to", lower))
                job.experience.append(ExperienceRequirement(kind="uncertain" if ambiguous else kind, minimum=int(number[1]) if number and not ambiguous else None, wording=line))
            elif re.search(r"no (?:prior )?experience|0 years", lower):
                job.experience.append(ExperienceRequirement(kind="required", minimum=0, wording=line))
            if kind == "required":
                job.required_skills = sorted(set(job.required_skills + skills))
            elif kind == "preferred":
                job.preferred_skills = sorted(set(job.preferred_skills + skills))
            if "bachelor" in lower:
                job.education = line
        title = job.title or ""
        job.level = "Senior" if re.search(r"\b(senior|staff|principal)\b", title, re.I) else "Early Career" if re.search(r"\b(junior|entry.level|new.grad|early.career)\b", title, re.I) else None
        arrangements = [label for label, pattern in [("Remote", r"\bremote\b"), ("Hybrid", r"\bhybrid\b"), ("In-person", r"\b(?:in.person|on.site|onsite)\b")] if re.search(pattern, job.description + " " + (job.location or ""), re.I)]
        if len(arrangements) == 1:
            job.arrangement = arrangements[0]
        elif len(arrangements) > 1:
            job.conflicts.append(FieldConflict(field="arrangement", values=arrangements, evidence=[line for line in job.description.splitlines() if re.search(r"remote|hybrid|onsite|on.site|in.person", line, re.I)] + ([job.location] if job.location else [])))
        job.limitations.append("Conservative deterministic extraction; unrecognized requirements remain in the source snapshot for review.")
        return job


def text_job(text: str, source_url: str | None = None) -> Job:
    description = plain_text(text)
    digest = hashlib.sha256(description.encode()).hexdigest()
    return Job(id="text-" + digest[:20], description=description,
               sources=[SourceEvidence(provider="Manual text", submitted_url=source_url, content_hash=digest, snapshot=description)])
