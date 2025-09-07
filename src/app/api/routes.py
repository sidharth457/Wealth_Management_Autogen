from fastapi import APIRouter, Request
from app.agents.runner import run_flow
from app.storage.memory_store import MemoryStore
import json

router = APIRouter()

@router.post("/cases/{case_id}/run")
async def run_case(case_id: str, request: Request):
    client_input = await request.json()
    artifacts = run_flow(case_id, client_input)
    MemoryStore().set(case_id, "__final__", artifacts)
    return artifacts

@router.get("/cases/{case_id}/artifacts")
async def get_artifacts(case_id: str):
    return MemoryStore().to_dict(case_id)
