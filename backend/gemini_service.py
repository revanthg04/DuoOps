import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from models import ExtractedEmailData

load_dotenv()
logger = logging.getLogger("opspilot")

def get_gemini_client() -> Optional[genai.Client]:
    """Returns a Gemini Client if GEMINI_API_KEY is configured, else None."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    return genai.Client(api_key=api_key)


def is_api_configured() -> bool:
    """Checks if a valid Google AI Studio API key is provided."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(api_key and api_key != "your_gemini_api_key_here")


def extract_email_with_gemini(sender: str, subject: str, body: str) -> ExtractedEmailData:
    """
    Calls Google Gemini (gemini-2.5-flash) using Google AI Studio API
    to parse an unstructured operations email into structured JSON.
    """
    client = get_gemini_client()
    if not client:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add your Google AI Studio API key in backend/.env"
        )

    prompt = f"""
You are OpsPilot, an intelligent operations analyst at a global financial firm.
Analyze this incoming operations email and extract structured details.

Sender: {sender}
Subject: {subject}
Body:
\"\"\"
{body}
\"\"\"

Guidelines:
1. Identify the client or institution name (check signature or sender domain).
2. Look for any currency or currency pair mentioned (e.g., 'USD/INR', 'EUR/USD', 'GBP/JPY'). If none, return null.
3. Look for trade reference identifiers (e.g. 'TRD-20261003-4821'). If none, return null.
4. Categorize intent into one of: 'settlement_query', 'rate_confirmation', 'new_trade_request', 'statement_request', 'dispute'.
5. Set priority to 'high' for settlement failures, margin disputes or urgent escalations; 'medium' for quotes/confirmations; 'low' for routine queries.
6. Provide a confidence score between 0.0 and 1.0.
7. Provide a concise 1-sentence summary of the request.
8. Recommend a clear, professional operational next action.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedEmailData,
            temperature=0.1
        )
    )

    if hasattr(response, "parsed") and response.parsed:
        return response.parsed
    
    # Fallback parsing from text
    return ExtractedEmailData.model_validate_json(response.text)
