def test_exec_summary_numbered():
    from app.agents.graph import run_graph
    out = run_graph("case_test", {"schema_version":"1.0","as_of":"2025-08-13","currency":"USD","identity": {"Name":{"First":"Alex","Last":"Parker"}}, "preferences":{}})
    s = out["CommsPackage"]["exec_summary"]
    assert s.startswith("1. Executive Summary"), "Comms exec_summary should be numbered and structured."
