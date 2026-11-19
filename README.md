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

### Django unit/integration

```bash
python manage.py test
```

### Playwright e2e

```bash
npm install
npx playwright install chromium
npm run test:e2e
```

Specs live in `e2e/`. Local Playwright MCP is configured in `.cursor/mcp.json` (`@playwright/mcp`) — reload Cursor MCP after clone.

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

## Demo screenshots & recording

See [`docs/DEMO.md`](docs/DEMO.md).

- Screenshots: `docs/screenshots/*.png`
- Recording: `docs/demo/testify-demo.mp4` (also `.webm`)

Regenerate:

```bash
python manage.py runserver
python scripts/capture_demo.py
```

## Out of scope (MVP)

Stripe, video testimonials, embed widgets, team seats, custom domains.
