# EventFlow — QR-Based Event Check-In System

A lightweight event management app where attendees register and receive a unique
QR ticket, and organizers scan tickets at the door for real-time, duplicate-proof
check-in. Built with **Python (Flask)** end to end — backend, templated frontend,
and a JSON API driving a live camera scanner and dashboard.

## Features

- **Self-serve registration** — attendees sign up with name, email, and ticket
  type (General / VIP / Speaker) and instantly get a QR ticket.
- **Unique QR generation** — each ticket encodes a UUID that can't be guessed or
  reused; served as a downloadable PNG on the ticket page.
- **Live camera scanning** — the organizer's `/scan` page uses the device camera
  (via `html5-qrcode`) to decode tickets and verify entry in real time, with a
  manual code-entry fallback for damaged or unreadable codes.
- **Duplicate detection** — a ticket that's already been scanned is flagged
  immediately instead of silently re-admitting someone.
- **Live analytics dashboard** — auto-refreshing stats (registered, checked in,
  remaining) and a rolling feed of the last check-ins.
- **Full attendee roster** — a simple admin table of everyone registered and
  their current status.

## Tech stack

| Layer      | Choice                                   |
|------------|-------------------------------------------|
| Backend    | Flask, Flask-SQLAlchemy                   |
| Database   | SQLite (swap the URI for Postgres/MySQL in production) |
| QR codes   | `qrcode` (generation) + `html5-qrcode` CDN (browser-side scanning) |
| Frontend   | Server-rendered Jinja templates, vanilla JS, no build step |

## Getting started

```bash
# 1. Clone and enter the project
git clone https://github.com/<your-username>/qr-event-checkin.git
cd qr-event-checkin

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

The app starts at **http://localhost:5000**. On first run it creates a local
SQLite database at `instance/eventflow.db` automatically — no manual setup
required.

| Page | Route | Purpose |
|------|-------|---------|
| Register | `/` | Attendee sign-up form |
| Ticket | `/ticket/<ticket_code>` | Shows the generated QR ticket |
| Scanner | `/scan` | Organizer camera check-in |
| Dashboard | `/dashboard` | Live check-in stats |
| Roster | `/attendees` | Full attendee list |

> The camera scanner needs HTTPS or `localhost` to access the device camera —
> that's a browser security requirement, not an app limitation. It works out of
> the box on `localhost` and will work on a deployed host with HTTPS.

## API reference

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `POST` | `/api/checkin` | `{"code": "<ticket_code>"}` | `success` / `duplicate` / `invalid` |
| `GET` | `/api/stats` | — | `{total, checked_in, remaining, percent}` |
| `GET` | `/api/feed` | — | Last 10 check-ins, most recent first |

## Configuration

Environment variables (all optional, sensible defaults are used otherwise):

| Variable | Default | Description |
|----------|---------|--------------|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Flask session secret — **set this in production** |
| `DATABASE_URL` | local SQLite file | Any SQLAlchemy-compatible connection string |
| `EVENT_NAME` | `Global Tech Summit 2026` | Event name shown across the UI |

## Roadmap / ideas for extension

- Email the QR ticket automatically on registration (e.g. via Flask-Mail)
- Organizer login so `/scan` and `/dashboard` aren't publicly accessible
- CSV export of the attendee roster
- Per-event support (multiple concurrent events instead of one global event)

## License

MIT - use it, fork it, adapt it for your own events.
