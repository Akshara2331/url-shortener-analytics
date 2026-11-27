from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.database import get_connection, init_db
from app.utils import encode_base62, is_valid_url


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="URL Shortener with Click Analytics", lifespan=lifespan)


class ShortenRequest(BaseModel):
    url: str


@app.post("/api/shorten")
def shorten_url(payload: ShortenRequest, request: Request):
    if not is_valid_url(payload.url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Must include http:// or https://",
        )

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO urls (original_url) VALUES (?)",
            (payload.url,),
        )
        url_id = cursor.lastrowid
        short_code = encode_base62(url_id)
        conn.execute(
            "UPDATE urls SET short_code = ? WHERE id = ?",
            (short_code, url_id),
        )

    base_url = str(request.base_url).rstrip("/")
    return {
        "short_code": short_code,
        "short_url": f"{base_url}/{short_code}",
        "original_url": payload.url,
    }


@app.get("/api/analytics/{short_code}")
def get_analytics(short_code: str):
    with get_connection() as conn:
        url_row = conn.execute(
            "SELECT id, short_code, original_url, created_at FROM urls WHERE short_code = ?",
            (short_code,),
        ).fetchone()

        if not url_row:
            raise HTTPException(status_code=404, detail="Short URL not found")

        url_id = url_row["id"]

        total_clicks = conn.execute(
            "SELECT COUNT(*) AS count FROM clicks WHERE url_id = ?",
            (url_id,),
        ).fetchone()["count"]

        clicks_by_day = conn.execute(
            """
            SELECT DATE(clicked_at) AS day, COUNT(*) AS clicks
            FROM clicks
            WHERE url_id = ?
            GROUP BY DATE(clicked_at)
            ORDER BY day DESC
            LIMIT 30
            """,
            (url_id,),
        ).fetchall()

        top_referrers = conn.execute(
            """
            SELECT COALESCE(NULLIF(referrer, ''), 'Direct') AS referrer, COUNT(*) AS clicks
            FROM clicks
            WHERE url_id = ?
            GROUP BY referrer
            ORDER BY clicks DESC
            LIMIT 10
            """,
            (url_id,),
        ).fetchall()

    return {
        "short_code": url_row["short_code"],
        "original_url": url_row["original_url"],
        "created_at": url_row["created_at"],
        "total_clicks": total_clicks,
        "clicks_by_day": [dict(row) for row in clicks_by_day],
        "top_referrers": [dict(row) for row in top_referrers],
    }


@app.get("/{short_code}")
def redirect_to_url(short_code: str, request: Request):
    with get_connection() as conn:
        url_row = conn.execute(
            "SELECT id, original_url FROM urls WHERE short_code = ?",
            (short_code,),
        ).fetchone()

        if not url_row:
            raise HTTPException(status_code=404, detail="Short URL not found")

        referrer = request.headers.get("referer")
        user_agent = request.headers.get("user-agent")

        conn.execute(
            "INSERT INTO clicks (url_id, referrer, user_agent) VALUES (?, ?, ?)",
            (url_row["id"], referrer, user_agent),
        )

    return RedirectResponse(url=url_row["original_url"], status_code=302)