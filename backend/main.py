import asyncio
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from enum import Enum
from typing import Dict, List
import os

app = FastAPI(title="YardVision Pro API", version="0.1")


class JobStatus(str, Enum):
    queued = "QUEUED"
    running = "RUNNING"
    complete = "COMPLETE"
    error = "ERROR"

class DesignJobRequest(BaseModel):
    project_id: str
    preview_only: bool = False

class CreditsDeductRequest(BaseModel):
    tenant_id: str
    amount: int

class CreditsPurchaseRequest(BaseModel):
    tenant_id: str
    plan_id: str

class RateCardItem(BaseModel):
    id: str
    item_type: str
    unit: str
    base_cost: float
    labor_hours: float
    category: str

fake_jobs: Dict[str, JobStatus] = {}
credit_wallets: Dict[str, int] = {}
rate_card_items: Dict[str, List[RateCardItem]] = {
    "default": [
        RateCardItem(
            id="plant_a",
            item_type="plant",
            unit="each",
            base_cost=10.0,
            labor_hours=0.5,
            category="Standard Plant",
        )
    ]
}

credit_plans = {
    "starter": 1000,
    "pro": 4000,
    "agency": 10000,
}

async def _process_job(job_id: str):
    fake_jobs[job_id] = JobStatus.running
    await asyncio.sleep(1)
    fake_jobs[job_id] = JobStatus.complete


@app.post("/v1/design-jobs")
def create_design_job(req: DesignJobRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    fake_jobs[job_id] = JobStatus.queued
    background_tasks.add_task(_process_job, job_id)
    return {"job_id": job_id}

@app.get("/v1/design-jobs/{job_id}")
def get_design_job(job_id: str):
    status = fake_jobs.get(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="job not found")
    return {"job_id": job_id, "status": status}

@app.post("/v1/credits/deduct")
def deduct_credits(req: CreditsDeductRequest):
    balance = credit_wallets.get(req.tenant_id, 0)
    if req.amount > balance:
        raise HTTPException(status_code=400, detail="insufficient credits")
    credit_wallets[req.tenant_id] = balance - req.amount
    return {"tenant_id": req.tenant_id, "balance": credit_wallets[req.tenant_id]}


@app.post("/v1/credits/purchase")
def purchase_credits(req: CreditsPurchaseRequest):
    credits = credit_plans.get(req.plan_id)
    if not credits:
        raise HTTPException(status_code=404, detail="plan not found")
    credit_wallets[req.tenant_id] = credit_wallets.get(req.tenant_id, 0) + credits
    return {
        "tenant_id": req.tenant_id,
        "balance": credit_wallets[req.tenant_id],
        "session_url": f"https://example.com/pay/{req.plan_id}",
    }

@app.get("/v1/rate-card")
def get_rate_card(tenant_id: str):
    items = rate_card_items.get(tenant_id) or rate_card_items["default"]
    return {"tenant_id": tenant_id, "items": [item.dict() for item in items]}
