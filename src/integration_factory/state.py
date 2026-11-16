"""Shared state passed between graph nodes."""
from enum import Enum

from pydantic import BaseModel, Field


class FailureType(str, Enum):
    SYNTAX = "syntax"                    # → write_code
    SCHEMA_MISMATCH = "schema_mismatch"  # → map_schema
    WRONG_DESIGN = "wrong_design"        # → design_commands
    UNKNOWN = "unknown"


class FixtureSource(str, Enum):
    DOCS = "docs"            # copied verbatim from vendor docs / OpenAPI examples
    RECORDED = "recorded"    # recorded from a real sandbox
    SYNTHETIC = "synthetic"  # invented by the LLM → must be flagged for review


class CommandSpec(BaseModel):
    name: str                       # e.g. "acme-get-alert"
    endpoint: str                   # e.g. "GET /alerts/{id}"
    arguments: list[str] = []
    outputs: list[str] = []


class FieldMapping(BaseModel):
    vendor_field: str
    target: str | None              # None == no_match
    confidence: float = Field(ge=0, le=1)
    reason: str = ""


class Fixture(BaseModel):
    endpoint: str
    response: dict
    source: FixtureSource


class ValidationResult(BaseModel):
    passed: bool
    stage: str                      # "static" | "unit" | "sandbox"
    failure_type: FailureType | None = None
    failing_tests: list[str] = []
    details: str = ""


class IntegrationState(BaseModel):
    # --- input ---
    vendor: str
    raw_docs: str

    # --- understanding ---
    api_spec: dict | None = None
    auth_spec: dict | None = None

    # --- design ---
    commands: list[CommandSpec] = []
    schema_mapping: list[FieldMapping] = []

    # --- artifacts ---
    fixtures: list[Fixture] = []
    tests: str | None = None
    code: str | None = None

    # --- loop control (decided by code, never by the LLM) ---
    attempts: list[ValidationResult] = []
    iteration: int = 0
    tokens_used: int = 0

    # --- transparency for the reviewer ---
    assumptions: list[str] = []
