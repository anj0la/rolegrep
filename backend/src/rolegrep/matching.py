from .models import CandidateProfile, EligibilityResult, Job, MatchResult


def match_job(job: Job, candidate: CandidateProfile, eligibility: EligibilityResult) -> MatchResult:
    core = job.required_skills or [skill for skill in job.technologies if skill not in job.preferred_skills]
    strong, partial, gaps = [], [], []
    points = {"strong": 1.0, "moderate": .65, "weak": .25}
    coverage = 0.0
    for skill in core:
        evidence = candidate.skills.get(skill)
        if evidence:
            coverage += points[evidence.strength]
            (strong if evidence.strength == "strong" else partial).append(f"{skill}: {evidence.strength} evidence — {evidence.source}")
        else:
            gaps.append(f"{skill}: no fixture evidence found")
    for skill in job.preferred_skills:
        if skill not in candidate.skills:
            gaps.append(f"Preferred {skill}: no fixture evidence found")
    gaps.extend("Preferred experience: " + req.wording for req in job.experience if req.kind == "preferred")
    concerns = [f"Technology preference conflict: {skill}" for skill in job.technologies if skill in candidate.avoided_technologies]
    personal = max(0, 70 - 20 * len(concerns))
    qualification = max(0, min(100, round(100 * coverage / len(core)) + (eligibility.experience_adjustment if coverage else 0))) if core else None
    overall = min(qualification, round(.9 * qualification + .1 * personal)) if qualification is not None else None
    if eligibility.status == "ineligible":
        concerns.append("Configured eligibility rules reject this role, regardless of skill score.")
    return MatchResult(overall=overall, qualification=qualification, personal=personal, candidate_version=candidate.version,
                       strong=strong, partial=partial, gaps=gaps, concerns=concerns,
                       explanation="Provisional synthetic fixture score: 90% demonstrated technology coverage (including experience adjustment), 10% technology preference fit, capped at qualification fit. Not a validated ranking algorithm. No score when technologies cannot be identified.")
