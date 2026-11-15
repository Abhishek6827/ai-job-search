# Debug Changelog & Regression Ledger

## [Bug Fix & URL Integrity] - 2026-11-06
- **Issue/Symptom:**
  - User reported Job #01 link (`https://in.linkedin.com/jobs/view/full-stack-ai-developer-platform-product-development-at-eastern-book-company-4485747653`) redirected/opened "Hello Watt — Senior Software Engineer (H/F), Paris, France" instead of Eastern Book Company (Lucknow).
  - TantranZm careers page showed GenAI Engineer requiring 3-6 years of experience, violating candidate max 3-year experience rule.
- **Root Cause:**
  - In LinkedIn URLs (`linkedin.com/jobs/view/<slug>-<job_id>`), LinkedIn's web app routing completely ignores the text slug and routes purely by the numeric job ID. The numeric ID `4485747653` belonged to Hello Watt (Paris). The genuine Eastern Book Company job ID in Lucknow is `4486366625` (`https://www.linkedin.com/jobs/view/4486366625`).
  - LinkedIn delists/redirects inactive or expired job postings (or mismatching IDs) to sponsored international listings.
  - Initial scraping regex filtered titles for experience terms, but certain jobs (e.g. TantranZm, Aventra.AI) specified 3-6 or 5+ years solely in the full job description body.
- **Files Modified / Tools Created:**
  - `tools/verify_and_filter_active_jobs.py`: Script created to verify live LinkedIn job state (`isActive: true`), validate actual experience requirements in full job descriptions (excluding >3 years), and ensure valid direct application links.
  - `job_scraper/live_verified_active_jobs.json`: Dataset containing verified active, strictly <= 3 years India / Remote jobs.
- **Architectural Invariants & Guardrails Established:**
  1. **Strict Job ID Validation:** Every job link must be verified against LinkedIn detail endpoint (`isActive: true`) before presentation to prevent dead links or unexpected redirections.
  2. **Direct Contact Fallback:** Where companies provide direct email (e.g., Eastern Book Company: `employment@ebc.co.in`), provide the direct email alongside the job link.
  3. **Full Description Experience Check:** Experience check must parse the full job description body, not just the title, ensuring candidate's <= 3 years limit is strictly respected.

## [Introspection & Source Control Cleanup] - 2026-11-06
- **Issue/Symptom:**
  - 123 files staged in git index, cluttering source control with temporary scratch scripts, test JSONs, and duplicate application files.
  - Excessive manual friction and ad-hoc script proliferation ("reinventing the wheel").
- **Root Cause:**
  - The repository already contains a full automated job search framework (`.claude/commands/`, `.claude/skills/job-scraper/`, `tools/scrape_state.py`, `tools/rank_state.py`, `cv/`).
  - Past sessions created 13 redundant one-off scripts in `tools/` (`fetch_fresh_jobs.py`, `filter_clean_jobs.py`, `verify_curated_urls.py`, etc.) and dumped 8 intermediate `.json` files instead of using the workspace's built-in pipeline.
  - A previous batch staged all changes (`git add .`) into git index.
- **Actions Taken:**
  - Unstaged all 123 files via `git restore --staged .`.
  - Identified 13 untracked temporary test scripts in `tools/` and temporary cache files in `job_scraper/` and `scratch/`.
- **Invariants Established:**
  1. **Reuse Existing Framework:** Use native workspace skills and CLI tools; do not write throwaway scratch scripts in `tools/`.
  2. **Clean Source Control:** Do not stage temporary test artifacts or intermediate JSON files into git index.

## [CLI & Command Parity: scrape & fetch-jobs] - 2026-11-08
- **Issue/Symptom:**
  - User requested that both `scrape` and `fetch-jobs` execute the complete end-to-end workflow identically across CLI and agent sessions, exactly matching Claude's original autonomous pipeline.
  - `.claude/commands/scrape.md` was missing in `.claude/commands/`, and `.claude/commands/fetch-jobs.md` was a minimal 15-line stub lacking explicit orchestration steps.
- **Root Cause:**
  - Original `/scrape` specification lived only in `.claude/skills/job-scraper/SKILL.md` rather than an explicit command file, causing command discovery drift across agent runtimes.
  - Lack of a unified standalone CLI runner that connects portal search CLIs (`.agents/skills/linkedin-search/`), `tools/scrape_state.py` deduplication, and active detail verification directly in terminal without LLM overhead.
- **Actions Taken & Invariants Established:**
  1. **Unified Command Specifications:** Created `.claude/commands/scrape.md` and updated `.claude/commands/fetch-jobs.md` with the full 5-step execution pipeline (CLI portal search -> `scrape_state.py` tracker/seen dedup -> detail verification for active status and <=3 yrs exp -> atomic storage -> formatted output).
  2. **Autonomous CLI Runner (`tools/scrape_cli.py`):** Added a lightweight zero-dependency CLI utility that glues existing portal CLIs (`linkedin-search`) with `tools/scrape_state.py` and `job_key.py`, executable directly in PowerShell via `python tools/scrape_cli.py`.
  3. **Guaranteed Zero-Duplicate Invariant:** Every run must filter against `job_search_tracker.csv` and `job_scraper/seen_jobs.json` before presenting or storing jobs.

## [Skill Alignment & Native Claude Scraper Execution] - 2026-11-09
- **Issue/Symptom:**
  - Invoking `/fetch-jobs` loaded an outdated custom skill (`C:\Users\Abhishek\.gemini\config\skills\fetch-jobs\SKILL.md`) that bypassed the repo's native Claude scraping architecture (`tools/scrape_cli.py`, `tools/scrape_state.py`, `job_scraper/seen_jobs.json`).
- **Root Cause:**
  - The custom skill contained conflicting instructions mandating zero state persistence and hardcoding a static list, failing the repo's Thin-Pointer Design (`AGENTS.md`) and Claude parity rules.
- **Actions Taken:**
  - Updated `C:\Users\Abhishek\.gemini\config\skills\fetch-jobs\SKILL.md` to directly reference and execute the canonical 5-step Claude scraping pipeline (`tools/scrape_cli.py` / `scrape_state.py`).
  - Upgraded `tools/scrape_cli.py` with multi-portal orchestration (`search_linkedin` + `search_freehire`), expanded priority search queries (`Full Stack`, `React`, `Python`, `AI Engineer`, `Backend`), and `--portal` flag support.
  - Executed full multi-portal scrape (`--jobage 7 --limit 15 --portal all`), pulling 125 raw postings across LinkedIn and FreeHire.
  - Deduplicated against `seen_jobs.json` and `job_search_tracker.csv` (21 already seen, 19 batch duplicates filtered).
  - Hydrated and verified 68 active, strictly 0-3 years experience postings across India and Remote.
  - Atomically stored all 68 newly found postings into `job_scraper/seen_jobs.json`.
- **Invariants Established:**
  1. **Strict Thin-Pointer Alignment:** Antigravity / Gemini skills must mirror `.claude/commands/` and `.claude/skills/` without drifting into static or ad-hoc workflows.
  2. **Multi-Portal Parity:** `tools/scrape_cli.py` must query both `linkedin-search` and `freehire-search` to aggregate direct company ATS and public board postings.
  3. **Stateful Scrape Guarantee:** All job scraping must read from and write to `job_scraper/seen_jobs.json` to ensure permanent deduplication.
  4. **Multi-Source Ingestion:** Scraper pipeline incorporates LinkedIn, FreeHire, direct Naukri listings (`site:naukri.com`), and Indeed (`site:in.indeed.com`) to guarantee complete market coverage across India & Remote.

## [Daily Scrape Parity & 86 Verified Jobs] - 2026-11-10
- **Workflow Run:**
  - Automated `/fetch-jobs` execution across 7 key tech query vectors ('Full Stack Developer', 'React Developer', 'Python Developer', 'AI Engineer', 'Backend Developer', 'Frontend Developer', 'Machine Learning Engineer') with 2-day recency.
- **Results & Deduplication:**
  - 175 raw postings pulled from LinkedIn, FreeHire, Naukri, and corporate ATS platforms (Greenhouse, Workday).
  - Deduplicated against `job_search_tracker.csv` and `job_scraper/seen_jobs.json` (22 already seen, 28 repeated in batch filtered).
  - 86 verified active jobs passing strictly <= 3 years experience check atomically persisted to `job_scraper/seen_jobs.json`.

## [Daily Scrape Parity & 102 Verified Jobs] - 2026-11-13
- **Workflow Run:**
  - Automated `/fetch-jobs` execution across 7 key tech query vectors with 3-day recency covering multi-portal sources (LinkedIn, FreeHire, Naukri, Lever, Workday).
- **Results & Deduplication:**
  - 175 raw postings pulled across all channels.
  - Deduplicated against `job_search_tracker.csv` and `job_scraper/seen_jobs.json` (19 already seen dropped, 13 batch duplicates filtered).
  - 102 verified active jobs passing strictly <= 3 years experience check atomically persisted to `job_scraper/seen_jobs.json`.

## [Bug Fix: Broken Job URLs & Ground-Truth Verification Engine] - 2026-11-13
- **Issue/Symptom:**
  - User reported that job links presented in chat were broken or invalid.
- **Root Cause:**
  - When `tools/scrape_cli.py` outputted a large report (102 jobs, 40+ KB), the terminal stdout was truncated by the runtime environment.
  - Because of the truncation, the model synthesized numeric job IDs in chat instead of reading the ground truth from disk. The true IDs stored in `seen_jobs.json` (e.g. Adani AI Labs `4488686737`, TravClan `4489254153`, Comviva `4490097005`) returned HTTP 200, whereas the misquoted IDs returned HTTP 404.
- **Actions Taken & Invariants Established:**
  1. **Automated Live URL Health Check:** Added `verify_url_live(url)` in `tools/scrape_cli.py` that pings each candidate URL via HTTP HEAD/GET before accepting it, dropping any 404, 410, or dead links.
  2. **Ground-Truth Report Export:** `tools/scrape_cli.py` now atomically exports `job_scraper/latest_scraped_report.json` containing the exact, validated URL and recruiter links for all verified positions.
  3. **Strict Zero-Guessing Invariant:** Updated `C:\Users\Abhishek\.gemini\config\skills\fetch-jobs\SKILL.md` requiring the agent to read `job_scraper/latest_scraped_report.json` directly from disk. Generating or hallucinating URLs from memory is strictly banned.

## [Daily Scrape Parity & 94 Verified Jobs] - 2026-11-15
- **Workflow Run:**
  - Automated `/fetch-jobs` execution across 7 key tech query vectors with 2-day recency covering multi-portal sources (LinkedIn, FreeHire, Naukri, AshbyHQ, Workday).
  - Automated live HTTP URL validation verified all accepted postings prior to storage.
- **Results & Deduplication:**
  - 175 raw postings pulled across all channels.
  - Deduplicated against `job_search_tracker.csv` and `job_scraper/seen_jobs.json` (24 already seen dropped, 13 batch duplicates filtered).
  - 94 verified active jobs passing strictly <= 3 years experience check atomically persisted to `job_scraper/seen_jobs.json` and ground-truth exported to `job_scraper/latest_scraped_report.json`.

## [Bug Fix: Experience Filter Leakage & Unicode Dash Matching] - 2026-11-15
- **Issue/Symptom:**
  - User reported that Speedioo — Full Stack Engineer (Index #3 in scraped report) slipped through the `<= 3 years` filter despite the job description stating `Senior Full Stack Engineer – Product & Platform` and `Experience: 6–8 Years`.
  - Audit revealed 11 other jobs with explicit `Senior` / `Lead` titles in `latest_scraped_report.json`.
- **Root Cause:**
  1. **Unicode Dash Mismatch:** The previous regex `\b(?:4|5|6|7|8|9|10)\s*-\s*\d+\s*(?:years?|yrs?)` only matched standard ASCII hyphen `-` (`\x2d`). In Speedioo's posting, the experience was written as `Experience: 6–8 Years` using a Unicode En-Dash `–` (`\u2013`), so the regex completely missed it.
  2. **Missing Key-Value Pattern:** Regex patterns lacked direct matching for key-value headers like `Experience: 6–8 Years` or `Exp: 5+ Years`.
  3. **No Title Seniority Guard:** `tools/scrape_cli.py` lacked a title filter for senior roles, allowing postings with `Senior`, `Lead`, `Principal`, or `Staff` in the title or opening description lines to bypass filtering.
  4. **Dangerous Whitelist Bypass:** `is_experience_valid` had a bypass `if re.search(r"\b(?:0-2|1-3|2-3|2-4)..."): continue` which allowed senior roles to pass if `1-3` was mentioned anywhere in the body.
  5. **LinkedIn Metadata Misclassification:** LinkedIn's API labeled Speedioo's seniority as `"Entry level"`, bypassing any native portal-level seniority filter.
- **Actions Taken:**
  1. Upgraded `EXP_EXCLUDE_PATTERNS` in `tools/scrape_cli.py` to match all dash variants (`[-–—‒―/]`, `to`, `through`), key-value labels (`Experience: 6-8 Years`), open-ended qualifiers (`4+`, `5+`), and minimum thresholds (`minimum 4 years`).
  2. Implemented `TITLE_EXCLUDE_PATTERNS` checking both `hit.get("title")` and the top 5 header lines of the description for `Senior`, `Sr.`, `Lead`, `Principal`, `Staff`, `Architect`, `Director`, `VP`, `Head of`, `Engineering Manager`.
  3. Removed the reckless whitelist bypass from `is_experience_valid(desc, title)`.
  4. Verified rejection of Speedioo (ID `4489874585`) via unit tests.
  5. Pruned 12 leaked senior/high-exp jobs from `job_scraper/latest_scraped_report.json` (remaining: 82 cleanly verified jobs).
- **Architectural Invariants & Guardrails Established:**
  1. **Unicode Separator Invariant:** All range-based text filters MUST match Unicode en-dash (`\u2013`), em-dash (`\u2014`), slashes, and `to`/`through` alongside standard hyphens.
  2. **Multi-Layer Seniority Filter:** Both job title and top description lines must be screened for seniority keywords; never rely solely on recruiter-supplied metadata (`seniority: Entry level`).
  3. **Strict Hard Exclusion:** Any explicit requirement of $\ge 4$ years is an immediate hard rejection, regardless of whether lower numbers appear elsewhere in description prose.
