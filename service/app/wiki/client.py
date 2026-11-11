"""MediaWiki api.php client. Local bot password only.

Every wiki write carries an edit summary naming the actor role and schema version.
No request is allowed to a basaibu or basa*wiki host.
"""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

import httpx

from app.schema import SCHEMA_VERSION, today_iso

FORBIDDEN_HOST = re.compile(
    r"(^|\.)basaibu([.-]|$)|basa[a-z0-9-]*wiki",
    re.IGNORECASE,
)

UULABELS_RE = re.compile(r"\{\{\s*UULabels\b(?P<body>[\s\S]*?)\}\}", re.IGNORECASE)


def is_forbidden_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    if "basaibu" in host:
        return True
    if re.search(r"basa[a-z0-9-]*wiki", host):
        return True
    return False


def assert_url_allowed(url: str) -> None:
    if is_forbidden_host(url):
        raise RuntimeError(f"refusing network call to forbidden host: {url}")


class WikiClient:
    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.base_url = (base_url or os.environ.get("MW_URL") or "http://mediawiki").rstrip("/")
        assert_url_allowed(self.base_url)
        self.username = username or os.environ.get("MW_BOT_USER") or "uu-bot"
        self.password = password or os.environ.get("MW_BOT_PASS") or "UuBotPass1!"
        self._client = httpx.Client(base_url=self.base_url, timeout=20.0, follow_redirects=True)
        self._logged_in = False

    def close(self) -> None:
        self._client.close()

    def _api(self, method: str, **params):
        assert_url_allowed(str(self._client.base_url))
        params.setdefault("format", "json")
        if method == "GET":
            r = self._client.get("/api.php", params=params)
        else:
            r = self._client.post("/api.php", data=params)
        r.raise_for_status()
        return r.json()

    def reachable(self) -> bool:
        try:
            assert_url_allowed(self.base_url)
            data = self._api("GET", action="query", meta="siteinfo", siprop="general")
            return "query" in data
        except Exception:
            return False

    def login(self) -> None:
        if self._logged_in:
            return
        tok = self._api("GET", action="query", meta="tokens", type="login")
        login_token = tok["query"]["tokens"]["logintoken"]
        result = self._api(
            "POST",
            action="clientlogin",
            username=self.username,
            password=self.password,
            logintoken=login_token,
            loginreturnurl=self.base_url + "/",
        )
        status = (result.get("clientlogin") or {}).get("status")
        if status != "PASS":
            # Fall back to action=login for bot-style accounts.
            tok = self._api("GET", action="query", meta="tokens", type="login")
            login_token = tok["query"]["tokens"]["logintoken"]
            result = self._api(
                "POST",
                action="login",
                lgname=self.username,
                lgpassword=self.password,
                lgtoken=login_token,
            )
            login_ok = (result.get("login") or {}).get("result") == "Success"
            if not login_ok:
                raise RuntimeError(f"wiki login failed: {result}")
        self._logged_in = True

    def _csrf(self) -> str:
        self.login()
        tok = self._api("GET", action="query", meta="tokens", type="csrf")
        return tok["query"]["tokens"]["csrftoken"]

    def get_wikitext(self, title: str) -> str:
        data = self._api(
            "GET",
            action="query",
            prop="revisions",
            rvprop="content",
            rvslots="main",
            titles=title,
        )
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            revs = page.get("revisions") or []
            if not revs:
                return ""
            slot = revs[0].get("slots", {}).get("main", {})
            return slot.get("content") or slot.get("*") or revs[0].get("*") or revs[0].get("content") or ""
        return ""

    def edit(self, title: str, text: str, summary: str) -> int:
        token = self._csrf()
        data = self._api(
            "POST",
            action="edit",
            title=title,
            text=text,
            token=token,
            summary=summary,
            bot=1,
        )
        if "error" in data:
            raise RuntimeError(f"edit failed: {data['error']}")
        edit = data.get("edit") or {}
        if edit.get("result") != "Success":
            raise RuntimeError(f"edit failed: {data}")
        return int(edit.get("newrevid") or edit.get("oldrevid") or 0)

    def write_labels(
        self,
        title: str,
        labels: dict[str, str | float | None],
        actor_role: str,
        body: str | None = None,
    ) -> int:
        existing = self.get_wikitext(title)
        page_body = body if body is not None else _strip_uulabels(existing)
        wikitext = page_body.rstrip() + "\n\n" + render_uulabels(labels) + "\n"
        summary = (
            f"UULabels {labels.get('state', 'machine')} by {actor_role}; "
            f"schema {SCHEMA_VERSION}"
        )
        return self.edit(title, wikitext, summary)

    def apply_correction(
        self,
        title: str,
        field: str,
        new_value: str,
        action: str,
        actor_role: str,
    ) -> int:
        existing = self.get_wikitext(title)
        labels = parse_uulabels(existing) or {}
        labels[field] = new_value
        state = {
            "confirmed": "author-confirmed",
            "corrected": "author-corrected",
            "rejected": "author-rejected",
        }[action]
        labels["state"] = state
        labels["confidence"] = None
        labels["schema"] = SCHEMA_VERSION
        labels["labelled"] = today_iso()
        page_body = _strip_uulabels(existing)
        wikitext = page_body.rstrip() + "\n\n" + render_uulabels(labels) + "\n"
        summary = (
            f"UULabels {action} by {actor_role} on {field}; schema {SCHEMA_VERSION}"
        )
        return self.edit(title, wikitext, summary)


def render_uulabels(labels: dict[str, str | float | None]) -> str:
    conf = labels.get("confidence")
    conf_line = f"|confidence={conf}\n" if conf not in (None, "") else ""
    return (
        "{{UULabels\n"
        f"|register={labels.get('register', '')}\n"
        f"|dialect={labels.get('dialect', '')}\n"
        f"|stance={labels.get('stance', '')}\n"
        f"|state={labels.get('state', 'machine')}\n"
        f"{conf_line}"
        f"|schema={labels.get('schema', SCHEMA_VERSION)}\n"
        f"|labelled={labels.get('labelled', today_iso())}\n"
        "}}"
    )


def parse_uulabels(wikitext: str) -> dict[str, str] | None:
    m = UULABELS_RE.search(wikitext)
    if not m:
        return None
    body = m.group("body")
    out: dict[str, str] = {}
    for line in body.splitlines():
        line = line.strip().lstrip("|")
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _strip_uulabels(wikitext: str) -> str:
    return UULABELS_RE.sub("", wikitext).rstrip()
