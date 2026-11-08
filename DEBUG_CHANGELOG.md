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
