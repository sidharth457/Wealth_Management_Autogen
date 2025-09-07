
# Wealth Management Multi-Agent System (AutoGen)

A robust, production-ready framework for building hyper-personalized, multi-agent wealth management solutions. This system orchestrates the entire client journey from Discovery through Planning, Tax, Risk, Compliance, and Communications, leveraging typed artifacts, policy-as-code, comprehensive mocks, and a FastAPI API layer.


## Key Features

- **Multi-Agent Orchestration:** Explicit, modular flow: Discovery → [Planning & Tax in parallel] → Risk → Compliance → Communications.
- **Typed Artifacts:** Strongly-typed outputs using Pydantic v2 for all major entities (ClientProfile, PlanSet, TaxActionPlan, RiskReport, ComplianceDecision, CommsPackage).
- **Policy-as-Code:** Built-in validation, guardrails, schema-first outputs, and robust handling of missing fields.
- **Comprehensive Mocks:** Includes realistic market data, tax brackets, and KYC scenarios for development and testing.
- **Professional Communications:** Automated generation of a numbered, executive “Financial DNA & Hyper-Personalized Action Plan.”
- **Centralized Artifact Store:** Shared store for all intermediate and final outputs, supporting traceability and auditability.

pip install -e .

## Getting Started

### 1. Environment Setup

- Ensure Python 3.11+ is installed.
- Clone this repository and navigate to the project directory.
- Create and activate a virtual environment:
    ```sh
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On Linux/Mac
    ```
- Install dependencies:
    ```sh
    pip install -e .
    cp .env.example .env
    ```

### 2. Model Configuration

Edit the `.env` file to set your model provider and API keys:

- `LLM_PROVIDER=azure_openai|openai|other`
- `LLM_MODEL=gpt-4o-mini`
- `LLM_API_KEY=YOUR_KEY`

### 3. Running the Application

- **Full Orchestration (CLI):**
    ```sh
    python -m app.main
    ```
- **API Server (FastAPI):**
    ```sh
    uvicorn app.api.server:app --reload --port 8080
    ```

### 4. Example API Usage

- **Run a Case:**
    - `POST http://localhost:8080/cases/case_alex/run`
    - Body: Use the contents of `src/app/agents/mocks/client_input_alex.json`
- **Retrieve Artifacts:**
    - `GET http://localhost:8080/cases/case_alex/artifacts`


## Repository Structure

- `agent_specs.yaml`: Business rules and calculation steps for each agent.
- `src/app/schemas`: Pydantic models and JSON Schemas for all artifacts.
- `src/app/agents`: Orchestration graph, runner, modular tools, and mocks.
- `src/app/core`: YAML loader, policy validation/defaults, prompts, and utilities.
- `src/app/storage`: In-memory store and optional database hooks.
- `src/app/api`: FastAPI server and DTOs.
- `tests`: Minimal tests for schema validation and communications formatting.


## System Overview

1. **Discovery:** Reads and validates client JSON, normalizes accounts/holdings/liabilities, and constructs the ClientProfile artifact.
2. **Planning & Tax (Parallel):**
    - *Planning:* Computes cashflow, savings rate, liquidity runway, allocations, scenarios, and identifies shortfalls.
    - *Tax:* Proposes tax-loss harvesting, Roth conversions, and DAF timing, with compliance notes.
3. **Risk:** Aggregates exposures, checks concentration limits, runs stress tests, and proposes mitigations.
4. **Compliance:** Enforces policy-as-code, returns ApprovalGranted or ReworkNeeded with conditions, disclosures, and redlines.
5. **Communications:** Builds a professional, numbered executive summary with KPIs and a phased action plan, ensuring all required fields are completed.


## Customizing Agent Prompts

- `agent_specs.yaml` defines each agent’s system prompt.
- `src/app/core/specs_loader.py` compiles descriptions, calculation steps, and output contracts into system messages.
- For advanced tuning, modify `src/app/core/prompts.py`.


## Model & Provider Flexibility

- `src/app/config/llm.py` manages model/provider settings and timeouts.
- Easily switch between providers or model versions using environment variables.


## Persistence & Logging

- `src/app/storage/memory_store.py`: In-memory store for development.
- `src/app/storage/store.py`: Hooks for Postgres/S3; implement `save_artifacts`/`get_artifacts` as needed.
- All runs log inputs, outputs, and rationale. Add hashing in policies for enhanced traceability if required.
