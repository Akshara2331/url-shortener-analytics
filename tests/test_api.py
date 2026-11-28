import pytest
from fastapi.testclient import TestClient

from app import database, main


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr(main, "get_connection", lambda: database.get_connection(test_db))
    monkeypatch.setattr(main, "init_db", lambda: database.init_db(test_db))
    with TestClient(main.app) as c:
        yield c


def test_shorten_and_redirect_tracks_clicks(client):
    res = client.post("/api/shorten", json={"url": "https://github.com"})
    assert res.status_code == 200
    short_code = res.json()["short_code"]

    redirect_res = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_res.status_code == 302
    assert redirect_res.headers["location"] == "https://github.com"

    stats_res = client.get(f"/api/analytics/{short_code}")
    assert stats_res.status_code == 200
    data = stats_res.json()
    assert data["total_clicks"] == 1
    assert data["original_url"] == "https://github.com"


def test_invalid_url_returns_400(client):
    res = client.post("/api/shorten", json={"url": "not-a-valid-url"})
    assert res.status_code == 400


def test_missing_short_code_returns_404(client):
    res = client.get("/api/analytics/doesnotexist")
    assert res.status_code == 404