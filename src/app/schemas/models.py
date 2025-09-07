from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ClientProfile(BaseModel):
    schema_version: str
    as_of: str
    currency: str
    identity: Dict[str, Any]
    preferences: Dict[str, Any]
    rationale: str
    data_lineage: Dict[str, Any]
    missing_fields: List[str]

class PlanSet(BaseModel):
    assumptions: Dict[str, Any]
    baseline_cashflow: Dict[str, Any]
    scenarios: List[Dict[str, Any]]
    probabilities: Dict[str, float]
    funding_gaps: Dict[str, float]
    savings_withdrawals: Dict[str, Any]
    liquidity_runway_months: float
    allocation_guidance: Dict[str, float]
    glidepath: Optional[Any]
    rationale: str
    data_lineage: Dict[str, Any]
    missing_fields: List[str]

class TaxActionPlan(BaseModel):
    actions: List[Dict[str, Any]]
    residency_notes: str
    expected_tax_impact: Dict[str, Any]
    dependencies: List[Any]
    rationale: str
    data_lineage: Dict[str, Any]
    missing_fields: List[str]

class RiskReport(BaseModel):
    exposures: Dict[str, float]
    concentrations: Dict[str, float]
    stress_results: List[Dict[str, Any]]
    liquidity_tiers: Dict[str, float]
    mitigations: List[Dict[str, Any]]
    rationale: str
    data_lineage: Dict[str, Any]
    missing_fields: List[str]

class ComplianceDecision(BaseModel):
    status: str
    conditions: List[Any]
    disclosures: List[str]
    redlines: List[Any]
    rationale: str
    data_lineage: Dict[str, Any]
    missing_fields: List[str]

class CommsPackage(BaseModel):
    proposal_refs: Dict[str, Any]
    exec_summary: str
    agenda: List[str]
    followups: List[Dict[str, Any]]
    approval_status: str
    rationale: str
    data_lineage: Dict[str, Any]
    missing_fields: List[str]
