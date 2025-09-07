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

    # Step 5: Comms (standardized output)
    artifacts = {
        "ClientProfile": client_profile,
        "PlanSet": plan_set,
        "TaxActionPlan": tax_plan,
        "RiskReport": risk_report,
        "ComplianceDecision": comp_decision
    }
    comms_pkg = comms_builder.build_comms_package(artifacts)
    store.set(case_id, "CommsPackage", comms_pkg)

    return {**artifacts, "CommsPackage": comms_pkg}
