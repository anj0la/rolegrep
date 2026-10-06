from .models import CandidateProfile, EligibilityResult, Job


def evaluate_eligibility(job: Job, candidate: CandidateProfile) -> EligibilityResult:
    reasons = []
    rejected = job.level == "Senior"
    uncertain = job.level is None or not job.experience
    adjustment = 0
    eligible_minimums = []
    if rejected:
        reasons.append("Senior/Staff/Principal title is outside configured career level.")
    for requirement in job.experience:
        if requirement.kind == "preferred":
            reasons.append("Preferred experience is a gap, not an exclusion: " + requirement.wording)
        elif requirement.kind == "uncertain" or requirement.minimum is None:
            uncertain = True
            reasons.append("Review ambiguous experience: " + requirement.wording)
        elif requirement.minimum > candidate.max_required_years:
            rejected = True
            reasons.append("Required experience exceeds configured maximum: " + requirement.wording)
        else:
            eligible_minimums.append(requirement.minimum)
            reasons.append("Eligible required experience: " + requirement.wording)
    if eligible_minimums:
        maximum = max(eligible_minimums)
        adjustment = -10 if maximum == 2 else 3 if maximum == 0 else 0
    for field, allowed in [("location", candidate.allowed_locations), ("arrangement", candidate.allowed_arrangements)]:
        if allowed is not None:
            value = getattr(job, field)
            if value is None:
                uncertain = True
                reasons.append(f"Unknown {field}; review configured restriction.")
            elif value not in allowed:
                rejected = True
                reasons.append(f"{field} conflicts with configured allowed values.")
    if job.conflicts:
        uncertain = True
        reasons.append("Conflicting source fields require review.")
    if job.level is None:
        reasons.append("Career level is unknown; review posting.")
    if not job.experience:
        reasons.append("Experience requirement is unknown, not assumed zero.")
    reasons.append("Work authorization is not assessed by this slice; review the posting.")
    return EligibilityResult(status="ineligible" if rejected else "uncertain" if uncertain else "eligible", reasons=reasons, experience_adjustment=adjustment)
