# Job Search Assistant — Product Design Context

> This file is durable product and technical context for coding agents (including Codex). It defines **what the product should do**, the architecture decisions already made, implementation constraints, and the order in which the system should be built. Treat it as the project source of truth unless the user explicitly changes a requirement.

## 1. Product Goal

Build a personal job-search assistant that turns time currently spent searching and screening jobs into time spent applying.

The product should:

1. Discover relevant entry-level jobs automatically.
2. Rank jobs based on the candidate's actual qualifications **and** preferences.
3. Explain why each job is or is not a strong match using information from the job posting and candidate evidence.
4. Recommend the best existing base resume for each job.
5. Offer resume tailoring only when it is useful.
6. Generate a cover letter when a worthwhile role requires one and the candidate requests it.
7. Send the candidate to the real application destination so the candidate can personally submit the application.
8. Track applications and outcomes with minimal manual data entry.
9. Produce useful statistics about which resumes, job types, and application strategies lead to interviews/offers.

### Core product promise

**Turn an hour of job searching into an hour of applying, without sacrificing application quality.**

The system is **not** an auto-apply bot.

---

## 2. Product Principles

### 2.1 Human-controlled applications

The candidate must personally review and submit applications. Do not design automatic job submission as part of the initial product.

### 2.2 Automate repetitive work, not judgment

The system should automate discovery, reading/summarizing postings, comparison, resume recommendation, optional document preparation, tracking, reminders, and analytics.

The candidate decides:

- whether a job is worth applying to;
- which resume/version to submit;
- whether generated tailoring is acceptable;
- whether to use a cover letter;
- the answers submitted in an application;
- the application's current outcome/status.

### 2.3 Explain recommendations

A match percentage must never be a mysterious AI number. The expanded job view must explain why the score exists and identify supporting evidence, partial matches, and gaps.

### 2.4 Use existing resumes first

The candidate already maintains multiple purpose-built base resumes. Do not generate a new resume for every job.

Always begin with:

1. identify the best base resume;
2. assess whether it is already sufficient;
3. offer tailoring only if tailoring would materially improve presentation.

### 2.5 Tailoring must remain truthful

Never invent skills, experience, accomplishments, projects, metrics, responsibilities, or qualifications.

When tailoring:

- preserve content that already works;
- change only content with a concrete reason to change;
- emphasize relevant truthful experience;
- allow the candidate to inspect what changed.

### 2.6 Evidence over flat keyword lists

Candidate capability should be inferred from resumes **and** GitHub/project evidence. A technology appearing repeatedly in meaningful projects is stronger evidence than a technology merely appearing in a Skills section.

### 2.7 Qualification fit dominates preference

Personal interest should influence ranking, but it must not turn an unqualified role into a high match.

### 2.8 Do not silently learn preferences from clicks

Application outcomes can inform analytics, but do not silently rewrite candidate preferences because the candidate passed on or clicked several jobs.

The system may later suggest a preference change for explicit confirmation.

---

## 3. Target Candidate Context

The initial product is personalized for an early-career computer science candidate.

Relevant candidate context:

- Bachelor's degree completed.
- Approximately 8 months of direct computer-science-related professional experience.
- Additional non-CS experience exists, including retail and school administrative/leadership experience, but direct role/tool fit should matter more for technical matching.
- The candidate currently maintains **8 base resumes** for different job families.
- The candidate also has tailored resume variants from previous applications.
- GitHub contains additional and unfinished projects that may demonstrate skills not represented on resumes.

The product should not assume that a resume is a complete representation of the candidate's technical ability.

---

## 4. Target Roles and Hard Eligibility Rules

### 4.1 Career level

Only surface:

- New Grad
- Entry Level
- Early Career
- equivalent junior roles

Do not surface clearly senior roles such as:

- Senior
- Staff
- Principal
- Lead roles that clearly require senior experience
- other obviously senior-level positions

### 4.2 Years of experience

Experience requirements are extremely important.

Initial preference behavior:

| Required experience | Treatment |
|---|---|
| 0 years | Positive signal |
| 1 year | Neutral / good |
| 2 years | Eligible, but negative points |
| More than 2 years | Generally exclude |

If a role says "2+ years," it can still be considered but should be penalized.

Do not fill the feed with aspirational 3–5+ year roles.

### 4.3 Education

A bachelor's degree requirement is acceptable.

Experience level and education have roughly similar importance after role/tool fit, preferred skills, and location.

---

## 5. Candidate Work Preferences

### 5.1 Highest-interest work

Strong positive preference for:

1. Programming languages
2. Compiler design / compiler engineering
3. Developer tools
4. Game-development tooling
5. Build programming
6. Game-engine programming
7. Godot-related development
8. General software developer / software engineer roles

Game-development interest is primarily on the **developer tooling / engine / build** side rather than generic game-content development.

Unreal-related roles may be considered.

### 5.2 Acceptable but lower-interest work

The candidate can and will consider:

- web development;
- frontend development;
- full-stack development;
- backend development;
- Python-focused application development;
- other general software roles supported by existing resumes.

These roles can still receive high qualification scores. They simply do not receive the same preference bonus as compiler/developer-tooling/game-engine work.

### 5.3 Positive domains

Small preference bonuses can be given to products/companies involving:

- fitness;
- sports;
- soccer;
- games;
- beauty / makeup;
- fashion / clothing;
- consumer technology;
- computers;
- phones;
- useful technology products/tools.

These domain preferences are secondary to role/tool fit.

### 5.4 Negative domains / technologies

Negative preference:

- fintech;
- Java-heavy roles;
- Spring / Spring Boot-heavy roles.

Very strong negative preference:

- C#;
- .NET;
- Unity-centric roles.

Do not target Unity roles.

Godot is preferred for game development. Unreal may be considered.

A disliked technology does not necessarily have to be implemented as a hard filter unless explicitly configured that way later, but C#/.NET/Unity should be treated as especially undesirable.

---

## 6. Location and Work Arrangement

The candidate prefers **in-person work** because relocation is desirable.

Preference ordering should generally be:

1. In-person
2. Hybrid
3. Remote

Remote roles are still acceptable and should not be excluded. Remote work has financial advantages, but given otherwise comparable jobs, the candidate would prefer the in-person opportunity.

Location/work arrangement matters **after role/tool fit and preferred skills**.

---

## 7. Candidate Evidence / Onboarding

Onboarding should be small. Avoid a giant questionnaire when information can be inferred.

### 7.1 Base resumes

The candidate uploads and labels all base resumes.

The system should extract evidence including:

- skills;
- programming languages;
- frameworks;
- tools;
- projects;
- professional experience;
- education;
- role positioning;
- domain experience.

The system must preserve each resume as a distinct base resume because different resumes intentionally target different job families.

### 7.2 GitHub

The candidate should be able to link/provide GitHub so the system can inspect technical evidence.

GitHub is important because:

- unfinished projects still demonstrate skills;
- some projects do not appear on resumes;
- repeated language/tool usage indicates what the candidate actually uses;
- project types can reveal interests such as language implementation, developer tools, game development, etc.

Do not rely solely on GitHub README Stats.

README/language statistics may be supplementary, but repository/project evidence is more useful.

GitHub stars, follower counts, and contribution streaks are not important matching signals.

### 7.3 Evidence strength

Candidate skills should not be modeled as only yes/no.

Conceptually support evidence levels such as:

- **Strong evidence** — meaningful professional/project use and/or repeated substantial use;
- **Moderate evidence** — smaller projects, unfinished projects, or repeated supporting use;
- **Weak evidence** — listed but minimally demonstrated;
- **No evidence** — requested by the job but not found in candidate evidence.

### 7.4 Explicit preferences

Ask the candidate for preferences that cannot be inferred reliably, including:

- desired work types;
- preferred technologies;
- disliked technologies;
- preferred domains;
- disliked domains;
- work arrangement preference;
- experience constraints.

### 7.5 Candidate profile review

After inference, show the candidate what the system believes about them.

The candidate must be able to correct mistakes such as:

> "You're overestimating my React experience."

The candidate profile should be editable and transparent.

---

## 8. Matching and Ranking Model — Product Behavior

Do not finalize implementation weights until technical design/testing, but preserve this priority order.

### 8.1 Priority order

1. **Role / tool fit** — most important by far.
2. **Preferred skills**.
3. **Location / work arrangement**.
4. **Experience level and education**.
5. **Personal role/domain preferences**.

### 8.2 Role/tool fit

The job should actually use technologies the candidate has demonstrated.

Evidence can come from:

- base resumes;
- tailored resumes where useful as historical evidence;
- GitHub repositories;
- projects.

Example:

A Junior Software Developer role repeatedly emphasizing Python, FastAPI, Docker, PostgreSQL, and REST APIs should score well when those technologies are strongly demonstrated.

### 8.3 Preferred skills

Distinguish between:

- required skills;
- preferred/nice-to-have skills;
- core technologies used by the role.

Missing one nice-to-have should not destroy an otherwise strong match.

### 8.4 Qualification fit vs. personal fit

Internally and/or in the expanded UI, preserve a distinction between:

- **Qualification fit** — how well the candidate can do the job based on evidence;
- **Personal fit** — how well the job aligns with what the candidate wants to work on.

The compact card can still display one overall match percentage.

Example:

- 87% Overall
- Qualification fit: Excellent
- Personal fit: Good

versus:

- 79% Overall
- Qualification fit: Moderate
- Personal fit: Exceptional

### 8.5 Explainability

When a candidate opens a job, explain the score using concrete facts.

Include concepts such as:

- strongest matching skills;
- partial matches;
- requested skills with no evidence;
- years of experience requested;
- education requirement;
- role level;
- work arrangement;
- preference alignment;
- important concerns.

Do not simply output "91% match" without reasons.

---

## 9. Job Discovery

### 9.1 Discovery strategy

Do **not** make LinkedIn or Jobright scraping a required dependency of the product. The user will continue using LinkedIn and Jobright as useful discovery surfaces, but automated discovery should primarily use public job sources that can be accessed without depending on unauthorized scraping of authenticated platforms.

Primary automated discovery channels should be:

- public ATS/job-board postings, initially investigating systems such as Greenhouse, Lever, Ashby, and SmartRecruiters;
- public company career pages / employer postings;
- public-web discovery used to find relevant postings and additional company/ATS boards;
- manual URL ingestion for jobs the user encounters on LinkedIn, Jobright, or elsewhere.

Potential later sources may include Glassdoor, ZipRecruiter, additional ATS providers, or other sources that materially improve coverage. Indeed is low priority.

### 9.2 Source-agnostic ingestion

Every discovery source must feed a common normalized job pipeline. Downstream matching, resume recommendation, tracking, and analytics must not depend on where a job was discovered.

Conceptually:

```text
Public ATS feeds ─────┐
Company career pages ┤
Public web discovery ┤──> Raw Job Candidate
Manual URL ingestion ┘            │
                                  v
                         Normalize / canonicalize
                                  │
                                  v
                         Cheap eligibility filter
                                  │
                                  v
                         Detailed match + ranking
                                  │
                                  v
                              Job Inbox
```

### 9.3 LinkedIn and Jobright

LinkedIn and Jobright remain important to the user's workflow, but treat them as **supplemental discovery channels**, not as required scraped backends.

The user must be able to paste/add a job URL encountered on either platform and send it through the same normalization, matching, resume, and tracking pipeline. A future browser extension may reduce this to an `Add to Job Search` action.

Do not implement a LinkedIn scraper or authenticated browser bot unless the user explicitly revisits this decision and the approach is compatible with platform constraints.

### 9.4 Frequency

Run automated discovery **daily**. The user does not need to review jobs daily; relevant jobs can accumulate in the inbox.

### 9.5 Discovery source vs. application destination

Keep these concepts separate. A job may be discovered through one or more channels while the canonical application destination is the employer's careers site or another application system.

If multiple sources resolve to the same underlying employer posting, the user should see one opportunity rather than duplicate cards. The exact deduplication algorithm is an implementation detail, but preserve all useful discovery-source provenance.

### 9.6 Newness

Preserve two timestamps/concepts:

- **Posted at** — when the job was posted according to available source data;
- **Discovered at** — when this product first found the job.

Posting recency is more important for prioritization. A job can still be new to the user even if it was posted several days earlier.

## 10. Job Inbox / Main Feed

The primary discovery screen should behave like an **inbox**, not an endless job database.

The purpose is fast triage.

### 10.1 Compact job card

Each collapsed card should show approximately:

- job title;
- company;
- overall match percentage;
- experience level (New Grad / Entry Level / Early Career);
- location and/or work arrangement;
- 4–7 meaningful keywords/technologies;
- posting age;
- discovery source.

Example:

```text
92%  Junior Backend Developer
     Acme · Early Career · In-person
     Python · FastAPI · Docker · PostgreSQL
     Posted 8h ago · LinkedIn
```

Do not clutter the card with the entire job description.

Exact years of experience do not need to be displayed on the collapsed card. Show them in the expanded decision view.

### 10.2 Keywords

Do not simply show the most frequent words in the posting.

Extract meaningful terms such as:

- programming languages;
- frameworks;
- infrastructure tools;
- databases;
- developer tooling;
- important domain technologies.

Avoid useless keywords such as "team," "experience," or "development."

### 10.3 Feed organization

Eventually support useful sorting/filtering such as:

- highest match;
- newest;
- role family;
- location;
- in-person/hybrid/remote;
- urgency.

---

## 11. Expanded Job Decision Screen

The expanded screen should answer:

**Should I apply to this job?**

### 11.1 Why this matches

Provide a concise explanation based on the job posting and candidate evidence.

Example concept:

> Strong alignment with your Python backend experience. The role emphasizes Python, FastAPI, REST APIs, Docker, and SQL, all of which are represented in your projects. The position targets early-career candidates and does not require senior-level system-design or leadership experience.

### 11.2 Qualification summary

Show:

- strong matches;
- partial matches;
- missing/not-found skills;
- years of experience requested;
- education requirement;
- work arrangement;
- location;
- salary if available;
- cover-letter requirement;
- application deadline if available;
- urgency/staleness.

This should save the candidate from spending ~5 minutes manually reading every posting just to determine whether it is worth applying.

---

## 12. Resume Recommendation

The candidate currently has 8 base resumes.

For each job:

1. evaluate the available base resumes;
2. recommend the best starting resume;
3. explain why;
4. assess whether tailoring is worthwhile.

### 12.1 No-tailoring case

Example behavior:

```text
Recommended: Software Developer — Backend
Resume Match: 93%

Strong coverage of Python
FastAPI experience already prominent
Docker experience already included
Relevant projects are well positioned

No tailoring recommended.
```

The ideal outcome for many jobs is to use an existing base resume unchanged.

### 12.2 Tailoring case

If the base resume is a good foundation but important relevant experience is under-emphasized, offer:

- View Base Resume
- Tailor for This Job

Do not automatically tailor every resume.

### 12.3 Tailoring behavior

When tailoring:

- preserve truthful content;
- never fabricate qualifications;
- leave strong existing bullets unchanged;
- emphasize relevant experience when justified;
- reorder relevant content when useful;
- adapt wording only where it improves alignment without changing truth.

After tailoring, support comparison between base and tailored versions.

Show a change summary, e.g.:

```text
3 changes made
- Emphasized REST API work in Project X
- Moved database project higher
- Adjusted skills emphasis
```

The candidate should not need to reread the entire resume to discover what changed.

---

## 13. Cover Letters

The candidate dislikes creating cover letters and may skip mediocre jobs that require them.

Behavior:

- If cover letter is optional: generally do not create extra work.
- If cover letter is required and the job is a weak/moderate match: clearly surface the additional application effort.
- If cover letter is required and the job is a very strong match: offer to generate one.

The candidate reviews any generated cover letter before use.

---

## 14. Candidate Actions on a Job

Keep primary actions simple.

### Pass

Candidate is not interested. Remove the job from the active inbox.

### Save

Candidate is interested but does not want to apply now. Keep it outside the new-job queue.

### Apply

Open/proceed to the real application destination.

**This does not submit the application.**

The candidate personally completes and submits it.

### Mark as Applied

After submission, the candidate marks the job as applied.

That action moves the job into the application tracker and records the relevant application context.

---

## 15. Job Staleness and Urgency

Keep **match quality** separate from **urgency**.

A 96% match should remain a 96% match even if the posting is getting old.

Use separate signals such as:

- Fresh
- Getting stale
- Apply soon
- Closing soon

### 15.1 Explicit deadlines

If a job has a known application deadline:

- prominently show it;
- warn as the deadline approaches;
- remove it from the active feed after the deadline passes.

### 15.2 No known deadline

Initial behavior can roughly treat jobs as:

- fresh when newly posted;
- aging after about a week;
- stale around two weeks.

For jobs without deadlines, approximately two weeks is a reasonable initial threshold for removing/moving them out of the active inbox.

Do not permanently erase useful historical data merely because a job becomes stale.

---

## 16. Application Tracker

The tracker is a major part of the product, not an afterthought.

The goal is to understand **what actually gets interviews**, not merely count applications.

### 16.1 Application record

Preserve at least the conceptual equivalent of:

- company;
- job title;
- application URL / employer destination;
- discovery source(s);
- job description or retained posting snapshot/data;
- job match score at application time;
- relevant match explanation/data;
- application date;
- recommended base resume;
- exact resume version submitted;
- whether the resume was tailored;
- cover-letter usage;
- application status;
- important status dates/outcomes.

### 16.2 Status lifecycle

Suggested lifecycle:

```text
Interested
   ↓
Applied
   ↓
Interviewing
   ↓
Offer / Rejected / Withdrawn / Ghosted
```

Additional stages can be represented later if useful (assessment, recruiter screen, technical interview, final interview, etc.).

### 16.3 Ghosted is not rejected

Never treat silence as a confirmed rejection in analytics.

Ghosted and Rejected must remain distinct.

### 16.4 No required email access

The candidate does **not** want email access to be required for application tracking.

The candidate will manually update important outcomes.

The system should use reminders to reduce forgotten status updates.

---

## 17. Application Aging / Follow-Up

Application aging is separate from job-posting aging.

Track **time since application**.

Initial conceptual behavior:

- shortly after applying: Waiting;
- after roughly 2–3 weeks with no recorded update: surface a reminder/warning;
- after roughly 1.5–2 months: suggest that the candidate may want to mark the application Ghosted.

Do not automatically mark an application Ghosted without candidate confirmation.

Example:

> You applied 18 days ago. Any update?
>
> Interview · Rejected · Still Waiting

If the candidate chooses Still Waiting, keep it active and check again later.

---

## 18. Analytics

Analytics are essential because raw application counts do not explain what is working.

The candidate currently has a low response/progression rate across many applications, while many employers simply ghost applicants. The product should make future outcomes measurable.

Support analysis such as:

### 18.1 Resume performance

- applications per base resume;
- interview/progression rate per base resume;
- offer rate per base resume;
- tailored vs. untailored performance.

Example:

```text
Backend Base Resume
24 applications
4 interviews
16.7% progression
```

### 18.2 Match-score performance

Example:

```text
90%+ match   → applications / responses / interviews
80–89% match → applications / responses / interviews
70–79% match → applications / responses / interviews
```

This helps determine whether the matching system is predictive.

### 18.3 Other useful dimensions

Track outcomes by:

- role family;
- experience requirement (0 / 1 / 2 years);
- source (LinkedIn / Jobright);
- work arrangement;
- tailored vs. base resume;
- cover-letter usage;
- domain/company type;
- relevant technology groups where statistically useful.

### 18.4 Ghosting metrics

Track ghosting separately from explicit rejection.

### 18.5 Productivity metric

A key product-level success metric is how many **worthwhile applications** the candidate can submit per hour.

The target experience is closer to reviewing/applying to ~17 relevant jobs in an hour rather than spending an hour searching and only applying to ~5 on a good day.

---

## 19. Initial Product Scope (v1)

The intended first meaningful version includes:

- candidate onboarding/profile;
- base-resume ingestion and labeling;
- GitHub/project evidence;
- explicit preferences and constraints;
- daily automated discovery from public ATS/company/public-web sources;
- manual URL ingestion for opportunities encountered on LinkedIn, Jobright, or elsewhere;
- entry-level eligibility filtering;
- job deduplication behavior from the user's perspective;
- compact job inbox;
- explainable match scoring;
- qualification vs. preference reasoning;
- expanded decision screen;
- base-resume recommendation;
- optional resume tailoring;
- base-vs-tailored/change review;
- optional cover-letter generation;
- manual application handoff;
- Mark as Applied workflow;
- application tracker;
- stale-job warnings;
- stale-application reminders;
- ghosted vs. rejected distinction;
- application/resume outcome analytics.

---

## 20. Explicitly Out of Scope for Initial Version

Do **not** assume v1 includes:

- automatic job application submission;
- automatic answering of employer application questions;
- required email inbox access;
- automatically marking applications rejected;
- automatically marking applications ghosted without confirmation;
- every job board on the internet;
- senior/staff/principal job discovery;
- automatic tailoring of every resume;
- Unity-focused job targeting;
- a predetermined implementation architecture simply because infrastructure already exists.

---

## 21. Technical Architecture Decisions

The following choices are now agreed for the initial implementation. Do not substitute a different stack without an explicit product/technical discussion.

| Layer | Decision |
|---|---|
| Application type | Web application |
| Frontend | React + TypeScript |
| Backend language | Python |
| API framework | FastAPI |
| Primary structured database | Google Cloud Firestore |
| File/object storage | Google Cloud Storage |
| Compute | Google Cloud Run |
| Cloud provider | GCP |
| Analytics | Python over Firestore data; do not add a warehouse for v1 |
| Offline behavior | Not offline-first; temporary offline tolerance may be added later |
| Future client | Browser extension is a possible later client, not a v1 requirement |

### 21.1 Architecture principle: optimize for one user

This is a personal tool, not a SaaS business. Optimize for:

- minimal or zero recurring infrastructure cost at the user's expected scale;
- low operational complexity;
- maintainability by one developer/user;
- straightforward debugging;
- reuse of existing GCP infrastructure where appropriate.

Do **not** introduce infrastructure such as Kubernetes, Kafka, Redis, Elasticsearch, a data warehouse, multiple microservices, or other distributed-system machinery unless a demonstrated requirement makes it necessary.

The system should have clean internal boundaries, but a modular monolith is preferable to unnecessary services for v1.

### 21.2 Web client boundary

The React/TypeScript frontend is a client of the job-search system, not the location of core business logic. Discovery, normalization, matching, candidate-profile logic, resume recommendation, tracking, and analytics belong behind the backend/service boundary.

This preserves the option to add a browser extension or another client later without duplicating core logic.

### 21.3 Firestore decision

Use Firestore as the primary structured data store for v1. PostgreSQL is not required at the expected single-user scale. Analytics that would normally benefit from SQL can initially be computed in Python over the relatively small Firestore dataset.

Do not introduce Cloud SQL merely for relational purity. Revisit PostgreSQL only if real query complexity, consistency requirements, or dataset size make Firestore materially painful.

### 21.4 File storage decision

Use Cloud Storage for actual document files and Firestore for metadata, extracted text, relationships, and analysis.

Conceptual split:

- **Firestore:** resume metadata, extracted resume text, candidate profile, jobs, retained job-description text, normalized requirements, match analysis, application records, status history, GitHub-derived profile, analytics inputs/results.
- **Cloud Storage:** source resume PDF/DOCX files, tailored resume files, generated cover-letter files, and other binary application artifacts.

Do not make local filesystem paths the authoritative source of application artifacts. Local copies are convenience/download copies only.

### 21.5 Document/version provenance

Never silently overwrite the historical artifact associated with an application. Preserve the exact resume version and cover letter (if any) used for each submitted application.

Base resumes may evolve over time, but historical applications must continue pointing to the version actually submitted. Tailored resumes should preserve their base-resume lineage.

### 21.6 Job snapshots

Retain useful job-description text and normalized posting data because external postings disappear. Applied jobs should preserve enough of the original posting and match state to support later analytics.

Passed jobs may retain substantially less data than saved/applied jobs, as long as there is enough information to prevent unwanted resurfacing and preserve necessary provenance.

---

## 22. Cost Constraints

Recurring cost is a first-class constraint. The user already has GCP/Cloud Run/Firestore, but does not want a personal job-search tool to become a meaningful monthly bill.

### 22.1 Cost priorities

At this scale, database capacity is not expected to be the primary cost risk. Pay particular attention to:

- LLM/API calls;
- job-discovery/search requests;
- unnecessary repeated parsing or analysis;
- Cloud Run invocations and long-running processes;
- storing redundant large artifacts.

### 22.2 Progressive processing

Do not send every discovered posting immediately through the most expensive AI analysis. Prefer a staged pipeline:

```text
Discovered jobs
      │
      v
Cheap deterministic filtering
(level, years, obvious role mismatch, stale/closed, etc.)
      │
      v
Candidate jobs
      │
      v
Structured extraction / matching
      │
      v
Detailed AI analysis only where useful
```

A clearly senior 5+ year Java/Spring/.NET role should be rejected cheaply before expensive analysis.

Cache/reuse analysis when the underlying candidate profile and job content have not materially changed.

---

## 23. Discovery Implementation Architecture

### 23.1 Public ATS adapters

Implement discovery as adapters behind a common interface rather than source-specific logic leaking into the rest of the application. Initial investigation should prioritize public job postings from ATS/job-board systems such as Greenhouse, Lever, Ashby, and SmartRecruiters where supported.

An adapter's responsibility should end at producing normalized/raw job candidates plus source provenance.

### 23.2 Company/board registry

It is acceptable for early versions to maintain a registry of known companies/job boards worth checking. This is not sufficient as the only discovery mechanism because the system must also discover relevant employers the user does not already know.

### 23.3 Public-web discovery

Use broader public-web discovery to find relevant early-career postings and discover new employer career/ATS boards. Search/discovery can be broad because the candidate-specific matcher performs the aggressive personalization later.

Useful broad role families include software engineer/developer, frontend, backend, developer tools, tools programmer, engine/build programmer, compiler/language roles, Python roles, and new-grad/junior variants. This list is illustrative, not exhaustive.

### 23.4 Manual URL ingestion

Manual URL ingestion is a v1 feature, not merely a fallback. Given a job URL, the system should attempt to resolve/extract the underlying posting, normalize it, run eligibility/matching, and present the same decision experience as an automatically discovered job.

This provides immediate usefulness even before automated discovery coverage is complete.

---

## 24. Implementation Order / Milestones

Do **not** begin by building a massive job crawler. Build vertical slices in this order unless the user explicitly changes priorities.

### Phase 1 — Single-job ingestion vertical slice

Goal: prove that one real job can flow through the product correctly.

Implement the path:

```text
Paste job URL
   -> extract/normalize job
   -> eligibility analysis
   -> candidate match
   -> compact job card
   -> expanded decision screen
```

The normalized job model should support, when available:

- title;
- company;
- description;
- location;
- work arrangement;
- experience level;
- years requested;
- education;
- required skills;
- preferred skills;
- technologies;
- role family;
- salary;
- deadline;
- posted date;
- canonical/application URL;
- discovery provenance.

### Phase 2 — Candidate profile and matching validation

Implement base-resume ingestion, GitHub/project evidence, explicit preferences/constraints, candidate-profile review, and explainable matching.

Where practical, validate the matcher against a sample of real jobs the user has previously considered/applied to. Prefer empirical calibration against the user's judgment over arbitrary weighting constants.

### Phase 3 — Public ATS discovery adapters

Add source adapters incrementally. All adapters must feed the same normalized ingestion pipeline built in Phase 1.

### Phase 4 — Broader company/public-web discovery

Discover additional employer boards and postings so coverage is not limited to a hand-maintained company list.

### Phase 5 — Scheduled daily discovery

Only after ingestion, matching, and source adapters are reliable should daily automated discovery be scheduled. The user's computer should not need to be running.

### Phase 6 — Resume tailoring, cover letters, tracker depth, and analytics

These features can be built incrementally once the core job/candidate data model is stable. Preserve provenance from the beginning so later analytics remain possible.

---

## 25. Deployment Model and Self-Hosting

`rolegrep` is a **single-user, self-hostable personal application**, not a centrally hosted SaaS product.

Each person who wants to run `rolegrep` is expected to operate their own deployment and infrastructure. For the supported v1 cloud deployment, that means their own GCP project/resources. The project owner is not responsible for hosting other users' data, compute, storage, discovery jobs, or AI usage.

### 25.1 One deployment = one user

Do not add centralized multi-tenancy merely so other people can use the repository. A deployment belongs to one person and contains that person's candidate profile, resumes/artifacts, job inbox, discovery state, application history, GitHub/project evidence, and analytics data.

Do not introduce organizations, shared accounts, subscriptions, billing, quotas, tenant IDs, admin consoles, or SaaS account-management infrastructure unless the user explicitly changes the product direction.

The Firestore model does not need a `users/{user_id}/...` hierarchy solely to anticipate future SaaS hosting. Prefer a clean single-user model for each independent deployment.

### 25.2 General product behavior, personal configuration

Although each deployment is single-user, the application itself should remain configurable and generally usable by another person.

Do not hardcode the owner's personal preferences into matching logic. Constraints and preferences such as target seniority, maximum years of experience, preferred technologies, avoided technologies, role interests, domains, and work-arrangement preferences belong in the Candidate Profile/configuration created through onboarding.

The repository should be reusable without requiring another user to edit source code to replace the original owner's preferences.

### 25.3 Supported v1 backend

The supported v1 deployment uses Cloud Run for backend compute, Firestore for structured data, Cloud Storage for binary artifacts, and the user's own GCP project and credentials.

Do not build a local SQLite/filesystem backend in v1 unless explicitly requested. However, keep persistence concerns separated from business logic so a local backend can be added later without rewriting matching, discovery, or application logic.

Prefer simple repository/service boundaries (for example, job/application repositories and artifact storage services) rather than scattering Firestore and Cloud Storage calls throughout domain logic. Do not create elaborate abstraction frameworks solely for hypothetical backends.

### 25.4 Possible future local mode

A future local mode may use SQLite plus the local filesystem. This is intentionally deferred. A local deployment would trade cloud convenience for zero cloud dependency: scheduled discovery would only run while the host machine is available, and multi-device access/backups would become the user's responsibility.

The architecture should not block this future option, but v1 must not pay the implementation/maintenance cost for it.

### 25.5 Secrets and environment configuration

Secrets must **never** be committed to the Git repository.

Requirements:

- `.env` must be included in `.gitignore`.
- Never commit `.env`, API keys, service-account credentials, access tokens, private keys, or equivalent secret material.
- Never place secrets in frontend bundles, Firestore documents, example configuration with real values, logs, screenshots, fixtures, or tests.
- Provide a safe `.env.example` containing variable names and non-secret placeholders only.
- Any real `.env` file retained for cloud/bootstrap use must live outside the repository in private, access-controlled storage (for example, a private Cloud Storage location) and must never be publicly readable.
- Runtime/deployment secret injection may use appropriate GCP secret/config mechanisms; deployment must never require committing secrets to source control.
- Each self-hosting user supplies and pays for their own credentials, API keys, GCP resources, and any third-party services they enable.

Treat secret handling as a hard repository rule, not an optional convention.

---

## 26. Security and Privacy Baseline

This is single-user software, so do not over-engineer enterprise identity/security. Security is still required.

At minimum:

- do not expose the app or storage buckets publicly by accident;
- keep credentials/API keys in appropriate secret/config mechanisms, never committed to source control;
- validate untrusted external job content before using it in downstream processing;
- treat resumes, candidate data, generated documents, and application history as private data;
- use least-privilege service permissions where practical;
- avoid storing secrets in Firestore documents or frontend bundles.

Do not add enterprise security infrastructure without a concrete requirement.

---

## 27. Guidance for Coding Agents

When implementing or proposing designs for this project:

1. Treat this file as the product and technical source of truth unless the user explicitly changes a requirement.
2. Use React + TypeScript for the web frontend and Python + FastAPI for backend/API work.
3. Use Firestore for primary structured data and Cloud Storage for document binaries unless a requirement is explicitly revisited.
4. Prefer a simple modular architecture suitable for one user and near-zero recurring cost.
5. Do not introduce auto-apply behavior without explicit user direction.
6. Do not broaden discovery to senior roles.
7. Do not optimize purely for number of jobs found; optimize for relevant, actionable jobs.
8. Do not make unauthorized LinkedIn/Jobright scraping a required dependency.
9. Keep discovery source adapters separate from normalization/matching logic.
10. Manual URL ingestion must use the same pipeline as automatic discovery.
11. Preserve explainability in matching decisions.
12. Keep job match and urgency as separate concepts.
13. Keep qualification fit and personal preference conceptually distinguishable.
14. Preserve source data needed for future analytics.
15. Preserve exact resume/version provenance for every application.
16. Keep Rejected and Ghosted distinct.
17. Do not require email integration for core tracking.
18. Treat resume/GitHub evidence as factual grounding; never fabricate candidate experience during tailoring.
19. Prefer cheap deterministic filtering before expensive AI analysis.
20. Avoid unnecessary infrastructure and recurring services.
21. Before changing product behavior because of a technical limitation, surface the tradeoff explicitly.
22. Follow the implementation phases; do not start with large-scale crawling before the single-job ingestion/matching vertical slice works.
23. Treat each deployment as single-user and self-hosted; do not turn the project into a centrally hosted multi-tenant SaaS.
24. Keep candidate-specific preferences in onboarding/profile configuration rather than hardcoding the owner's preferences.
25. Assume each user supplies and pays for their own GCP project, credentials, API keys, and enabled third-party services.
26. Keep persistence behind simple repository/service boundaries so a future local backend remains possible, but do not implement SQLite/local mode without a concrete request.
27. Never commit `.env` or secrets. Keep `.env` ignored, provide only `.env.example` placeholders, and keep real deployment secrets outside the repository.

---

## 28. Immediate Next Engineering Step

The next engineering work should be **Phase 1: the single-job ingestion vertical slice**.

Before substantial implementation, define the repository/project structure and the minimum domain models/interfaces required for:

- a normalized job;
- discovery/source provenance;
- candidate profile/evidence placeholders;
- eligibility result;
- match result/explanation;
- Firestore persistence boundaries;
- Cloud Storage artifact references;
- FastAPI API boundary;
- React job-card and decision-screen data contracts.

Do not attempt full automated discovery until this path works against real public job URLs.
