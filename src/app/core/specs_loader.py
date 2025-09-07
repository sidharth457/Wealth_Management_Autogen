import yaml

def load_agent_specs(path="agent_specs.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def build_system_prompt(agent_name, specs):
    desc = specs[agent_name]["description"]
    steps = specs[agent_name]["calculation_steps"]
    contract = specs[agent_name]["output_contract"]
    return f"{desc}\nSteps: {steps}\nOutput: {contract}\nReturn valid JSON per Schema; do not fabricate; include missing_fields if required data is absent."
