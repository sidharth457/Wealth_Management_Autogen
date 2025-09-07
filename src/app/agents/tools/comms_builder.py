import os
import requests
import json

import locale
locale.setlocale(locale.LC_ALL, '')

def format_currency(val):
    try:
        return "$" + locale.format_string("%d", int(val), grouping=True)
    except:
        return "n/a"

def build_exec_summary(artifacts):
    # Compose prompt for Ollama llama2:latest
    # Use Gemini API for exec_summary generation
    essential = {
        "ClientProfile": {
            "identity": artifacts.get("ClientProfile", {}).get("identity", {}),
            "preferences": artifacts.get("ClientProfile", {}).get("preferences", {}),
            "rationale": artifacts.get("ClientProfile", {}).get("rationale", "")
        },
        "PlanSet": {
            "baseline_cashflow": artifacts.get("PlanSet", {}).get("baseline_cashflow", {}),
            "funding_gaps": artifacts.get("PlanSet", {}).get("funding_gaps", {}),
            "liquidity_runway_months": artifacts.get("PlanSet", {}).get("liquidity_runway_months", "n/a"),
            "allocation_guidance": artifacts.get("PlanSet", {}).get("allocation_guidance", {})
        },
        "TaxActionPlan": artifacts.get("TaxActionPlan", {}),
        "RiskReport": artifacts.get("RiskReport", {}),
        "ComplianceDecision": artifacts.get("ComplianceDecision", {})
    }
    prompt = (
        "You are a financial communications agent. Given the following essential upstream artifacts, generate a client-facing exec_summary string in the following format. Be concise, professional, and readable. Focus on actionable steps for tax loss harvesting and other recommendations, with clear instructions.\n\nArtifacts:\n"
        + json.dumps(essential, indent=2)
        + "\n\nOutput Format:\n---\nExecutive Summary for Alex Parker\n\n1. What We Did\n- Brief summary of the analysis and recommendations.\n\n2. What You Need to Do\n- Clear, numbered action items (e.g., tax loss harvesting, portfolio adjustments).\n\n3. How to Do It\n- Step-by-step instructions for each action, especially for tax loss harvesting.\n---"
    )

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyAwRrdLK_UibxUbfMAgRAzloe84VICJg6w"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        result = response.json()
        # Gemini response parsing
        summary = result["candidates"][0]["content"]["parts"][0]["text"] if "candidates" in result else str(result)
    except Exception as e:
        summary = "[Gemini API error: " + str(e) + "]"
    # Fallback: parse missing fields and followups from artifacts
    missing = []
    cp = artifacts.get("ClientProfile", {})
    plan = artifacts.get("PlanSet", {})
    for k, v in [("Gross Annual Income", plan.get("baseline_cashflow", {}).get("income", {}).get("total_income", "n/a")),
                ("Estimated Net Worth", cp.get("derived", {}).get("net_worth", "n/a")),
                ("Total Investable Assets", cp.get("derived", {}).get("total_investable_assets", "n/a")),
                ("True Savings Rate", plan.get("derived", {}).get("true_savings_rate", "n/a")),
                ("Housing Cost Ratio", cp.get("derived", {}).get("housing_cost_ratio", "n/a"))]:
        if v == "n/a":
            missing.append(k)
    followups = [
        {"task": "Approve proposal", "responsible": "Client", "deadline": "ASAP"},
        {"task": "Increase HSA payroll deduction", "responsible": "HR", "deadline": "Next payroll"}
    ]
    return summary, missing, followups

def build_comms_package(artifacts):
    exec_summary, missing_fields, followups = build_exec_summary(artifacts)
    comms = {
        "proposal_refs": {"deck": "s3://case_id/proposal.pdf"},
        "exec_summary": exec_summary,
        "agenda": ["Executive Summary","Financial DNA Dashboard","Action Plan","Risk Management","Compliance","Next Steps"],
        "followups": followups,
        "approval_status": "Pending",
        "rationale": "Composed from upstream artifacts; numbered and compliant.",
        "missing_fields": missing_fields,
        "data_lineage": {"source": "all_artifacts"}
    }
    return comms
