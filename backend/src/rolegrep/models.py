from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class ExperienceRequirement(BaseModel):
    kind: Literal["required", "preferred", "uncertain"]
    minimum: int | None = None
    wording: str


class FieldConflict(BaseModel):
    field: str
    values: list[str]
    evidence: list[str]


class SourceEvidence(BaseModel):
    provider: str
    submitted_url: str | None = None
    fetched_url: str | None = None
    posting_id: str | None = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: str
    snapshot: str = Field(max_length=40000)


class Job(BaseModel):
    id: str
    title: str | None = None
    company: str | None = None
    description: str = Field(max_length=40000)
    location: str | None = None
    arrangement: str | None = None
    level: str | None = None
    experience: list[ExperienceRequirement] = Field(default_factory=list)
    education: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    role_family: str | None = None
    salary: str | None = None
    deadline: datetime | None = None
    posted_at: datetime | None = None
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    application_url: str | None = None
    cover_letter: str | None = None
    sources: list[SourceEvidence]
    conflicts: list[FieldConflict] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class SkillEvidence(BaseModel):
    strength: Literal["strong", "moderate", "weak"]
    source: str


class CandidateProfile(BaseModel):
    version: str
    fixture: bool = True
    skills: dict[str, SkillEvidence]
    max_required_years: int = 2
    avoided_technologies: list[str] = Field(default_factory=list)
    discovery_exclusions: list[str] = Field(default_factory=list)
    arrangement_order: list[str] = Field(default_factory=list)
    allowed_locations: list[str] | None = None
    allowed_arrangements: list[str] | None = None
    work_authorization: str | None = None


class EligibilityResult(BaseModel):
    status: Literal["eligible", "ineligible", "uncertain"]
    reasons: list[str]
    experience_adjustment: int = 0


class MatchResult(BaseModel):
    overall: int | None
    qualification: int | None
    personal: int
    provisional: bool = True
    algorithm_version: str = "fixture-rules-v1"
    candidate_version: str
    strong: list[str]
    partial: list[str]
    gaps: list[str]
    concerns: list[str]
    explanation: str


class JobDecision(BaseModel):
    job: Job
    eligibility: EligibilityResult
    match: MatchResult
