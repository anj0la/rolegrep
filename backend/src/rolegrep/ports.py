from typing import Protocol
from .models import Job, JobDecision


class JobRepository(Protocol):
    def save(self, decision: JobDecision) -> None: ...
    def get(self, job_id: str) -> JobDecision | None: ...
    def list(self) -> list[JobDecision]: ...


class JobSource(Protocol):
    def fetch(self, url: str) -> Job: ...


class JobExtractor(Protocol):
    """Optional AI extraction can implement this boundary later."""
    def extract(self, job: Job) -> Job: ...


class InMemoryJobRepository:
    def __init__(self):
        self.items: dict[str, JobDecision] = {}

    def save(self, decision: JobDecision) -> None:
        previous = self.items.get(decision.job.id)
        if previous:
            decision.job.discovered_at = previous.job.discovered_at
            decision.job.sources = (previous.job.sources + decision.job.sources)[-5:]
        self.items[decision.job.id] = decision

    def get(self, job_id: str) -> JobDecision | None:
        return self.items.get(job_id)

    def list(self) -> list[JobDecision]:
        return list(self.items.values())
