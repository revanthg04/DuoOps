import os
import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import OpsRequest, EmailInput, ExtractedEmailData
from sample_emails import SAMPLE_RAW_EMAILS
import gemini_service

app = FastAPI(
    title="OpsPilot API",
    description="Backend service for intelligent operations request management powered by Google Gemini.",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for requests in current session
REQUESTS_DB: Dict[str, OpsRequest] = {}


def process_initial_sample_emails():
    """Initializes requests database using Gemini if API key is set, or default fallback."""
    has_key = gemini_service.is_api_configured()
    
    for email in SAMPLE_RAW_EMAILS:
        req_id = email["id"]
        if req_id in REQUESTS_DB:
            continue

        if has_key:
            try:
                extracted = gemini_service.extract_email_with_gemini(
                    sender=email["from"],
                    subject=email["subject"],
                    body=email["body"]
                )
                req = OpsRequest(
                    id=req_id,
                    received_at=email["received_at"],
                    sender=email["from"],
                    subject=email["subject"],
                    client=extracted.client,
                    currency=extracted.currency,
                    trade_id=extracted.trade_id,
                    intent=extracted.intent,
                    priority=extracted.priority,
                    confidence=extracted.confidence,
                    summary=extracted.summary,
                    recommended_action=extracted.recommended_action,
                    status="pending",
                    raw_body=email["body"]
                )
                REQUESTS_DB[req_id] = req
                continue
            except Exception as e:
                print(f"[Warning] Gemini extraction failed for {req_id}: {e}")

        # Fallback if key not yet entered or during offline dev
        fallback_data = {
            "req-001": ("Alpha Hedge Fund", "USD/INR", "TRD-20261003-4821", "settlement_query", "high", 0.95,
                        "Client reports USD/INR trade TRD-20261003-4821 is overdue for settlement.",
                        "Check Nostro account status and reply with settlement confirmation."),
            "req-002": ("Beta Capital", "EUR/USD", "TRD-20261002-3317", "rate_confirmation", "medium", 0.88,
                        "Client needs written confirmation of agreed EUR/USD rate for trade booked 2 Oct 2026.",
                        "Pull trade blotter and send official rate confirmation email."),
            "req-003": ("Gamma Funds", "GBP/JPY", None, "new_trade_request", "medium", 0.82,
                        "Client requests spot buy order for 500,000 GBP against JPY for GF-2291.",
                        "Route to FX trading desk for spot quote and execution."),
            "req-004": ("Delta Investments", None, None, "statement_request", "low", 0.97,
                        "Client requests FX trading and ledger statement for September 2026.",
                        "Generate Sep 2026 ledger statement from portal and send PDF."),
            "req-005": ("Epsilon Trading", "AUD/USD", "TRD-20261001-7743", "dispute", "high", 0.89,
                        "Client disputes USD 45,000 margin call claiming expected maximum is USD 18,200.",
                        "Escalate immediately to Risk and Valuation desk for margin sheet recalculation.")
        }
        
        info = fallback_data.get(req_id, ("Unknown Client", None, None, "settlement_query", "medium", 0.75, "Operations request", "Review details"))
        REQUESTS_DB[req_id] = OpsRequest(
            id=req_id,
            received_at=email["received_at"],
            sender=email["from"],
            subject=email["subject"],
            client=info[0],
            currency=info[1],
            trade_id=info[2],
            intent=info[3],
            priority=info[4],
            confidence=info[5],
            summary=info[6],
            recommended_action=info[7],
            status="pending",
            raw_body=email["body"]
        )


@app.on_event("startup")
def startup_event():
    process_initial_sample_emails()


@app.get("/api/health")
def health_check():
    """Health status and Gemini API key status."""
    configured = gemini_service.is_api_configured()
    return {
        "status": "healthy",
        "gemini_api_configured": configured,
        "model": "gemini-3.5-flash-lite",
        "message": "Gemini API key is active!" if configured else "Add your key to backend/.env (GEMINI_API_KEY)"
    }


@app.get("/api/requests")
def get_requests():
    """Returns all requests matching the agreed OpsPilot frontend contract."""
    # Ensure items are populated
    if not REQUESTS_DB:
        process_initial_sample_emails()

    items = [req.model_dump(by_alias=True) for req in REQUESTS_DB.values()]
    return {
        "requests": items,
        "count": len(items),
        "ai_powered": gemini_service.is_api_configured()
    }


@app.post("/api/extract")
def extract_new_email(payload: EmailInput):
    """
    Accepts any raw email (from, subject, body),
    runs Google Gemini to extract structured info, and saves it to the requests list.
    """
    new_id = f"req-{uuid.uuid4().hex[:6]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        extracted: ExtractedEmailData = gemini_service.extract_email_with_gemini(
            sender=payload.sender,
            subject=payload.subject,
            body=payload.body
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini AI processing error: {str(e)}"
        )

    new_request = OpsRequest(
        id=new_id,
        received_at=now_iso,
        sender=payload.sender,
        subject=payload.subject,
        client=extracted.client,
        currency=extracted.currency,
        trade_id=extracted.trade_id,
        intent=extracted.intent,
        priority=extracted.priority,
        confidence=extracted.confidence,
        summary=extracted.summary,
        recommended_action=extracted.recommended_action,
        status="pending",
        raw_body=payload.body
    )

    REQUESTS_DB[new_id] = new_request
    return {
        "success": True,
        "request": new_request.model_dump(by_alias=True)
    }


class StatusUpdate(BaseModel):
    status: str  # "approved" | "rejected" | "pending"


@app.post("/api/requests/{request_id}/status")
def update_status(request_id: str, payload: StatusUpdate):
    """Update approval/rejection status of a request."""
    if request_id not in REQUESTS_DB:
        raise HTTPException(status_code=404, detail="Request ID not found")

    if payload.status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    REQUESTS_DB[request_id].status = payload.status
    return {
        "id": request_id,
        "status": REQUESTS_DB[request_id].status
    }
