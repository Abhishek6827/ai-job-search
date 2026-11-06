# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

## Search Sites

Primary (your market's job boards - CLIs run into these automatically):

- **`linkedin.com/jobs`** — LinkedIn job listings (filter: India & Remote); also covered by `linkedin-search` CLI
- **`freehire.me`** — aggregator covering many countries, markets, and remote opportunities; also covered by `freehire-search` CLI

Secondary (company career pages via Google):

- Direct Google searches with `site:` filters for target companies (Stripe, Vercel, Render, Razorpay, OpenRouter, early-stage SaaS startups, etc.)

## Query Categories

Queries are grouped by priority. Combine each query with your location terms where the site supports it.

### Priority 1: Full Stack & Web Engineering

These match your strongest and most desired career direction.

```
site:linkedin.com/jobs "Full Stack Developer" Lucknow [INDIA]
site:linkedin.com/jobs "Full Stack Engineer" Bangalore [INDIA]
site:linkedin.com/jobs "Software Engineer" "[TypeScript]" Noida [INDIA]
site:linkedin.com/jobs "React Developer" "[Node.js]" Mumbai [INDIA]
site:linkedin.com/jobs "Full Stack Engineer" "[Python]" Hyderabad [INDIA]
site:freehire.me "Full Stack Developer" Lucknow [INDIA]
site:freehire.me "Full Stack Engineer" "[JavaScript]" Noida [INDIA]
site:freehire.me "Full Stack Developer" Remote [INDIA]
```

### Priority 1: AI / LLM Systems Engineering

Match your AI systems track — production-grade multi-provider LLM runtimes, agentic workflows, observability for AI features. These pull from your CHINTU AI experience and backend work.

```
site:linkedin.com/jobs "LLM Engineer" Bangalore [INDIA]
site:linkedin.com/jobs "AI Engineer" "[machine learning]" Hyderabad [INDIA]
site:linkedin.com/jobs "ML Engineer" "[prompt engineering]" Pune [INDIA]
site:linkedin.com/jobs "Large Language Model Engineer" "[Python]" Bangalore [INDIA]
site:freehire.me "LLM Engineer" Bengaluru [INDIA]
site:freehire.me "AI Engineer" "[multi-provider]" Pune [INDIA]
site:freehire.me "AI Engineer" Remote [INDIA]
```

### Priority 2: Backend / Microservices Engineering

Match your backend track — scalable services, event pipelines, payments infrastructure, observability.

```
site:linkedin.com/jobs "Backend Engineer" "[Java]" Bangalore [INDIA]
site:linkedin.com/jobs "Systems Engineer" "[microservices]" Pune [INDIA]
site:linkedin.com/jobs "Backend Engineer" "[Python]" Hyderabad [INDIA]
site:linkedin.com/jobs "Senior Software Engineer" "[cloud infrastructure]" Mumbai [INDIA]
site:freehire.me "Backend Engineer" "[Spring Boot]" Bangalore [INDIA]
site:freehire.me "Microservices Engineer" "[event-driven]" Pune [INDIA]
site:freehire.me "Backend Developer" Remote [INDIA]
```

### Priority 2: Payments / Fintech Engineering

Match your payments track — Stripe, Razorpay, Zoho, webhook architecture, HMAC verification, idempotency. Pulls directly from your Indian Capital and Investment integration and CHINTU billing work.

```
site:linkedin.com/jobs "Payment Engineer" "[Stripe]" Bangalore [INDIA]
site:linkedin.com/jobs "Fintech Engineer" "[webhook architecture]" Pune [INDIA]
site:linkedin.com/jobs "Payments Engineer" "[idempotency]" Mumbai [INDIA]
site:linkedin.com/jobs "Fintech Engineer" "[HMAC verification]" Hyderabad [INDIA]
site:freehire.me "Payment Engineer" "[SaaS billing]" Bengaluru [INDIA]
site:freehire.me "Fintech Engineer" "[payment gateway]" Pune [INDIA]
```

### Priority 3: Performance Engineering & Frontend Optimization

Match your performance optimization track — query patterns, Lighthouse scores, p95 latency, memoization, frontend builds.

```
site:linkedin.com/jobs "Performance Engineer" "[query optimization]" Bangalore [INDIA]
site:linkedin.com/jobs "Web Performance Engineer" "[Lighthouse]" Mumbai [INDIA]
site:linkedin.com/jobs "Frontend Engineer" "[React profiling]" Hyderabad [INDIA]
site:linkedin.com/jobs "Performance Engineer" "[database indexing]" Pune [INDIA]
```

### Priority 3: Adjacent Roles - Pivot Candidates

Roles closer to your current stack that signal willingness to grow; flag moderate fit, address gaps honestly.

```
site:linkedin.com/jobs "Technical Consultant" "[full-stack]" Bangalore [INDIA]
site:linkedin.com/jobs "Solutions Engineer" "[backend]" Mumbai [INDIA]
site:linkedin.com/jobs "Senior Software Engineer" "[TypeScript]" Pune [INDIA]
site:linkedin.com/jobs "DevOps Engineer" "[infrastructure as code]" Hyderabad [INDIA]
```

### Priority 4: Broader Technical / Consulting

Wider net for general technical roles that could absorb your transferable skills.

```
site:linkedin.com/jobs "Engineer" "[TypeScript developer]" Delhi [INDIA]
site:linkedin.com/jobs "Software Engineer" "[distributed systems]" Bangalore [INDIA]
site:linkedin.com/jobs "Developer" "[web applications]" Mumbai [INDIA]
```

## Location Filter

When evaluating results, verify the job location is within reasonable commute distance from your home. Define acceptable areas:

- **Lucknow and surrounding areas** — your home base
- **Delhi NCR (Gurgaon, Noida)** — regionally acceptable
- **Bangalore, Hyderabad, Pune, Mumbai** — metro acceptable with strong remote component
- **Remote** — global or India-wide remote roles

## Language Filter

Your working languages and levels are in CLAUDE.md's Languages table (English: Professional working proficiency / Fluent; Hindi: Native). When filtering scraped results, apply `04-job-evaluation.md`'s Language Gate:

- A posting requiring a language you haven't declared at all is **excluded**.
- A posting requiring a *higher level* than you declared in a language you *do* work in is **flagged, not excluded** — see `04-job-evaluation.md`'s Language Gate and the flag surfaces in `/scrape` output.
- Postings simply *written* in a language you don't work in, that don't require it on the job, are fine.

Note: both English and Hindi are listed, so most postings pass. Any posting requiring a third language (German, Danish, Japanese, etc.) without explicit declaration is excluded.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area (e.g. `/scrape [focus_area]`), select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- `/scrape AI systems` -> Priority 1 AI/LLM queries + 2-3 custom prompts/routing/observability queries
- `/scrape fintech` -> Priority 2 Payments queries + 2-3 custom webhook/idempotency/HMAC queries
- `/scrape remote` -> Priority 4 broader queries with remote filter emphasis