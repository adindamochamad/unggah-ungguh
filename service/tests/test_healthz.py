from fastapi.testclient import TestClient

from app.main import app
from app.schema import SCHEMA_VERSION

client = TestClient(app)


def test_healthz_schema_pin(monkeypatch):
    from app import main as mainmod

    class FakeWiki:
        def reachable(self) -> bool:
            return True

    monkeypatch.setattr(mainmod, "_wiki", FakeWiki())
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["schema"] == SCHEMA_VERSION
    assert body["mw_reachable"] is True
