# URL Shortener with Click Analytics

![CI](https://github.com/Akshara2331/url-shortener-analytics/actions/workflows/ci.yml/badge.svg)

A lightweight, full-stack URL shortening service with real-time click tracking and daily analytics, built with **FastAPI**, **SQLite**, and **vanilla HTML/JavaScript**.

---

## Features

- **Collision-Free Base62 Shortening:** Encodes auto-incremented database IDs into compact Base62 (`0-9`, `a-z`, `A-Z`) short codes without random-string collision checks.
- **Accurate Click Tracking:** Redirects via **HTTP 302 (Found)** instead of 301 so browsers do not cache redirects and bypass analytics logging.
- **Click Analytics API:** Aggregates total clicks, 30-day daily click breakdowns, and top referrers using indexed SQL queries.
- **Interactive Web UI:** Built-in frontend for shortening links, one-click copying, and inspecting live click stats.
- **Automated Testing & CI:** Isolated `pytest` API test suite running automatically on every push and pull request via GitHub Actions.

---

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Database:** SQLite (normalized schema with foreign keys and indexes)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (`fetch` API)
- **Testing & CI:** Pytest, HTTPX (`TestClient`), GitHub Actions

---

## Architecture & Engineering Decisions

### Database Schema
Two normalized tables separate link storage from click events to keep redirects fast while supporting analytical aggregations:

- **`urls`**: Stores `id` (primary key), `short_code` (unique, indexed), `original_url`, and `created_at`.
- **`clicks`**: Stores `id`, `url_id` (foreign key to `urls.id`, indexed), `clicked_at`, `referrer`, and `user_agent`.

### Key Design Choices
- **Base62 Encoding:** Inserting the URL first and encoding its unique integer `id` guarantees zero collisions and predictable short-code growth.
- **HTTP 302 Redirects:** Permanent redirects (`301`) are cached aggressively by browsers, which prevents subsequent visits from hitting the server. Using `302` ensures every click is recorded accurately.
- **Isolated Test Database:** The `pytest` suite monkeypatches the database path to a temporary directory (`tmp_path`) so tests never mutate local data.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web interface (`static/index.html`) |
| `POST` | `/api/shorten` | Validates a URL and returns its generated `short_code` and `short_url` |
| `GET` | `/{short_code}` | Logs click metadata (`referrer`, `user_agent`) and redirects (`302`) to the original URL |
| `GET` | `/api/analytics/{short_code}` | Returns total clicks, daily click counts (last 30 days), and top referrers |

### Example Request (`POST /api/shorten`)
```json
{
  "url": "[https://github.com](https://github.com)"
}
```
```
url-shortener-analytics/
├── .github/workflows/
│   └── ci.yml           # GitHub Actions CI pipeline
├── app/
│   ├── main.py          # FastAPI routes & startup lifecycle
│   ├── database.py      # SQLite connection & schema initialization
│   └── utils.py         # Base62 encoder & URL validator
├── static/
│   └── index.html       # Frontend UI for shortening & analytics
├── tests/
│   └── test_api.py      # Automated API test suite
├── pytest.ini           # Pytest configuration
├── requirements.txt     # Python dependencies
└── README.md
```
