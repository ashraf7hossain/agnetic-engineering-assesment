# Product Requirements Document — Testify (Testimonial.to-style MVP)

## Overview

Full-stack web app for collecting, moderating, and publicly displaying customer testimonials. Inspired by [testimonial.to](https://testimonial.to). Owners create **Spaces**; customers submit text testimonials anonymously on a public collection page; owners approve/reject submissions; approved items appear on a public **Wall of Love**.

## Goals

- Let authenticated users create and manage Spaces.
- Collect text testimonials without requiring submitter accounts.
- Require explicit consent before publishing.
- Support optional 1–5 star ratings.
- Moderate submissions (pending → approved / rejected).
- Show approved testimonials on a public wall.
- Deliver smooth UX via HTMX + Tailwind CSS.

## Non-goals (MVP)

- Stripe / billing
- Embeddable widgets / iframe SDK
- Video testimonials
- Team / multi-seat management
- Custom domains
- Social import / Chrome extension

## Tech stack

| Layer | Choice |
| --- | --- |
| Backend | Django 5.x |
| Frontend | Django templates + HTMX |
| Styling | Tailwind CSS (CDN for MVP) |
| Database | PostgreSQL (Docker); SQLite fallback for local/tests |
| Auth | Django built-in auth + password reset |

## Personas

1. **Space owner** — registers, creates Spaces, shares collect link, moderates inbox, publishes wall.
2. **Customer / submitter** — opens public collect URL, writes testimonial, consents, submits (no login).

## Features

### 1. Authentication

- Register (email + password; username derived or separate)
- Login / logout
- Password reset via email (console backend in local/dev)

### 2. Spaces

- CRUD for Spaces owned by the authenticated user
- Fields: name, slug (unique), logo URL (optional), header title, custom message, `collect_ratings` (bool), theme (`light`/`dark`)
- Dashboard lists owner’s Spaces with links to inbox, collect page, wall

### 3. Public collection page (`/s/<slug>/`)

- Branded header (title, message, optional logo)
- Form: name, email, testimonial text, optional rating (if enabled), consent checkbox (required)
- Anonymous POST; CSRF protected
- On success: thank-you partial via HTMX (no full reload)

### 4. Testimonials & moderation

- Status: `pending` | `approved` | `rejected`
- New submissions start as `pending`
- Owner inbox at `/spaces/<slug>/inbox/` with HTMX approve/reject actions
- Only owner of Space may moderate

### 5. Wall of Love (`/s/<slug>/wall/`)

- Public page listing **approved** testimonials only
- Show name, text, rating (if any), relative date
- Empty state when none approved

## Data model

### Space

- `owner` → User (FK)
- `name` CharField
- `slug` SlugField unique
- `logo_url` URLField blank
- `header_title` CharField
- `message` TextField
- `collect_ratings` BooleanField default True
- `theme` CharField choices light/dark
- `created_at` DateTimeField auto_now_add

### Testimonial

- `space` → Space (FK)
- `name` CharField
- `email` EmailField
- `body` TextField
- `rating` PositiveSmallIntegerField null/blank (1–5)
- `consent` BooleanField
- `status` CharField choices pending/approved/rejected
- `created_at` DateTimeField auto_now_add

## URL map

| Path | Auth | Purpose |
| --- | --- | --- |
| `/` | public | Landing |
| `/accounts/register/` | public | Sign up |
| `/accounts/login/` | public | Login |
| `/accounts/logout/` | auth | Logout |
| `/accounts/password_reset/`… | public | Reset flow |
| `/dashboard/` | auth | List Spaces |
| `/spaces/new/` | auth | Create Space |
| `/spaces/<slug>/` | auth | Space detail / settings |
| `/spaces/<slug>/edit/` | auth | Edit Space |
| `/spaces/<slug>/inbox/` | auth | Moderate |
| `/spaces/<slug>/inbox/<id>/approve/` | auth | HTMX approve |
| `/spaces/<slug>/inbox/<id>/reject/` | auth | HTMX reject |
| `/s/<slug>/` | public | Collect form |
| `/s/<slug>/submit/` | public | HTMX submit |
| `/s/<slug>/wall/` | public | Wall of Love |

## Security

- Login required for dashboard / moderation
- Object-level ownership checks on Space mutations
- CSRF on all state-changing requests
- Consent required server-side
- Rate-limit not required for MVP; validate lengths + email format
- No PII of pending/rejected items on public wall

## UI notes

- Clean SaaS look; Tailwind utility classes
- HTMX for form submit + inbox actions (partial HTML swaps)
- Mobile-friendly layouts
- Light/dark theme on public collect/wall based on Space setting

## Testing

- Unit/integration tests for models, auth gates, submit → pending, approve → wall visibility
- Prefer Django `TestCase` / `Client`
- CI-friendly: SQLite in tests

## Milestones

1. Project scaffold + auth + base templates
2. Space CRUD + dashboard
3. Public collect + thank you (HTMX)
4. Inbox moderation (HTMX)
5. Wall of Love
6. Tests + README + Docker Compose
7. Push to GitHub

## Success criteria

- End-to-end: register → create Space → submit testimonial → approve → appear on wall
- README documents setup, env vars, and demo flow
- `docker compose up` or local venv run works
- Tests pass with `python manage.py test`
