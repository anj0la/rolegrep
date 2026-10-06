# rolegrep — Phase 1

Local single-job ingestion: public Greenhouse URL or pasted description → conservative normalization → deterministic eligibility → synthetic-fixture match → job card and decision view.

Scores are provisional test-fixture outputs, not validated predictions for the owner. Phase 2 will ingest real candidate evidence and calibrate ranking. No AI calls, GCP resources, authentication, automatic discovery, or application submission are used here.

## Run locally (PowerShell, repository root)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e "./backend[test]"
.\.venv\Scripts\python.exe -m uvicorn rolegrep.main:app --host 127.0.0.1 --port 8000 --reload
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. API documentation: http://127.0.0.1:8000/docs. Keep both servers on loopback; authentication is required before internet exposure.

## Checks

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests
cd frontend
npm test
npm run build
```

## Boundaries and limitations

- Greenhouse hosted URLs must use `https://boards.greenhouse.io/BOARD/jobs/ID` or `https://job-boards.greenhouse.io/BOARD/jobs/ID`. Embedded/custom career URLs and other providers require pasted descriptions for now. LinkedIn/Jobright authentication is never bypassed.
- Public data is fetched from the fixed Greenhouse API host, with public-address validation, redirects disabled, 10-second network-operation timeouts, and a 256 KB decoded response limit. Retained description and source snapshot are each limited to 40,000 characters, and each job retains at most five source snapshots.
- Extraction recognizes a small technology vocabulary and explicit qualification sections. Unrecognized wording stays visible in retained text. Required versus preferred experience is preserved; ambiguous wording is uncertain. Missing fields remain unknown. Greenhouse `updated_at` is never substituted for posting date.
- Work arrangement conflicts retain their competing values and evidence. No generalized conflict-resolution engine exists.
- Matching uses synthetic project evidence. Qualification coverage dominates technology preferences; preferred gaps do not automatically exclude jobs. Scores do not incorporate posting age. Location/arrangement restrictions are unset in the fixture; work authorization is not assessed.
- Manual jobs are analyzed even when preferences or eligibility oppose them. The result clearly distinguishes ineligibility from technology preference concerns.
- In-memory state disappears on restart. Repeated identical Greenhouse posting IDs or text hashes reuse a card and preserve first discovery time. No cloud persistence or document generation is implemented; artifact storage is deferred until needed.
- API boundaries separate extraction, eligibility, and matching; source/repository/extractor interfaces permit later adapters without requiring cloud or AI for tests.
- Do not put credentials or real candidate data into test fixtures. Phase 1 requires no `.env` or secrets.

Greenhouse integration follows the [public Job Board API documentation](https://docs.greenhouse.io/job-board.html). Only GET posting retrieval is implemented.
