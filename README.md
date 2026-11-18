# Testify

Testimonial.to-style MVP: create **Spaces**, collect text testimonials (with consent + optional ratings), moderate an inbox, and publish a public **Wall of Love**.

Built with **Django + HTMX + Tailwind CSS**. PostgreSQL via Docker Compose; SQLite by default for local/tests.

## Quick start (local / SQLite)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or: cp .env.example .env
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Docker (PostgreSQL)

```bash
docker compose up --build
```

App: http://127.0.0.1:8000/ · DB: `postgres://testify:testify@localhost:5432/testify`

## Demo walkthrough

1. Sign up → create a Space (`/spaces/new/`).
2. Open the **Collect** link (`/s/<slug>/`) in a private window.
3. Submit a testimonial (consent required).
4. Owner **Inbox** → Approve / Reject (HTMX, no full reload).
5. Open **Wall of Love** (`/s/<slug>/wall/`) — approved only.

## Tests

```bash
python manage.py test
```

## Project layout

```
accounts/     # register, login, password reset
spaces/       # Space + Testimonial models, collect, inbox, wall
templates/    # Django + HTMX partials
docs/PRD.md   # product requirements
docs/instructions.md
```

## Env vars

See `.env.example`. Leave `DATABASE_URL` empty for SQLite.

## Out of scope (MVP)

Stripe, video testimonials, embed widgets, team seats, custom domains.
