---
description: Discover, deduplicate, verify (0-3 yrs exp, India & Remote), and present fresh tech jobs for Abhishek Tiwari.
---

# /scrape - Find and Deduplicate Fresh Tech Jobs

Discover fresh postings matching Abhishek Tiwari's profile using installed portal CLIs, deduplicate against previously seen jobs and `job_search_tracker.csv`, verify live active status and experience requirements, store newly found postings in `job_scraper/seen_jobs.json`, and present curated results with referral contacts.

---

## Candidate Profile Constraints (Strict Invariants)
- **Candidate:** Abhishek Tiwari
- **Location:** Lucknow, India (Domestic relocation OK to Delhi-NCR, Bengaluru, Pune, Hyderabad, Mumbai; International: REMOTE ONLY).
- **Experience:** 2+ years professional experience (Strictly <= 3 years; entry to mid-level only. Reject 4+, 5+ years).
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
*(Use `--jobage 1` for daily fresh runs, `--jobage 7` for weekly runs).*

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
1. Fetch full details via:
   ```bash
   bun run .agents/skills/linkedin-search/cli/src/cli.ts detail <id> --format json
   ```
2. Verify `isActive: true`. If `false`, mark status as `expired` so ghost postings are discarded.
3. Verify Experience: Read the full description body. Exclude jobs requiring 4+, 5+, or senior 6+ years. Retain strictly <= 3 years (0-2 yrs, 1-3 yrs, 2-4 yrs SDE1).
4. Assign Fit:
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

