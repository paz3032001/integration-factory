# Integration Factory

Agentic pipeline that turns a vendor's OpenAPI spec into a tested Cortex XSOAR integration draft,
delivered as a pull request for human review.

**Principle:** the LLM proposes; code constrains, verifies and decides.

## Graph

parse_docs → design_commands → map_schema → build_fixtures → write_tests → write_code
→ validate → classify_failure (loop back or stop) → open_pr

## Setup

```bash
uv sync --all-extras
cp .env.example .env   # add your ANTHROPIC_API_KEY
uv run pytest
```
