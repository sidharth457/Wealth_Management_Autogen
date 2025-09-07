def validate_artifact(artifact, model):
    # Validate artifact against Pydantic model
    return model(**artifact)

def ensure_comms_defaults(comms_dict):
    comms_dict.setdefault("proposal_refs", {})
    comms_dict.setdefault("followups", [])
    comms_dict.setdefault("agenda", ["Executive Summary","Financial DNA Dashboard","Action Plan","Risk Management","Compliance","Next Steps"])
    comms_dict.setdefault("approval_status", "Pending")
    return comms_dict
