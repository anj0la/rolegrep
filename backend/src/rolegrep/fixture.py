from .models import CandidateProfile, SkillEvidence


def test_candidate() -> CandidateProfile:
    return CandidateProfile(
        version="synthetic-backend-v1",
        skills={skill: SkillEvidence(strength=strength, source="Synthetic test project; not owner evidence")
                for skill, strength in {"Python": "strong", "FastAPI": "strong", "Docker": "moderate", "PostgreSQL": "moderate", "Git": "strong"}.items()},
        avoided_technologies=["Unity", "C#", ".NET", "Java", "Spring"],
        discovery_exclusions=["Unity", "C#", ".NET"],
        arrangement_order=["In-person", "Hybrid", "Remote"],
    )
