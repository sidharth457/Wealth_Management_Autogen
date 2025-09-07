# Wealth Management Multi‑Agent (AutoGen) – Ready‑to‑Run

A production‑grade skeleton for a hyper‑personalized wealth‑management multi‑agent system (Discovery → Planning || Tax → Risk → Compliance → Comms). Includes typed artifacts, policy‑as‑code, working mocks, and a FastAPI wrapper.

## Highlights

- Multi‑agent orchestration with explicit flow: Discovery → [Planning || Tax] → Risk → Compliance → Comms.
- Typed artifacts (Pydantic v2) for ClientProfile, PlanSet, TaxActionPlan, RiskReport, ComplianceDecision, CommsPackage.
- Policy‑as‑code: validation, guardrails, schema‑first outputs, missing_fields behavior.
- Working mocks for market data, tax brackets, and KYC.
- Comms agent produces a numbered “Financial DNA + Hyper‑Personalized Action Plan.”
- Single, shared ArtifactStore to persist intermediate outputs during runs.

## Quick start

1) Clone and setup

- Create a new virtual environment (Python 3.11+).
- Copy repo files, then:

```
pip install -e .
cp .env.example .env
```

2) Configure model

- In .env, set your model keys (example placeholders):
    - LLM_PROVIDER=azure_openai|openai|other
    - LLM_MODEL=gpt-4o-mini
    - LLM_API_KEY=YOUR_KEY

3) Run the full flow (CLI)
```
python -m app.main
```

4) Run API server (FastAPI)
```
uvicorn app.api.server:app --reload --port 8080
```

5) Call the flow endpoint
POST http://localhost:8080/cases/case_alex/run

- Body: contents of src/app/agents/mocks/client_input_alex.json

GET http://localhost:8080/cases/case_alex/artifacts

- Retrieves all artifacts for the case.

## Repository layout

- agent_specs.yaml: Business rules and calculation steps per agent.
- src/app/schemas: Pydantic models and JSON Schemas for every artifact.
- src/app/agents: Orchestration graph + runner; modular tools; mocks.
- src/app/core: Loader (YAML), policies (validation/defaults), prompts, utils.
- src/app/storage: Simple in‑memory store + optional DB hooks.
- src/app/api: FastAPI server and DTOs.
- tests: Minimal tests for schema validation and comms formatting.

## How it works

1) Discovery reads client JSON, validates headers, normalizes accounts/holdings/liabilities, and builds ClientProfile.
2) Planning and Tax run in parallel:
    - Planning computes cashflow, savings rate, liquidity runway, allocations, scenarios, and shortfalls.
    - Tax proposes TLH, Roth conversions, and DAF timing with compliance notes.
3) Risk aggregates exposures, checks concentrations vs caps, runs stress, proposes mitigations.
4) Compliance enforces policy‑as‑code, returns ApprovalGranted/ReworkNeeded with conditions/disclosures/redlines.
5) Comms builds a numbered, professional exec_summary with KPIs and a phased action plan; fills required fields.

## Customize agent prompts

- agent_specs.yaml drives each agent’s system prompt.
- src/app/core/specs_loader.py compiles description + calculation_steps + output contract into the system message.
- For deeper tuning, edit src/app/core/prompts.py.

## Swap models or providers

- src/app/config/llm.py controls model/provider settings and timeouts.
- You can route to different providers/versions via env vars.

## Persistence & logs

- src/app/storage/memory_store.py: in‑memory store for develop.
- src/app/storage/store.py: hook for Postgres/S3; implement save_artifacts/get_artifacts.
- All runs log inputs/outputs and rationale; add hashing in policies if needed.
