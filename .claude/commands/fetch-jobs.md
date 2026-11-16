---
description: Fetch and curate latest verified tech jobs (0-3 yrs exp, India & Remote) for Abhishek Tiwari across direct company career sites and active openings.
---

# /fetch-jobs - Daily Tech Job Fetch & Curation

Execute the `/fetch-jobs` workflow leveraging all project skills, portal CLIs, and deduplication engines to discover, verify, and present fresh job opportunities.

---

## Candidate Profile Constraints (Strict Invariants)
- **Candidate:** Abhishek Tiwari
- **Location:** Lucknow, India (Open to remote global/India, relocation to Bangalore/NCR/Hyderabad/Pune; International: REMOTE ONLY).
- **Experience:** 2+ years professional experience (Strictly <= 3 years; entry to mid-level only. Reject 4+, 5+ years).
- **Role Seniority Invariant:** Absolute ban on Senior, Lead, Principal, Staff, Architect, or Director positions. Both title and the opening lines of the description must be screened.
- **Mass IT Consultancy Lateral Invariant:** Hard reject generic lateral technical postings from mass IT consultancies (`Infosys`, `TCS`, `Wipro`, `Cognizant`, `Birlasoft`, `HCLTech`, `Tech Mahindra`, `LTIMindtree`, `Capgemini`, `Accenture`) because their lateral requisition codes (e.g. `INFSYS-EXTERNAL-XXXXXX`) hide 5-9+ years requirements on internal portals while omitting them on LinkedIn. Retain ONLY if explicitly marked as intern, refresher, trainee, 0-1, or 0-2 yrs.
- **Domain Hygiene & Anti-Ghost-Job Invariant:**
  - Absolute ban on secondary content-farm scrapers (`jobleads.com`, `devglobaljobs.com`, `qajobsboard.com`, `jooble.org`, `talent.com`, `adzuna.com`, `neuvoo.com`, `shine.com`). Only allow direct LinkedIn, verified corporate ATS (`greenhouse.io`, `lever.co`, `ashbyhq.com`, `myworkdayjobs.com`), and primary tech portals (`naukri.com`, `cutshort.io`, `hirist.tech`, `himalayas.app`).
  - Absolute ban on dormant/dead ATS subdomains (e.g. `crimsoniteam.freshteam.com`).
  - Immediate rejection of postings requiring obsolete tech stacks (>5 years old: React 15/16, Bootstrap 2/3/4, Python 2.7, AngularJS 1.x).
  - Strict recency: LinkedIn postings must be <= 48 hours (`--jobage 2`). Aggregator re-index dates must never be trusted without source verification.
- **Core Tech Stack:** TypeScript, React.js, Next.js, Node.js, Python, FastAPI, Java, Spring Boot, REST APIs, Microservices, PostgreSQL, MongoDB, Docker, LLMs & Agentic AI workflows.

---

## Execution Workflow (Step-by-Step)

### Step 1: Run Portal Search CLIs
Run search queries for target priorities using installed CLIs in `.agents/skills/`:

```bash
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -l "India" -q "Full Stack Developer" --jobage 1 -n 25 --format json
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -l "India" -q "Python Developer" --jobage 1 -n 25 --format json
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -l "India" -q "Backend Developer" --jobage 1 -n 25 --format json
bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "Full Stack" --country IN --jobage 1 -n 25 --format json
```
*(Also search direct company career sites on AshbyHQ and Greenhouse for early-stage tech startups in India/Remote).*

### Step 2: Deduplicate against Tracker & Seen Jobs
Combine search hits into a temporary JSON array and run:
```bash
python tools/scrape_state.py candidates --results "<temporary search results.json>"
```
This automatically drops:
1. Any posting URL or (company, title) already in `job_scraper/seen_jobs.json`.
2. Any (company, role) already applied to in `job_search_tracker.csv`.
3. Any duplicates within the current batch.

### Step 3: Hydrate & Validate Candidates
For each hit in `selected`:
1. Check URL domain: Hard reject if hosted on secondary spam scrapers (`jobleads.com`, `devglobaljobs.com`, `qajobsboard.com`, `shine.com`, etc.) or dormant unmaintained portals (`crimsoniteam`).
2. Check URL slug: Hard reject if URL contains high experience ranges (e.g. `4-to-5-years`, `3-to-6-years`, `3-to-7-years`, `3-to-5-years`, `4-plus-years`).
3. Check title against `Senior`, `Sr.`, `Lead`, `Principal`, `Staff`, `Architect`, `Director`, `VP`, `Head of`, `Manager`. Discard immediately if matched.
4. Fetch full details via:
   ```bash
   bun run .agents/skills/linkedin-search/cli/src/cli.ts detail <id> --format json
   ```
5. Verify `isActive: true`. If `false`, mark status as `expired` so ghost postings are discarded.
6. Screen company: Hard reject generic lateral openings from mass IT consultancies (Infosys, TCS, Wipro, Birlasoft, Cognizant, etc.) unless explicitly designated with early-career word boundaries (`\bintern\b`, `\bfresher\b`, `\btrainee\b`, `\b0-1\b`, `\b0-2\b`).
7. Verify opening lines of description: Discard if the header or role states Senior / Lead.
8. Detect obsolete tech: Hard reject postings requiring obsolete legacy stacks (>5 yrs old: React 15/16, Bootstrap 2/3/4, Python 2.7, AngularJS 1.x) indicating dormant ghost jobs.
9. Verify Experience: Read the full description body. Exclude any jobs requiring >= 4 years (`4+`, `5+`, `6–8`, `min 4 years`, `Experience: 6-8 Years`), testing for all dash types (Unicode en-dash `–`, em-dash `—`, hyphen `-`, and `to`). Hard reject any range where upper bound is >= 5 (e.g. `2-5 years`, `3-5 years`, `3–6 years`, `3–7 years`) or >= 6. Retain strictly <= 3 years (0-2 yrs, 1-3 yrs, 2-4 yrs SDE1).
10. Assign Fit:
   - **High Match:** Core alignment (React, Next.js, Python, FastAPI, Java, TypeScript, AI/LLMs).
   - **Medium Match:** Adjacent tech (Node.js backend, general SDE, cloud integrations).
   - **Low Match:** Mismatched tech stack.

### Step 4: Persist Newly Found Jobs
Store all verified candidates atomically into `job_scraper/seen_jobs.json` so they are never presented again:
```bash
python tools/scrape_state.py store --results "<temporary verified jobs.json>"
```
Each entry must contain: `title`, `company`, `url`, `first_seen`, `posted_date`, `deadline`, `fit`, `status`, `portal`, `source`, `location`.

### Step 5: Present Results & Contacts
Output the report adhering to zero-AI writing style:
1. **Summary Header:** `## New Job Matches - YYYY-MM-DD (Found X new positions)`
2. **Markdown Table:**
   `| # | Fit | Title | Company | Location | Deadline | URL |`
3. **High-Match Highlights:** 2-3 concise bullets per high-fit job covering profile alignment, key requirements, and verification signals.
4. **Referral Outreach Links:**
   - Recruiter/TA LinkedIn search link
   - Role peer LinkedIn search link
5. **1-Click Copyable Block:** Dedicated markdown code block formatted for Notepad.
6. **Next Actions:** Offer `/rank` for multi-dimensional triage or `/apply` for tailoring resume & cover letter.
