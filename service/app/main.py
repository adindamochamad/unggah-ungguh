from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.labeller import label_text
from app.schema import (
    SCHEMA_VERSION,
    CorrectionRequest,
    CorrectionResponse,
    HealthzResponse,
    LabelRequest,
    LabelResponse,
    allowed_for,
    schema_document,
)
from app.wiki.client import WikiClient, assert_url_allowed

app = FastAPI(title="unggah-service", version=SCHEMA_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_wiki: WikiClient | None = None


def wiki() -> WikiClient:
    global _wiki
    if _wiki is None:
        _wiki = WikiClient()
    return _wiki


@app.get("/healthz", response_model=HealthzResponse)
def healthz() -> HealthzResponse:
    mw_url = os.environ.get("MW_URL", "http://mediawiki")
    assert_url_allowed(mw_url)
    reachable = wiki().reachable()
    return HealthzResponse(
        status="ok",
        schema=SCHEMA_VERSION,
        mw_reachable=reachable,
    )


@app.get("/schema")
def get_schema() -> dict:
    return schema_document()


@app.post("/label", response_model=LabelResponse)
def post_label(req: LabelRequest) -> LabelResponse:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")
    result = label_text(req.text)
    if req.page:
        wiki().write_labels(
            title=req.page,
            labels={
                "register": result.register,
                "dialect": result.dialect,
                "stance": result.stance,
                "state": "machine",
                "confidence": result.confidence,
                "schema": SCHEMA_VERSION,
            },
            actor_role="machine",
            body=req.text,
        )
    return result


@app.post("/correction", response_model=CorrectionResponse)
def post_correction(req: CorrectionRequest) -> CorrectionResponse:
    allowed = allowed_for(req.field)
    if req.action == "corrected" and req.to not in allowed:
        raise HTTPException(status_code=400, detail=f"invalid value {req.to} for {req.field}")
    if req.action != "corrected":
        req.to = req.from_value
    revision = wiki().apply_correction(
        title=req.page,
        field=req.field,
        new_value=req.to,
        action=req.action,
        actor_role=req.actor_role,
    )
    return CorrectionResponse(written=True, revision=revision, schema_version=SCHEMA_VERSION)
