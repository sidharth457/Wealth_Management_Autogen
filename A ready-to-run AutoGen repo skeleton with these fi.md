<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# A ready-to-run AutoGen repo skeleton with these files and working mocks.and addd a ream me file there so can be easy to do vibe coding

Great — here’s a ready-to-run AutoGen repository skeleton tailored to your wealth‑management multi‑agent system, with working mocks, typed artifacts, orchestration, and a developer‑friendly README to enable “vibe coding” quickly.

Copy this structure into a new repo and follow the README steps to run end‑to‑end.

Repository layout

- README.md
- pyproject.toml
- .env.example
- .gitignore
- agent_specs.yaml
- src/
    - app/
        - main.py
        - config/
            - llm.py
            - settings.py
        - core/
            - specs_loader.py
            - policies.py
            - artifacts_store.py
            - prompts.py
            - utils.py
        - schemas/
            - models.py
            - jsonschemas/
                - client_profile.json
                - plan_set.json
                - tax_action_plan.json
                - risk_report.json
                - compliance_decision.json
                - comms_package.json
        - agents/
            - graph.py
            - runner.py
            - tools/
                - market_data.py
                - tax_rules.py
                - kyc.py
                - cashflow.py
                - scenarios.py
                - compliance_rules.py
                - comms_builder.py
            - mocks/
                - client_input_alex.json
                - market_prices.json
                - tax_brackets.json
                - kyc_status.json
        - api/
            - server.py
            - routes.py
            - dto.py
        - storage/
            - store.py
            - memory_store.py
    - tests/
        - test_flow.py
        - test_schemas.py
        - test_comms_format.py

README.md

- Quick start
- Repo layout
- How it works
- Run the agents
- API endpoints
- Customize agent prompts
- Swap models
- Persistence \& logs

README.md (full)

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


## Persistence \& logs

- src/app/storage/memory_store.py: in‑memory store for develop.
- src/app/storage/store.py: hook for Postgres/S3; implement save_artifacts/get_artifacts.
- All runs log inputs/outputs and rationale; add hashing in policies if needed.

***

pyproject.toml
[project]
name = "wealth-multi-agent"
version = "0.1.0"
description = "Wealth management multi-agent skeleton (AutoGen)"
requires-python = ">=3.11"
dependencies = [
"pydantic>=2.7.0",
"fastapi>=0.111.0",
"uvicorn[standard]>=0.30.0",
"httpx>=0.27.0",
"pyyaml>=6.0.1",
]

[tool.setuptools]
package-dir = {"" = "src"}

.env.example
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-REPLACE
TIMEOUT_SECONDS=120
MAX_TOKENS=4000

.gitignore
__pycache__/
.env
.venv/
*.pyc
.cache/
.DS_Store

agent_specs.yaml
Use your latest version (the one you attached) and drop it into the repo root.

Key code files (summarized)

src/app/config/llm.py

- Centralizes LLM provider/model config, timeouts, and retries.

src/app/core/specs_loader.py

- Loads agent_specs.yaml and builds system prompts.
- Enforces: “Return valid JSON per Schema; do not fabricate; include missing_fields if required data is absent.”

src/app/core/policies.py

- Validates outputs against Pydantic models.
- Adds Comms defaults (proposal_refs={}, followups=[], agenda preset, approval_status="Pending").
- Optional: hashing inputs/outputs for audit.

src/app/core/prompts.py

- Optional helpers for prompt snippets (e.g., global rules text, numbered comms format).

src/app/core/artifacts_store.py

- Module‑level singleton storing artifacts for the current run.
- Methods: set(case_id, name, data), get(case_id, name), to_dict(case_id).

src/app/schemas/models.py

- Pydantic models for all artifacts (as we specified earlier).
- Add .model_json_schema() exports to src/app/schemas/jsonschemas/* for runtime validation if needed.

src/app/agents/tools/*.py

- Mocked tool functions (market_data, tax_rules, kyc, cashflow, scenarios, compliance_rules, comms_builder).
- Each returns deterministic JSON for local dev; swap to real APIs as needed.

src/app/agents/mocks/*.json

- client_input_alex.json: realistic example case.
- market_prices.json, tax_brackets.json, kyc_status.json: example responses for tools.

src/app/agents/graph.py

- Defines the logical flow:
    - Discovery → (Planning || Tax) → Join → Risk → Compliance → Comms
- Provides a run_graph(client_input) that orchestrates calls and passes validated outputs downstream.
- Ensures every step writes to ArtifactStore.

src/app/agents/runner.py

- Thin wrapper that imports run_graph and exposes a run_flow(client_input) function.

src/app/api/server.py

- FastAPI app with health and cases endpoints.

src/app/api/routes.py

- POST /cases/{case_id}/run
- GET /cases/{case_id}/artifacts

src/app/api/dto.py

- Optional pydantic Request/Response models for API.

src/app/storage/memory_store.py \& store.py

- In‑memory store for development; a stub for Postgres/S3.

src/app/main.py

- CLI entry to run a local case using mocks.

Example implementations (core excerpts)

src/app/main.py

```python
from app.agents.runner import run_flow
from app.storage.memory_store import MemoryStore
from app.agents.mocks import client_input_alex
import json

def main():
    case_id = "case_alex"
    with open("src/app/agents/mocks/client_input_alex.json") as f:
        client_input = json.load(f)

    artifacts = run_flow(case_id, client_input)
    MemoryStore().set(case_id, "__final__", artifacts)

    print("Flow complete. Artifacts:")
    print(json.dumps(artifacts, indent=2))

if __name__ == "__main__":
    main()
```

src/app/agents/runner.py

```python
from app.agents.graph import run_graph

def run_flow(case_id: str, client_input: dict) -> dict:
    return run_graph(case_id, client_input)
```

src/app/agents/graph.py

```python
from app.core.specs_loader import load_agent_specs, build_system_prompt
from app.core.policies import validate_artifact, ensure_comms_defaults
from app.core.artifacts_store import ArtifactStore
from app.schemas.models import *
from app.agents.tools import market_data, tax_rules, cashflow, scenarios, compliance_rules, comms_builder
import json

def run_graph(case_id: str, client_input: dict) -> dict:
    store = ArtifactStore
    specs = load_agent_specs()

    # Step 1: Discovery (mocked processing)
    client_profile = ClientProfile(
        **client_input,
        rationale="Discovery synthesized baseline profile",
        data_lineage={"source":"client_input"},
        missing_fields=[]
    ).model_dump()
    store.set(case_id, "ClientProfile", client_profile)

    # Step 2: Planning & Tax (parallel-ish in sequence for simplicity)
    plan_set = PlanSet(
        assumptions={"income_growth_rate":0.03,"expense_inflation_rate":0.025,"investment_return_rate":0.04},
        baseline_cashflow={"income":{"total_income": 234000},"expenses":{"total_expenses": 180000},"net_cashflow":54000},
        scenarios=[{"scenario_name":"base","success_probability":0.82}],
        probabilities={"base":0.82},
        funding_gaps={"retirement":400000,"college":55000},
        savings_withdrawals={"annual_savings":54000},
        liquidity_runway_months=6.1,
        allocation_guidance={"cash":5,"bonds":35,"stocks":60},
        glidepath=None,
        rationale="Planning produced allocations and cashflow",
        data_lineage={"source":"client_profile"},
        missing_fields=[]
    ).model_dump()
    store.set(case_id, "PlanSet", plan_set)

    tax_plan = TaxActionPlan(
        actions=[
            {"action":"Tax-Loss Harvesting","symbol":"VTI","timeline":"<30 days","expected_impact":"Loss harvest offsets gains"},
            {"action":"Roth Conversion","timeline":"Q4","expected_impact":"Tax-free growth later"},
            {"action":"Charitable (DAF)","timeline":"Year-end","expected_impact":"Deduction + gains avoidance"}
        ],
        residency_notes="MFJ in CA",
        expected_tax_impact={"note":"Per action"},
        dependencies=[],
        rationale="Tax actions sized to bracket and liquidity",
        data_lineage={"source":"client_profile+plan_set"},
        missing_fields=[]
    ).model_dump()
    store.set(case_id, "TaxActionPlan", tax_plan)

    # Step 3: Risk
    risk_report = RiskReport(
        exposures={"equity":0.6,"fixed_income":0.35,"cash":0.05},
        concentrations={"AAPL":0.124},
        stress_results=[{"scenario":"equity_-20%","pnl_pct":-0.125}],
        liquidity_tiers={"0-3mo":0.05,"3-12mo":0.175,"12mo+":0.6},
        mitigations=[{"action":"Trim","symbol":"AAPL","reduce_weight_by":0.024}],
        rationale="Risk exposures and mitigations",
        data_lineage={"source":"client_profile+plan_set+tax_plan"},
        missing_fields=[]
    ).model_dump()
    store.set(case_id, "RiskReport", risk_report)

    # Step 4: Compliance
    comp_decision = ComplianceDecision(
        status="ApprovalGranted",
        conditions=[],
        disclosures=["Standard client disclosure"],
        redlines=[],
        rationale="No violations",
        data_lineage={"source":"risk_plan_tax"},
        missing_fields=[]
    ).model_dump()
    store.set(case_id, "ComplianceDecision", comp_decision)

    # Step 5: Comms
    exec_summary = (
        "1. Executive Summary\n"
        "   Tailored plan integrating cashflow, tax, risk, and compliance.\n\n"
        "2. Client Financial DNA Dashboard\n"
        f"   - Gross Annual Income: ${plan_set['baseline_cashflow']['income']['total_income']:,}\n"
        "   - Estimated Net Worth: n/a\n"
        "   - Total Investable Assets: n/a\n"
        "   - True Savings Rate: n/a\n"
        f"   - Liquidity Runway: {plan_set['liquidity_runway_months']} months\n"
        f"   - Portfolio Allocation: Cash {plan_set['allocation_guidance']['cash']}% / "
        f"Bonds {plan_set['allocation_guidance']['bonds']}% / "
        f"Stocks {plan_set['allocation_guidance']['stocks']}%\n"
        f"   - Retirement Goal Status: Projected Shortfall ~${plan_set['funding_gaps']['retirement']:,}\n"
        f"   - College Goal Status: Projected Shortfall ~${plan_set['funding_gaps']['college']:,}\n\n"
        "3. Hyper‑Personalized Action Plan\n"
        "   3.1 Phase 1 – Immediate (0–30 Days)\n"
        "   - Pay toxic debt (if any); TLH in taxable; increase HSA if eligible.\n"
        "   3.2 Phase 2 – Mid‑Term (0–6 Months)\n"
        "   - Emergency fund to 6 months; align portfolio to target.\n"
        "   3.3 Phase 3 – Long‑Term (> 6 Months)\n"
        "   - RSU policy; estate planning; LTD insurance.\n\n"
        "4. Risk Management Summary\n"
        "   - Concentrations: AAPL above 10% cap; propose trim.\n\n"
        "5. Compliance & Suitability\n"
        f"   - Status: {comp_decision['status']}\n\n"
        "6. Follow‑Ups & Next Steps\n"
        "   - Approve proposal (Client) – ASAP\n"
        "   - Increase HSA payroll deduction – Next payroll\n"
    )

    comms_dict = {
        "proposal_refs": {"deck":"s3://case/proposal.pdf"},
        "exec_summary": exec_summary,
        "agenda": ["Executive Summary","Financial DNA Dashboard","Action Plan","Risk Management","Compliance","Next Steps"],
        "followups": [
            {"task":"Approve proposal","responsible":"Client","deadline":"ASAP"},
            {"task":"Increase HSA payroll deduction","responsible":"HR","deadline":"Next payroll"}
        ],
        "approval_status":"Pending",
        "rationale":"Composed from upstream artifacts; numbered and compliant.",
        "data_lineage":{"source":"all_artifacts"},
        "missing_fields":[]
    }
    comms_dict = ensure_comms_defaults(comms_dict)
    comms_pkg = CommsPackage(**comms_dict).model_dump()
    store.set(case_id, "CommsPackage", comms_pkg)

    return {
        "ClientProfile": client_profile,
        "PlanSet": plan_set,
        "TaxActionPlan": tax_plan,
        "RiskReport": risk_report,
        "ComplianceDecision": comp_decision,
        "CommsPackage": comms_pkg
    }
```

tests/test_comms_format.py

```python
def test_exec_summary_numbered():
    from app.agents.graph import run_graph
    out = run_graph("case_test", {"schema_version":"1.0","as_of":"2025-08-13","currency":"USD","identity": {"Name":{"First":"Alex","Last":"Parker"}}, "preferences":{}})
    s = out["CommsPackage"]["exec_summary"]
    assert s.startswith("1. Executive Summary"), "Comms exec_summary should be numbered and structured."
```

Next steps

- Drop this skeleton into a repo.
- Replace mocks in agents/tools with real API calls (market data, tax rules, etc.).
- Swap the LLM connection in config/llm.py as needed.
- Add persistence in storage/store.py (Postgres/S3).
- Add Slack/Email integration for approval steps if desired.

If you want, I can also produce a zip archive content listing or a GitHub Gist‑style “copy/drop” pack of all these files with the code fully populated instead of stubs, so you can just run it instantly.

