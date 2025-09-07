from app.agents.graph import run_graph

def run_flow(case_id: str, client_input: dict) -> dict:
    return run_graph(case_id, client_input)
