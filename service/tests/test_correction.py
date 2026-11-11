from fastapi.testclient import TestClient

from app import main as mainmod
from app.main import app
from app.schema import SCHEMA_VERSION

client = TestClient(app)


class FakeWiki:
    def __init__(self) -> None:
        self.calls = []

    def apply_correction(self, title, field, new_value, action, actor_role):
        self.calls.append(
            {
                "title": title,
                "field": field,
                "new_value": new_value,
                "action": action,
                "actor_role": actor_role,
            }
        )
        return 17

    def reachable(self) -> bool:
        return True


def test_correction_writes_and_returns_revision(monkeypatch):
    fake = FakeWiki()
    monkeypatch.setattr(mainmod, "_wiki", fake)
    r = client.post(
        "/correction",
        json={
            "page": "Proposal:Contoh Krama",
            "field": "register",
            "from": "krama",
            "to": "ngoko",
            "action": "corrected",
            "actor_role": "author",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["written"] is True
    assert body["revision"] == 17
    assert body["schema_version"] == SCHEMA_VERSION
    assert fake.calls[0]["action"] == "corrected"
    assert fake.calls[0]["new_value"] == "ngoko"
    assert fake.calls[0]["actor_role"] == "author"


def test_reject_keeps_value(monkeypatch):
    fake = FakeWiki()
    monkeypatch.setattr(mainmod, "_wiki", fake)
    r = client.post(
        "/correction",
        json={
            "page": "Proposal:Contoh Krama",
            "field": "register",
            "from": "krama",
            "to": "ngoko",
            "action": "rejected",
            "actor_role": "author",
        },
    )
    assert r.status_code == 200
    assert fake.calls[0]["new_value"] == "krama"
    assert fake.calls[0]["action"] == "rejected"
