"""Register schema v0.1.0 — single source of truth.

Provisional. The fellowship's first quarter replaces this through co-design
with Javanese writers. Every value is contestable.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SCHEMA_VERSION = "0.1.0"

REGISTER_VALUES = ("ngoko", "madya", "krama", "mixed", "undetermined")
DIALECT_VALUES = ("mataraman", "jawa-timuran", "banyumasan", "undetermined")
STANCE_VALUES = ("peer", "deferential", "assertive", "mixed", "undetermined")
LABEL_STATES = ("machine", "author-confirmed", "author-corrected", "author-rejected")
CORRECTION_ACTIONS = ("corrected", "rejected", "confirmed")
ACTOR_ROLES = ("author",)
DIMENSIONS = ("register", "dialect", "stance")

Register = Literal["ngoko", "madya", "krama", "mixed", "undetermined"]
Dialect = Literal["mataraman", "jawa-timuran", "banyumasan", "undetermined"]
Stance = Literal["peer", "deferential", "assertive", "mixed", "undetermined"]
LabelState = Literal["machine", "author-confirmed", "author-corrected", "author-rejected"]
CorrectionAction = Literal["corrected", "rejected", "confirmed"]
Dimension = Literal["register", "dialect", "stance"]


class LabelEvidence(BaseModel):
    lexicon: list[str] = Field(default_factory=list)
    lexicon_reading: dict[str, str] = Field(default_factory=dict)
    model: str = ""
    model_reading: dict[str, str] = Field(default_factory=dict)


class LabelRequest(BaseModel):
    text: str
    page: str | None = None


class LabelResponse(BaseModel):
    register: Register
    dialect: Dialect
    stance: Stance
    confidence: float = Field(ge=0.0, le=1.0)
    schema_version: str = SCHEMA_VERSION
    evidence: LabelEvidence
    agreement: bool

    @field_validator("schema_version")
    @classmethod
    def version_pin(cls, v: str) -> str:
        if v != SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
        return v


class CorrectionRequest(BaseModel):
    page: str
    field: Dimension
    from_value: str = Field(alias="from")
    to: str
    action: CorrectionAction
    actor_role: Literal["author"] = "author"

    model_config = {"populate_by_name": True}


class CorrectionResponse(BaseModel):
    written: bool
    revision: int
    schema_version: str = SCHEMA_VERSION


class HealthzResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)
    status: str
    schema_version: str = Field(default=SCHEMA_VERSION, alias="schema")
    mw_reachable: bool


class SchemaDocument(BaseModel):
    schema_version: str = SCHEMA_VERSION
    properties: dict[str, Any]


def schema_document() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "note": (
            "Provisional. Stance in this spike is derived only from register "
            "plus address forms."
        ),
        "properties": {
            "Has register": {
                "datatype": "Text",
                "allowed": list(REGISTER_VALUES),
            },
            "Has dialect": {
                "datatype": "Text",
                "allowed": list(DIALECT_VALUES),
            },
            "Has stance": {
                "datatype": "Text",
                "allowed": list(STANCE_VALUES),
            },
            "Has label state": {
                "datatype": "Text",
                "allowed": list(LABEL_STATES),
            },
            "Has label confidence": {
                "datatype": "Number",
                "allowed": "0.0–1.0, machine labels only",
            },
            "Has schema version": {
                "datatype": "Text",
                "allowed": [SCHEMA_VERSION],
            },
            "Has labelled at": {
                "datatype": "Date",
                "allowed": "ISO 8601",
            },
        },
    }


def allowed_for(field: str) -> tuple[str, ...]:
    return {
        "register": REGISTER_VALUES,
        "dialect": DIALECT_VALUES,
        "stance": STANCE_VALUES,
    }[field]


def today_iso() -> str:
    return date.today().isoformat()
