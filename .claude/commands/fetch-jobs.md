---
description: Fetch and curate latest verified tech jobs (0-3 yrs exp, India & Remote) for Abhishek Tiwari across direct company career sites and active openings.
---

# /fetch-jobs

Execute the `/fetch-jobs` workflow leveraging all project skills:
1. Load canonical facts from `.claude/skills/job-application-assistant/01-candidate-profile.md` and `CLAUDE.md`.
2. Apply vetoes and scoring from `.claude/skills/job-application-assistant/04-job-evaluation.md` (Strictly max 3 yrs exp, India/Remote only).
3. Query portals via `.agents/skills/` (freehire-search, linkedin-search) and search streams for Naukri, Indeed, and direct career sites.
4. Check deduplication against `job_search_tracker.csv`.
5. Enforce anti-AI human writing style from `.claude/skills/job-application-assistant/03-writing-style.md`.
6. Output curated Tier 1 (direct startup career pages) and Tier 2 (fresh verified openings).
7. Zero local filesystem dumps (no scratch scripts, no application folders).
8. Present a one-click copyable markdown block for Notepad.
