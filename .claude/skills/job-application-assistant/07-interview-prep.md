---
framework_version: 1.0.0
---

# Interview Preparation Guide

<!-- SETUP: STAR examples are personalized by running /setup based on your actual experience -->

## STAR Format

Structure answers as: **Situation** (context), **Task** (your responsibility), **Action** (what you did), **Result** (outcome).

Keep answers to 1-2 minutes. Be specific. End with what you learned or would do differently.

## Ready-Made STAR Examples

<!-- These are populated by /setup from your actual experience. -->

### 1. Multi-LLM SaaS Runtime Routing (Reliability / Performance)
**S:** CHINTU AI serves 500+ users across web, desktop, and Android, with LLM inference routed live across Groq, Gemini, and OpenRouter. Provider latency and failures are visible to every user, and any degradation directly erodes the product's core promise.
**T:** As founder and sole engineer, I needed to ensure reliable, low-latency responses despite three independent providers each with their own failure modes (timeouts, empty streams, rate limits).
**A:** I built a runtime router that wraps provider APIs with a uniform interface in asynchronous Python/FastAPI services backed by RabbitMQ background workers for audio transcription. Failover is sub-400 ms; I added structured schema validation and retry logic across the response pipeline, and audited usage logs to find and eliminate silent failures (empty streams, unhandled provider timeouts that previously showed as "no response" to the user).
**R:** Achieved 99.8% uptime. Eliminated silent LLM failures and cut user-facing error rates from 7.2% to under 0.4%. The platform now processes 25k+ monthly LLM inferences.
**Use for:** "Tell me about a time you built a resilient system", "How do you handle third-party API failures?", "How do you measure reliability in a distributed system?"

### 2. Webhook-Driven Payment Infrastructure (Systems Design / Ownership)
**S:** At Indian Capital and Investment (Coimbatore) Limited, a fintech investment platform, I was the sole owner of the Stripe and Zoho Payments integration end to end. The previous implementation polled a third-party gateway every 20 minutes for payment status, creating a long lag before failures were detected and reconciliation was manual and error-prone.
**T:** I needed to replace polling with a secure, real-time event pipeline and guarantee correct idempotency and reconciliation semantics across two payment providers.
**A:** I built webhook-driven event endpoints with HMAC signature verification across all routes, implemented idempotency-key handling for every mutation, and structured transaction processing so each event is processed exactly once. Entitlement sync and billing events are driven directly from the verified webhook stream.
**R:** Cut payment-failure detection lag from 20 minutes to under 3 minutes. Achieved 100% reconciliation accuracy. In a follow-up engagement at CHINTU AI, I built Razorpay credit-based billing with the same HMAC-verified, idempotent pattern from a clean start.
**Use for:** "Tell me about a payments integration you owned", "How do you handle idempotency?", "How do you secure webhook endpoints?"

### 3. Query Performance Optimization (Engineering / Metrics)
**S:** At Vasnaani Sanskaran, an early-stage software startup, I was the sole engineer for four customer-facing web applications. Three high-traffic endpoints (listings and search routes serving live product data) were responding at p95 of ~850 ms, which was noticeable to users and threatened page-load goals.
**T:** I needed to identify the latency source and bring p95 down to acceptable levels without a rewrite or a larger team, using only production-observable data.
**A:** I profiled the endpoints with production server-timing logs and found classic N+1 query patterns and missing indexes on high-cardinality filter columns. I eliminated the N+1 queries by introducing batched fetches and eager loading, and added composite indexes aligned to the actual filter orderings used by the application.
**R:** p95 response time dropped from ~850 ms to ~550 ms, confirmed in production server-timing logs. This was the highest-impact optimization for the lowest engineering effort in that product line.
**Use for:** "How do you debug performance problems in production?", "How do you prioritize performance work?", "Walk me through a performance optimization you made."

### 4. Frontend Performance with Measurable Impact (Frontend / Optimization)
**S:** At Hoping Minds, the marketing-facing pages were performance-critical: they needed to rank and convert, and the existing Lighthouse mobile score was 68 with slow page loads. As the Full Stack Developer intern, I was asked to bring those pages up to standard.
**T:** I needed to rebuild performance-critical pages as React components that consume Django REST APIs, and demonstrate a measurable improvement in both Lighthouse score and load time.
**A:** I rebuilt the hotspots as React components backed by the existing Django REST APIs, introduced memoized selectors (reselect) across 12 Redux-connected components to eliminate full-tree re-renders, and verified changes with the React DevTools Profiler and Lighthouse.
**R:** Raised the Lighthouse mobile score from 68 to 94 and cut page load time by 22%. The reselect change alone produced a measurable 25% improvement in component render time under the Profiler.
**Use for:** "How do you optimize frontend performance?", "How do you measure the impact of your work?", "Tell me about a time you improved a metric by a specific amount."

## Common Tough Questions

### "Why did you leave [previous company]?"
> [PREPARE YOUR ANSWER - be honest, forward-looking, no negativity about former employer]

### "You don't have [specific skill/experience]."
> [PREPARE YOUR ANSWER - acknowledge the gap, bridge to adjacent experience, show willingness to learn]

### "Where do you see yourself in 5 years?"
> [PREPARE YOUR ANSWER - show ambition aligned with the role's growth path]

### "What's your biggest weakness?"
> [PREPARE YOUR ANSWER - genuine weakness with concrete mitigation strategy]

### "Why this company specifically?"
> Customize per company. Must reference: specific projects, company values, market position, or team structure. Never give a generic answer.

## Questions You Should Ask Interviewers

### About the Role
- "What does a typical week look like in this role?"
- "What would success look like in the first 6 months?"
- "What's the biggest challenge the team is facing right now?"

### About the Team
- "How big is the team, and how do you divide work?"
- "What does the development/project lifecycle look like, from idea to production?"
- "How do you onboard new team members?"

### About Tech & Growth
- "What's your current tech stack for [relevant area]?"
- "Is there room to grow into more architectural or strategic decisions?"
- "How does the team stay current with new tools and methods?"

### About Culture (use these to prevent disappointment)
- "How would you describe the team culture?"
- "What does professional development look like here?"
- "Is there flexibility for remote/hybrid work?"
- "What's the balance between development/new projects and maintenance work?"
- "How would you describe the leadership style in this team?"
- "What do people who thrive here have in common?"

## Phone/Video Interview Tips
- Have STAR examples written out (use this file)
- Keep a glass of water nearby
- Smile when speaking (it changes your tone)
- Ask for clarification if a question is vague
- It's OK to take 5 seconds to think before answering
- End with: "Is there anything else you'd like to know about my background?"

## After the Application (Best Practice)

### Follow-Up Etiquette
- **Don't call to "stand out"** or to learn more about the role post-submission - this risks a negative impression
- If the employer specified a timeline, respect it and wait
- If no timeline was given and significant time has passed (2+ weeks), a brief call to ask about status is acceptable
- If you have genuinely new, relevant information to share, a short follow-up is fine

### Thank-You Notes
- When you receive any update (interview invitation, rejection, or status update), send a brief thank-you message
- Express appreciation for their time and the process
- Keep it short (2-3 sentences)

## Roleplay Guidelines
When the user asks for interview practice:
1. Ask which role/company to simulate
2. Start with easy warm-up questions ("Tell me about yourself")
3. Progress to role-specific technical questions
4. Include 1-2 behavioral questions using the competencies from the job posting
5. End with a tough question or curveball
6. After each answer, give brief feedback: what worked, what to sharpen
7. Suggest which STAR example would work best for each question
