from typing import Annotated
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, model_validator
from .eligibility import evaluate_eligibility
from .fixture import test_candidate
from .greenhouse import GreenhouseSource, IngestionError
from .matching import match_job
from .models import JobDecision
from .normalization import DeterministicExtractor, text_job
from .ports import InMemoryJobRepository


class IngestRequest(BaseModel):
    url: Annotated[str | None, Field(max_length=2000)] = None
    text: Annotated[str | None, Field(min_length=1, max_length=40000)] = None
    source_url: Annotated[str | None, Field(max_length=2000)] = None

    @model_validator(mode="after")
    def one_input(self):
        if bool(self.url) == bool(self.text):
            raise ValueError("Supply exactly one URL or description.")
        return self


def create_app(repository=None, source=None, extractor=None):
    app = FastAPI(title="rolegrep — local Phase 1")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    repository = repository or InMemoryJobRepository()
    source = source or GreenhouseSource()
    extractor = extractor or DeterministicExtractor()
    candidate = test_candidate()

    @app.get("/health")
    def health():
        return {"status": "ok", "candidate": "synthetic fixture", "storage": "in-memory"}

    @app.post("/jobs/ingest", response_model=JobDecision)
    def ingest(request: IngestRequest):
        try:
            job = source.fetch(request.url) if request.url else text_job(request.text, request.source_url)
            if not job.description.strip():
                raise IngestionError("Paste a nonempty job description.")
            job = extractor.extract(job)
            eligibility = evaluate_eligibility(job, candidate)
            decision = JobDecision(job=job, eligibility=eligibility, match=match_job(job, candidate, eligibility))
            repository.save(decision)
            return decision
        except (IngestionError, ValidationError) as error:
            raise HTTPException(422, detail={"message": str(error), "next_action": "Provide a public employer Greenhouse posting URL or pasted job description."}) from error

    @app.get("/jobs")
    def jobs():
        return [{"id": item.job.id, "title": item.job.title, "company": item.job.company, "location": item.job.location,
                 "arrangement": item.job.arrangement, "level": item.job.level, "technologies": item.job.technologies[:7],
                 "posted_at": item.job.posted_at, "discovered_at": item.job.discovered_at,
                 "source": item.job.sources[-1].provider, "score": item.match.overall, "eligibility": item.eligibility.status} for item in repository.list()]

    @app.get("/jobs/{job_id}", response_model=JobDecision)
    def job_detail(job_id: str):
        result = repository.get(job_id)
        if result is None:
            raise HTTPException(404, "Job not found")
        return result

    return app


app = create_app()
