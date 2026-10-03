r"""
Quick CLI tester to verify Gemini API connection and email extraction.
Run with:
    .\venv\Scripts\python.exe test_gemini.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from gemini_service import is_api_configured, extract_email_with_gemini
from sample_emails import SAMPLE_RAW_EMAILS

def main():
    print("=" * 60)
    print(" OpsPilot - Gemini API Connection Test")
    print("=" * 60)

    if not is_api_configured():
        print("\n[!] GEMINI_API_KEY is not configured in backend/.env!")
        print("\nSteps to configure:")
        print(" 1. Go to https://aistudio.google.com/app/apikey")
        print(" 2. Click 'Create API key'")
        print(" 3. Open backend/.env and paste: GEMINI_API_KEY=your_key_here")
        print(" 4. Run this script again!\n")
        sys.exit(1)

    print("[OK] GEMINI_API_KEY detected in backend/.env.")
    print("Sending Sample Email 1 to Gemini for live extraction...")

    sample = SAMPLE_RAW_EMAILS[0]
    try:
        result = extract_email_with_gemini(
            sender=sample["from"],
            subject=sample["subject"],
            body=sample["body"]
        )
        print("\n[SUCCESS] Gemini AI extracted structured JSON:\n")
        print(f"  * Client:             {result.client}")
        print(f"  * Currency:           {result.currency}")
        print(f"  * Trade ID:           {result.trade_id}")
        print(f"  * Intent:             {result.intent}")
        print(f"  * Priority:           {result.priority}")
        print(f"  * Confidence:         {result.confidence * 100:.1f}%")
        print(f"  * Summary:            {result.summary}")
        print(f"  * Recommended Action: {result.recommended_action}")
        print("\n" + "=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Gemini API call failed: {e}")

if __name__ == "__main__":
    main()
