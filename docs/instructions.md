# Submission Instructions

> `docs/instructions.md` was empty on disk. This checklist is the submission contract for this assessment.

## Deliverable

A working **testimonial.to-style** MVP (see `docs/PRD.md`) pushed to a **public GitHub repository**.

## Required artifacts

1. **Source code** — Django + HTMX + Tailwind full-stack app matching the PRD.
2. **README.md** — how to run locally, Docker instructions, demo walkthrough, tech stack.
3. **Tests** — `python manage.py test` passes.
4. **Docker Compose** — PostgreSQL + app (or clear SQLite local path).
5. **This PRD** — kept under `docs/PRD.md`.

## Evaluation focus

- Feature completeness vs PRD (auth, spaces, collect, consent, ratings, moderation, wall)
- Code clarity and Django conventions
- HTMX used for key interactions (submit + moderate)
- Security basics (CSRF, authz on ownership)
- Runnable docs + passing tests

## Out of scope (do not block submission)

Stripe, video, embeds, teams, custom domains.

## How to submit

1. Push repository to GitHub under your account.
2. Ensure README has clone + run steps that work on a clean machine.
3. Share the repository URL as the submission.
