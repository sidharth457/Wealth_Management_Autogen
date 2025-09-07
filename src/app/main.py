from app.agents.runner import run_flow
from app.storage.memory_store import MemoryStore
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
