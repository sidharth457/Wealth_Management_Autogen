def test_client_profile_schema():
    from app.schemas.models import ClientProfile
    data = {
        "schema_version": "1.0",
        "as_of": "2025-08-13",
        "currency": "USD",
        "identity": {"Name": {"First": "Alex", "Last": "Parker"}},
        "preferences": {},
        "rationale": "Test rationale",
        "data_lineage": {"source": "test"},
        "missing_fields": []
    }
    cp = ClientProfile(**data)
    assert cp.schema_version == "1.0"

def test_plan_set_schema():
    from app.schemas.models import PlanSet
    data = {
        "assumptions": {},
        "baseline_cashflow": {},
        "scenarios": [],
        "probabilities": {},
        "funding_gaps": {},
        "savings_withdrawals": {},
        "liquidity_runway_months": 0.0,
        "allocation_guidance": {},
        "glidepath": None,
        "rationale": "Test rationale",
        "data_lineage": {"source": "test"},
        "missing_fields": []
    }
    ps = PlanSet(**data)
    assert ps.liquidity_runway_months == 0.0
