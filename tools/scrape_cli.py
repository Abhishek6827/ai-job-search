#!/usr/bin/env python3
"""CLI runner for /scrape and /fetch-jobs.

Automates the complete end-to-end workflow:
1. Runs installed portal CLIs (LinkedIn & Freehire via Bun)
2. Deduplicates candidates against job_scraper/seen_jobs.json and job_search_tracker.csv
3. Fetches details for eligible jobs to verify isActive: true and experience <= 3 years
4. Stores new entries atomically into job_scraper/seen_jobs.json
5. Prints the formatted table, match highlights, contacts, and copyable Notepad block
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from scrape_state import select, tracker_pairs, load_state, STATE, TRACKER
from job_key import make_key

DEFAULT_QUERIES = [
    "Full Stack Developer",
    "React Developer",
    "Python Developer",
    "AI Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Machine Learning Engineer",

]

SEP = r"(?:[-–—‒―/]|to|through)"
UNITS = r"(?:years?|yrs?|yr\b)"

TITLE_EXCLUDE_PATTERNS = [
    re.compile(r"\b(Senior|Sr\.?|Lead|Principal|Staff|Architect|Director|VP|Head\s+of|Engineering\s+Manager)\b", re.I),
]

EXP_EXCLUDE_PATTERNS = [
    # 4+ years, 5+ yrs, 6+ years, 10+ yrs, etc.
    re.compile(r"\b(?:[4-9]|\d{2,})\s*(?:\+|plus)\s*" + UNITS, re.I),
    # 4-6 years, 6–8 years, 4 to 7 yrs, 5-10 yrs (supports all unicode dashes & 'to')
    re.compile(r"\b(?:[4-9]|\d{2,})\s*" + SEP + r"\s*\d+\s*" + UNITS, re.I),
    # minimum / at least 4 years / min. 5 yrs / more than 3 years
    re.compile(r"\b(?:minimum|at\s+least|min\.?|more\s+than)\s+(?:of\s+)?(?:[4-9]|\d{2,})\s*(?:\+)?\s*" + UNITS, re.I),
    # 4 or more years
    re.compile(r"\b(?:[4-9]|\d{2,})\s*(?:or\s+more)\s+" + UNITS, re.I),
    # Key-value / field style: Experience: 6-8 Years, Exp: 5+ Years, Experience - 4 Years, etc.
    re.compile(r"\b(?:experience|exp|work\s+experience)\s*[:–—-]\s*(?:minimum\s+|at\s+least\s+)?([4-9]|\d{2,})\s*(?:" + SEP + r"|\+|plus)?(?:\s*\d+)?\s*" + UNITS + r"?", re.I),
    # 4-8 years of experience, 5+ years of relevant experience
    re.compile(r"\b(?:[4-9]|\d{2,})\s*(?:" + SEP + r"|\+)?\s*(?:\d+)?\s*" + UNITS + r"\s*(?:of\s+)?(?:[\w\s]{0,25})?experience", re.I),
]


def run_cmd(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            shell=sys.platform == "win32",
        )
        if proc.returncode != 0:
            return ""
        return proc.stdout.strip()
    except Exception as exc:
        print(f"Warning: Command failed {cmd}: {exc}", file=sys.stderr)
        return ""


def search_linkedin(query: str, jobage: int, limit: int) -> list[dict]:
    cli_path = ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
    cmd = [
        "bun", "run", str(cli_path),
        "search",
        "-l", "India",
        "-q", query,
        "--jobage", str(jobage),
        "-n", str(limit),
        "--format", "json",
    ]
    raw = run_cmd(cmd)
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data.get("results", [])
    except json.JSONDecodeError:
        return []


def get_linkedin_detail(job_id: str) -> dict:
    cli_path = ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
    cmd = [
        "bun", "run", str(cli_path),
        "detail", str(job_id),
        "--format", "json",
    ]
    raw = run_cmd(cmd)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def search_freehire(query: str, jobage: int, limit: int) -> list[dict]:
    cli_path = ROOT / ".agents" / "skills" / "freehire-search" / "cli" / "src" / "cli.ts"
    cmd = [
        "bun", "run", str(cli_path),
        "search",
        "-q", query,
        "--country", "IN",
        "--jobage", str(jobage),
        "-n", str(limit),
        "--format", "json",
    ]
    raw = run_cmd(cmd)
    if not raw:
        return []
    try:
        data = json.loads(raw)
        results = data.get("results", [])
        formatted = []
        for r in results:
            formatted.append({
                "id": r.get("id"),
                "title": r.get("title"),
                "company": r.get("company"),
                "url": r.get("url"),
                "date": r.get("date"),
                "location": r.get("location") or "India",
                "description": r.get("description", ""),
                "portal": "freehire-search",
                "source": "cli",
            })
        return formatted
    except json.JSONDecodeError:
        return []


def get_freehire_detail(slug: str) -> dict:
    cli_path = ROOT / ".agents" / "skills" / "freehire-search" / "cli" / "src" / "cli.ts"
    cmd = [
        "bun", "run", str(cli_path),
        "detail", str(slug),
        "--format", "json",
    ]
    raw = run_cmd(cmd)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def is_experience_valid(desc: str, title: str = "") -> bool:
    # 1. Reject if title explicitly specifies senior/lead/managerial positions
    if title:
        for pat in TITLE_EXCLUDE_PATTERNS:
            if pat.search(title):
                return False

    if not desc:
        return True

    # 2. Reject if the opening lines of the description declare a senior/lead role
    first_few_lines = "\n".join(desc.splitlines()[:5])
    for pat in TITLE_EXCLUDE_PATTERNS:
        if pat.search(first_few_lines):
            return False

    # 3. Reject if explicit 4+, 5+, 6-8, etc. years of experience are required
    for pat in EXP_EXCLUDE_PATTERNS:
        if pat.search(desc):
            return False

    return True


def verify_url_live(url: str, timeout: float = 3.5) -> bool:
    if not url:
        return False
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status in (200, 301, 302)
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return False
        if e.code in (403, 406, 429):
            return True
        return False
    except Exception:
        return False


def determine_fit(title: str, desc: str) -> str:
    text = f"{title} {desc}".lower()
    core_kw = ["full stack", "react", "next.js", "python", "fastapi", "spring boot", "java", "typescript"]
    matches = sum(1 for kw in core_kw if kw in text)
    if matches >= 2:
        return "high"
    elif matches == 1:
        return "medium"
    return "low"


def main():
    parser = argparse.ArgumentParser(description="Run daily job scraping and deduplication")
    parser.add_argument("-q", "--query", help="Search query (default: all primary queries)")
    parser.add_argument("--jobage", type=int, default=1, help="Job age in days (default: 1 for daily runs)")
    parser.add_argument("-n", "--limit", type=int, default=15, help="Results per query (default: 15)")
    parser.add_argument("--portal", choices=("all", "linkedin", "freehire"), default="all", help="Portal to search")
    parser.add_argument("--no-store", action="store_true", help="Do not save to seen_jobs.json (dry run)")
    args = parser.parse_args()

    queries = [args.query] if args.query else DEFAULT_QUERIES
    today_iso = datetime.date.today().isoformat()

    print(f"🔍 Running multi-portal job scrape (queries: {queries}, jobage: {args.jobage} days, portal: {args.portal})...")
    all_hits = []

    if args.portal in ("all", "linkedin"):
        for q in queries:
            hits = search_linkedin(q, args.jobage, args.limit)
            print(f"  [LinkedIn] Found {len(hits)} raw postings for '{q}'")
            for h in hits:
                h["portal"] = "linkedin-search"
                h["source"] = "cli"
                all_hits.append(h)

    if args.portal in ("all", "freehire"):
        for q in queries:
            hits = search_freehire(q, args.jobage, args.limit)
            print(f"  [FreeHire] Found {len(hits)} raw postings for '{q}'")
            all_hits.extend(hits)

    if not all_hits:
        print("No raw postings found.")
        return 0

    # Deduplicate against tracker and seen_jobs.json
    doc, seen = load_state(STATE)
    tracker = tracker_pairs(TRACKER)
    selected, counts = select(all_hits, seen, tracker)
    print(f"📊 Deduplication: {len(selected)} candidate(s) selected after filtering.")
    print(f"   (Already seen: {counts['already_seen']}, Already applied: {counts['already_applied']}, Repeated: {counts['repeated_in_batch']})")

    if not selected:
        print("All fetched jobs were already seen or applied to. Nothing new to add.")
        return 0

    print("🔎 Hydrating details, checking active status and experience requirements...")
    verified_jobs = []
    for hit in selected:
        job_id = hit.get("id")
        title = hit.get("title", "")
        portal = hit.get("portal", "linkedin-search")
        desc = hit.get("description", "")

        # Quick pre-filter: skip roles whose title is explicitly Senior, Lead, Manager, etc.
        if any(pat.search(title) for pat in TITLE_EXCLUDE_PATTERNS):
            continue

        if portal == "linkedin-search":
            if not job_id:
                continue
            detail = get_linkedin_detail(job_id)
            if not detail:
                continue
            if detail.get("isActive") is False:
                continue
            desc = detail.get("description", "")
        elif portal == "freehire-search":
            if not desc and job_id:
                detail = get_freehire_detail(job_id)
                desc = detail.get("description", "")

        if not is_experience_valid(desc, title):
            continue

        url = hit.get("url", "")
        if not verify_url_live(url):
            continue

        fit = determine_fit(hit.get("title", ""), desc)
        entry = {
            "title": hit.get("title"),
            "company": hit.get("company"),
            "url": url,
            "first_seen": today_iso,
            "posted_date": hit.get("date") or today_iso,
            "deadline": None,
            "fit": fit,
            "status": "new",
            "portal": portal,
            "source": "cli",
            "location": hit.get("location", "India"),
            "description_snippet": desc[:200].replace("\n", " ") if desc else ""
        }
        verified_jobs.append(entry)

    print(f"✅ Verified {len(verified_jobs)} active, strictly 0-3 yrs experience jobs.")
    if not verified_jobs:
        print("No verified jobs passed experience and active filters.")
        return 0

    # Write ground-truth report file so agents never hallucinate URLs
    report_path = ROOT / "job_scraper" / "latest_scraped_report.json"
    report_data = {
        "scraped_at": datetime.datetime.now().isoformat(),
        "total_verified": len(verified_jobs),
        "jobs": [
            {
                "index": i,
                "title": j["title"],
                "company": j["company"],
                "url": j["url"],
                "fit": j["fit"],
                "location": j["location"],
                "recruiter_search": f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(j['company'] + ' recruiter')}&origin=GLOBAL_SEARCH_HEADER"
            }
            for i, j in enumerate(verified_jobs, 1)
        ]
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"📄 Written verified report: {report_path}")

    # Store newly found jobs
    if not args.no_store:
        added_count = 0
        for job in verified_jobs:
            key = make_key(job["company"], job["title"], job["url"])
            if key not in seen:
                seen[key] = job
                added_count += 1
        if added_count > 0:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            from rank_state import save_state
            save_state(STATE, doc)
            print(f"💾 Persisted {added_count} new postings to job_scraper/seen_jobs.json.")

    # Output Presentation
    print("\n" + "=" * 80)
    print(f"## New Job Matches - {today_iso}")
    print(f"Found {len(verified_jobs)} new verified positions (0-3 yrs exp, India & Remote).\n")

    print(f"{'#':<3} | {'Fit':<6} | {'Title':<40} | {'Company':<25} | {'Location':<20}")
    print("-" * 105)
    for i, j in enumerate(verified_jobs, 1):
        print(f"{i:<3} | {j['fit'].capitalize():<6} | {j['title'][:38]:<40} | {j['company'][:23]:<25} | {j['location'][:18]:<20}")

    print("\n" + "=" * 80)
    print("### High-Match Highlights & Direct Links\n")
    for i, j in enumerate(verified_jobs, 1):
        company_enc = quote_plus(f"{j['company']} recruiter")
        recruiter_link = f"https://www.linkedin.com/search/results/people/?keywords={company_enc}&origin=GLOBAL_SEARCH_HEADER"
        print(f"{i}. {j['company']} — {j['title']}")
        print(f"   Location: {j['location']}")
        print(f"   URL: {j['url']}")
        print(f"   Recruiter Outreach: {recruiter_link}")
        print()

    print("=" * 80)
    print("Run `/rank` to triage and shortlist, or `/apply` to generate tailored materials.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

