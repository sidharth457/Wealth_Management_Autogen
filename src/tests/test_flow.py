def test_full_flow():
    from app.agents.runner import run_flow
    from app.agents.mocks import client_input_alex
    case_id = "case_test"
    import json
    with open("src/app/agents/mocks/client_input_alex.json") as f:
        client_input = json.load(f)
    artifacts = run_flow(case_id, client_input)
    assert "ClientProfile" in artifacts
    assert "CommsPackage" in artifacts
