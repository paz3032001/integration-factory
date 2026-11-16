# CLAUDE.md: Integration Factory

## What this project is
An agentic pipeline that scales delivery of Cortex XSOAR/XSIAM integrations: AI agents in CI/CD that
generate and test integration code, with evals for the generated code.

## How we work
- Code, identifiers and commit messages in English.
- For design decisions, ask the developer first; don't hand over solutions.
- Claude sets up infrastructure and boilerplate; the developer leads the node logic.
- Personal working preferences live in `CLAUDE.local.md` (not committed).

## Guiding principle
**The LLM proposes. Code constrains, verifies and decides.**
- Constrain (before the LLM): closed lists/enums, templates, structured output.
- Verify (after the LLM): tests and validators. Verification is always objective, i.e. code.
- Decide (around the LLM): routing, budget, stop conditions.
- Use an LLM only where language understanding/judgment is needed and mistakes are cheap.

## Product
Engineer opens a request with vendor docs → minutes later a PR with a tested XSOAR integration draft
and a list of assumptions to review. Never merges or ships without human review.

## Graph (LangGraph)
| Node | Kind | Notes |
|---|---|---|
| parse_docs | code (MVP: OpenAPI only) | LLM only for free-text docs (later) |
| design_commands | hybrid | code enforces naming (`vendor-verb-noun`), LLM picks useful endpoints |
| map_schema | constrained LLM | choose from closed list + `no_match` + confidence; RAG for candidates & examples |
| build_fixtures | code for OpenAPI | fixtures copied from docs examples; verify verbatim; tag source |
| write_tests | LLM | before code (TDD), separate context from code writer |
| write_code | hybrid | skeleton from template, LLM writes command bodies; may NOT modify tests/fixtures |
| validate | code only | static → unit tests → sandbox (if any) |
| classify_failure | hybrid | rules for most failures, LLM for ambiguous; stop conditions always code |
| open_pr | code (+LLM wording) | normal PR, or Draft PR with report if stopped |

Stop conditions: max iterations, token budget, same tests failing twice in a row.

## Retrieval (map_schema)
- Extract mappings from integration YAMLs in demisto/content **with code** (no agent).
- One record = one chunk (a target field, or a historical mapping).
- Two indexes: standard target fields; historical vendor-field → target mappings.
- Hybrid search (vector + BM25), fused. Reranker only if eval shows it's needed.
- Behind the `Retriever` protocol (`src/integration_factory/retrieval/base.py`): start with an
  in-memory implementation; swap to Elasticsearch later without touching nodes.

## Eval
- Backtesting: give the agent only the docs, compare to the human integration.
- Execution-based: run the human-written unit tests against generated code.
- Leakage: time split (integrations added after model training cutoff); retrieval index built only from
  integrations before the split, **excluding by vendor**, not just by integration.
- Interface coupling: give the agent the YAML as contract; black-box tests at command level.
- Two tracks: implementation (docs + YAML → test pass rate) and design (docs only → compare to human YAML).
- Metrics: human-test pass rate (≥60%), mapping precision (≥85%), recall (≥70%), assumption calibration,
  tokens/time per integration. Targets are hypotheses; measure baseline first.

## Decisions
- MVP input: OpenAPI only. CI (GitHub Action: labeled issue → run → PR) is in the MVP.
- LLM: Anthropic API. Claude Sonnet 5.5 for development.
  Code depends on the `LLM` protocol (`src/integration_factory/llm/base.py`), not on the SDK.
- Embeddings: local open-source model (sentence-transformers) first; Voyage AI if retrieval is weak.
- Package manager: uv. Python ≥3.11.
- demisto/content lives in a **separate** folder (`../content`), partial + sparse clone.

## Status (2026-11-16)
- Skeleton created: pyproject, state.py, LLM and Retriever protocols, smoke test.
- Done: `uv sync --all-extras` + pytest pass (Python 3.13 via uv); git init + first commit;
  `../content` cloned (partial, sparse, `Packs/Base`).
- Next:
  1. Create the GitHub repo and push.
  2. API key in `.env`.
  3. Explore demisto/content together: pick one OpenAPI-based integration and dissect it.

## To verify in demisto/content
- Integration YAML structure (commands, args, outputs / context paths).
- Output conventions: standard context vs vendor-specific prefix (for `no_match`).
- How unit tests are structured (fixtures, mocking HTTP) and how they import CommonServerPython.
- demisto-sdk: validate / lint / format commands.
- How many OpenAPI-based integrations were added after the model cutoff (enough for a test set?).
