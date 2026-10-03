from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class ExtractedEmailData(BaseModel):
    """Structured data extracted by Gemini from an operations email."""
    client: str = Field(description="Extracted client or company name. If unknown, infer from email domain or context.")
    currency: Optional[str] = Field(None, description="Currency or currency pair involved (e.g., 'USD/INR', 'EUR/USD'). null if none.")
    trade_id: Optional[str] = Field(None, description="Trade reference or ID if mentioned (e.g., 'TRD-20261003-4821'). null if none.")
    intent: Literal["settlement_query", "rate_confirmation", "new_trade_request", "statement_request", "dispute"] = Field(
        description="The primary intent of the email."
    )
    priority: Literal["high", "medium", "low"] = Field(
        description="Priority: 'high' for urgent settlement issues/disputes/deadlines, 'medium' for standard requests/trade queries, 'low' for statements/routine queries."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0.0 and 1.0 indicating how confident the model is in the extraction."
    )
    summary: str = Field(description="A clear one-sentence summary of the client's request.")
    recommended_action: str = Field(description="A concrete, concise operational action recommendation for operations staff.")


class EmailInput(BaseModel):
    """Raw email input payload."""
    model_config = ConfigDict(populate_by_name=True)

    sender: str = Field(..., alias="from")
    subject: str
    body: str


class OpsRequest(BaseModel):
    """Full request record conforming to OpsPilot frontend contract."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    received_at: str
    sender: str = Field(..., alias="from")
    subject: str
    client: str
    currency: Optional[str] = None
    trade_id: Optional[str] = None
    intent: str
    priority: str
    confidence: float
    summary: str
    recommended_action: str
    status: Literal["pending", "approved", "rejected"] = "pending"
    raw_body: Optional[str] = None
