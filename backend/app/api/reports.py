from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class Report(BaseModel):
    venue_id: str
    issue: str
    comment: str = ""
    submitted_at: datetime = datetime.utcnow()

@router.post("/report")
def submit_report(report: Report):
    print(f"RECEIVED REPORT: {report}")
    return {"status": "ok", "message": "Thanks for reporting!"}
