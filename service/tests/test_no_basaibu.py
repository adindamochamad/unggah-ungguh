from __future__ import annotations

from pathlib import Path

import pytest

from app.wiki.client import WikiClient, assert_url_allowed, is_forbidden_host

def _repo_root() -> Path:
    for candidate in (Path(__file__).resolve().parents[2], Path("/workspace")):
        if (candidate / "service").is_dir() and (candidate / "mediawiki").is_dir():
            return candidate
    return Path(__file__).resolve().parents[2]


REPO = _repo_root()


@pytest.mark.parametrize(
    "url",
    [
        "https://basaibu.org",
        "http://wiki.basaibu.example",
        "https://basajawawiki.org",
        "http://basa-wiki.net",
    ],
)
def test_forbidden_hosts_rejected(url: str):
    assert is_forbidden_host(url)
    with pytest.raises(RuntimeError, match="forbidden host"):
        assert_url_allowed(url)
    with pytest.raises(RuntimeError, match="forbidden host"):
        WikiClient(base_url=url)


def test_local_hosts_allowed():
    assert not is_forbidden_host("http://mediawiki")
    assert not is_forbidden_host("http://localhost:8080")
    assert_url_allowed("http://127.0.0.1:8080")


def test_repo_service_code_has_no_basaibu_urls():
    roots = [REPO / "service", REPO / "mediawiki"]
    offenders = []
    for root in roots:
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".php", ".js", ".yml", ".yaml", ".json", ".sh"}:
                continue
            if "test_no_basaibu" in path.name:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            lower = text.lower()
            if "basaibu" in lower and "http" in lower:
                for line in text.splitlines():
                    lowered_line = line.lower()
                    if "basaibu" in lowered_line and ("http://" in lowered_line or "https://" in lowered_line):
                        offenders.append(f"{path}:{line.strip()}")
    assert offenders == []
