import os
import json
from pathlib import Path

# Base prompt template used by OpsPilot
PROMPT_TEMPLATE = """You are OpsPilot, an intelligent operations analyst at a global financial firm.
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
8. Recommend a clear, professional operational next action."""

# Comprehensive domain training dataset for OpsPilot operations management
TRAINING_SAMPLES = [
    # 1. Settlement Failure - Nostro Account Break
    {
        "sender": "raj.sharma@alphahedge.fake",
        "subject": "Urgent — settlement failure TRD-20261003-4821",
        "body": "Hi Ops Team,\n\nOur USD/INR trade with reference TRD-20261003-4821 was scheduled to settle yesterday at 15:00 UTC. However, our custodians report that funds have not been credited yet and the counterparty leg appears unfulfilled.\n\nThis is causing an exposure breach on our end. Please investigate immediately, verify the Nostro account status, and confirm settlement today without fail.\n\nRegards,\nRaj Sharma\nHead of Settlements, Alpha Hedge Fund",
        "output": {
            "client": "Alpha Hedge Fund",
            "currency": "USD/INR",
            "trade_id": "TRD-20261003-4821",
            "intent": "settlement_query",
            "priority": "high",
            "confidence": 0.99,
            "summary": "Alpha Hedge Fund reports an overdue USD/INR settlement for trade TRD-20261003-4821 causing an exposure breach.",
            "recommended_action": "Check Nostro account ledger, trace counterparty settlement leg with custodian, and send immediate status update."
        }
    },
    # 2. Rate Confirmation - EOD Reconciliation
    {
        "sender": "priya.nair@betacapital.fake",
        "subject": "FX rate confirmation needed — TRD-20261002-3317",
        "body": "Hello Operations,\n\nCould you please confirm the agreed spot EUR/USD exchange rate for trade TRD-20261002-3317 executed on 2 Oct 2026? Our middle office requires written confirmation of the rate and value date for our end-of-day reconciliation.\n\nThanks,\nPriya Nair\nBeta Capital",
        "output": {
            "client": "Beta Capital",
            "currency": "EUR/USD",
            "trade_id": "TRD-20261002-3317",
            "intent": "rate_confirmation",
            "priority": "medium",
            "confidence": 0.98,
            "summary": "Beta Capital requests written confirmation of the spot EUR/USD rate and value date for trade TRD-20261002-3317.",
            "recommended_action": "Verify executed rate on the trade blotter and dispatch an official rate confirmation letter."
        }
    },
    # 3. New Trade Request - Spot Buy
    {
        "sender": "ankit.verma@gammafunds.fake",
        "subject": "New trade request — GBP/JPY spot",
        "body": "Dear Desk,\n\nPlease execute a spot buy order for 500,000 GBP against JPY at best available market rate for portfolio account GF-2291. Please acknowledge execution and provide trade ticket details once filled.\n\nBest regards,\nAnkit Verma\nGamma Funds",
        "output": {
            "client": "Gamma Funds",
            "currency": "GBP/JPY",
            "trade_id": None,
            "intent": "new_trade_request",
            "priority": "medium",
            "confidence": 0.97,
            "summary": "Gamma Funds places an order to buy 500,000 GBP against JPY at market rate for portfolio account GF-2291.",
            "recommended_action": "Route order to FX spot trading desk for execution and generate pre-filled trade blotter ticket."
        }
    },
    # 4. Statement Request - Monthly Ledger
    {
        "sender": "sara.ali@deltainvest.fake",
        "subject": "Statement request — Sep 2026",
        "body": "Hi Support,\n\nCould you please generate and email us our FX trading and ledger statement for the month of September 2026? Account ID: DELTA-FX-889.\n\nWarm regards,\nSara Ali\nDelta Investments",
        "output": {
            "client": "Delta Investments",
            "currency": None,
            "trade_id": None,
            "intent": "statement_request",
            "priority": "low",
            "confidence": 0.99,
            "summary": "Delta Investments requests the September 2026 FX trading and ledger statement for account DELTA-FX-889.",
            "recommended_action": "Generate September 2026 ledger PDF for account DELTA-FX-889 and email to client."
        }
    },
    # 5. Margin Call Dispute
    {
        "sender": "mohan.das@epsilontrading.fake",
        "subject": "Discrepancy in margin call — TRD-20261001-7743",
        "body": "Attention Operations Risk,\n\nWe have received a margin call notice citing USD 45,000 for trade TRD-20261001-7743 (AUD/USD). According to our internal valuation and collateral agreement, the variation margin should not exceed USD 18,200. We formally dispute this calculation and request an immediate margin recalculation sheet before any transfer is initiated.\n\nMohan Das\nTreasury & Collateral, Epsilon Trading",
        "output": {
            "client": "Epsilon Trading",
            "currency": "AUD/USD",
            "trade_id": "TRD-20261001-7743",
            "intent": "dispute",
            "priority": "high",
            "confidence": 0.98,
            "summary": "Epsilon Trading disputes a USD 45,000 margin call on AUD/USD trade TRD-20261001-7743, stating variation margin should be USD 18,200.",
            "recommended_action": "Place temporary hold on margin debit and escalate recalculation worksheet to Risk and Valuation Desk."
        }
    },
    # 6. SWIFT MT103 Missing Payment Leg
    {
        "sender": "laura.chen@apexglobal.fake",
        "subject": "URGENT: Missing SWIFT MT103 for settlement FX-992014",
        "body": "Dear Settlements,\n\nOur correspondent bank has not received the MT103 wire for 2,400,000 USD corresponding to trade FX-992014 (USD/SGD). Market cutoff is in 45 minutes. Please provide the UETR reference number immediately to avoid interest penalties.\n\nLaura Chen\nApex Global Asset Management",
        "output": {
            "client": "Apex Global Asset Management",
            "currency": "USD/SGD",
            "trade_id": "FX-992014",
            "intent": "settlement_query",
            "priority": "high",
            "confidence": 0.99,
            "summary": "Apex Global urgently requests UETR and proof of MT103 wire for 2.4M USD settlement FX-992014 due to imminent cutoff in 45 minutes.",
            "recommended_action": "Retrieve SWIFT UETR tracking code from payment gateway and transmit wire confirmation immediately."
        }
    },
    # 7. FX Forward Roll Request
    {
        "sender": "david.ross@oakridgecapital.fake",
        "subject": "Trade Request: Roll FX Forward TRD-20260915-1102 to Dec 2026",
        "body": "Hello Ops,\n\nWe would like to roll our existing EUR/USD forward position (trade reference TRD-20260915-1102) with nominal EUR 1,000,000 to maturity date 18-Dec-2026. Please calculate the swap points and provide terms.\n\nThanks,\nDavid Ross\nOakridge Capital Management",
        "output": {
            "client": "Oakridge Capital Management",
            "currency": "EUR/USD",
            "trade_id": "TRD-20260915-1102",
            "intent": "new_trade_request",
            "priority": "medium",
            "confidence": 0.97,
            "summary": "Oakridge Capital requests to roll forward EUR 1,000,000 on trade TRD-20260915-1102 to 18-Dec-2026.",
            "recommended_action": "Forward roll request with swap points calculation to FX Forward trading desk for pricing."
        }
    },
    # 8. Mismatched Trade Ticket Dispute
    {
        "sender": "elena.rostova@vanguardia-fx.fake",
        "subject": "Trade Discrepancy — Notional Mismatch TRD-20261004-9021",
        "body": "Hi Ops Desk,\n\nYour trade confirmation for TRD-20261004-9021 shows notional of 3,000,000 USD/CHF, whereas our broker blotter shows 2,500,000 USD/CHF. We cannot affirm this ticket until the discrepancy is amended.\n\nRegards,\nElena Rostova\nVanguardia FX",
        "output": {
            "client": "Vanguardia FX",
            "currency": "USD/CHF",
            "trade_id": "TRD-20261004-9021",
            "intent": "dispute",
            "priority": "high",
            "confidence": 0.99,
            "summary": "Vanguardia FX disputes trade TRD-20261004-9021 citing a notional mismatch between 3M USD and 2.5M USD.",
            "recommended_action": "Check dealer voice audio/chat logs to verify correct agreed notional and issue an amended trade confirmation."
        }
    },
    # 9. Audit Confirmation Request
    {
        "sender": "marcus.vance@vanceholdings.fake",
        "subject": "Annual Audit Confirmation Certificate - Vance Holdings",
        "body": "Dear Operations Support,\n\nOur statutory auditors (KPMG) require an independent balance confirmation for all open FX and derivative contracts as of 30 September 2026. Please send the signed confirmation directly to audit-confirm@kpmg.fake.\n\nSincerely,\nMarcus Vance\nChief Financial Officer, Vance Holdings",
        "output": {
            "client": "Vance Holdings",
            "currency": None,
            "trade_id": None,
            "intent": "statement_request",
            "priority": "low",
            "confidence": 0.98,
            "summary": "Vance Holdings requests an independent audit balance confirmation for open contracts as of 30-Sep-2026 for KPMG.",
            "recommended_action": "Generate standard audit confirmation pack for Vance Holdings and dispatch to specified auditor address."
        }
    },
    # 10. Rate Fixing Confirmation
    {
        "sender": "kenji.sato@nippontrading.fake",
        "subject": "Rate Fixing inquiry — USD/JPY NDF TRD-20260920-5519",
        "body": "Good morning,\n\nCould you confirm the benchmark fixing rate used for settlement of USD/JPY contract TRD-20260920-5519? We recorded 148.42 while our broker quotes 148.38.\n\nBest,\nKenji Sato\nNippon Trading Ltd",
        "output": {
            "client": "Nippon Trading Ltd",
            "currency": "USD/JPY",
            "trade_id": "TRD-20260920-5519",
            "intent": "rate_confirmation",
            "priority": "medium",
            "confidence": 0.97,
            "summary": "Nippon Trading requests verification of the benchmark fixing rate for USD/JPY contract TRD-20260920-5519.",
            "recommended_action": "Extract published central bank / Reuters fixing page screenshot and provide official rate audit trail."
        }
    },
    # 11. Overdue Payment Investigation
    {
        "sender": "claire.dupont@luminafunds.fake",
        "subject": "URGENT: Outstanding payment leg TRD-20261002-6611",
        "body": "Ops,\n\nValue date was yesterday for EUR/GBP transaction TRD-20261002-6611. Our accounting team shows a debit of 850,000 EUR but no corresponding GBP credit. Please initiate a SWIFT GPI trace immediately.\n\nClaire Dupont\nLumina Funds Paris",
        "output": {
            "client": "Lumina Funds",
            "currency": "EUR/GBP",
            "trade_id": "TRD-20261002-6611",
            "intent": "settlement_query",
            "priority": "high",
            "confidence": 0.99,
            "summary": "Lumina Funds reports that the GBP credit leg for EUR/GBP transaction TRD-20261002-6611 is missing despite EUR debit.",
            "recommended_action": "Initiate SWIFT gpi payment tracker for the GBP credit leg and provide tracking UETR to Lumina Funds."
        }
    },
    # 12. Limit Order Placement
    {
        "sender": "tariq.mansoor@gulfasset.fake",
        "subject": "Order: Limit buy USD/AED at 3.6725",
        "body": "Please place a limit order to purchase 10,000,000 USD against AED at rate 3.6725, good till cancelled (GTC). Account code: GA-FX-990.\n\nThank you,\nTariq Mansoor\nGulf Asset Management",
        "output": {
            "client": "Gulf Asset Management",
            "currency": "USD/AED",
            "trade_id": None,
            "intent": "new_trade_request",
            "priority": "medium",
            "confidence": 0.98,
            "summary": "Gulf Asset Management places a GTC limit buy order for 10M USD/AED at 3.6725 for account GA-FX-990.",
            "recommended_action": "Enter limit order into electronic order book and confirm resting order status with client."
        }
    },
    # 13. Year-to-Date Fee Statement
    {
        "sender": "hannah.schmidt@bavariacapital.fake",
        "subject": "Request for YTD Brokerage and Clearing Fee Schedule",
        "body": "Dear DuoOps team,\n\nKindly send us the comprehensive breakdown of all clearing and brokerage fees charged to account BC-DE-4411 from Jan 1 2026 through Sep 30 2026.\n\nRegards,\nHannah Schmidt\nBavaria Capital",
        "output": {
            "client": "Bavaria Capital",
            "currency": None,
            "trade_id": None,
            "intent": "statement_request",
            "priority": "low",
            "confidence": 0.98,
            "summary": "Bavaria Capital requests the YTD brokerage and clearing fee schedule for account BC-DE-4411.",
            "recommended_action": "Pull clearing fee schedule report from accounting ledger and send report to Bavaria Capital."
        }
    },
    # 14. Interest Claim Dispute
    {
        "sender": "roberto.silva@saopaulotrading.fake",
        "subject": "DISPUTE: Rejecting interest claim notice TRD-20260918-1004",
        "body": "Team,\n\nWe received a claim for EUR 4,200 late interest regarding settlement delay on TRD-20260918-1004. As per SWIFT logs, the delay was caused by your intermediary bank clearing cutoff, not our SSI. We formally reject this claim.\n\nRoberto Silva\nSao Paulo Trading",
        "output": {
            "client": "Sao Paulo Trading",
            "currency": None,
            "trade_id": "TRD-20260918-1004",
            "intent": "dispute",
            "priority": "high",
            "confidence": 0.98,
            "summary": "Sao Paulo Trading rejects an EUR 4,200 interest claim on trade TRD-20260918-1004, attributing delay to intermediary bank.",
            "recommended_action": "Review SWIFT timestamp audit trail with Intermediary Bank and escalate to Operations Legal Desk."
        }
    },
    # 15. Cross-Currency Swap Confirmation
    {
        "sender": "artur.kowalski@balticinvest.fake",
        "subject": "Confirmation request: USD/PLN swap TRD-20261001-8842",
        "body": "Hi,\n\nPlease furnish the formal confirmation sheet for the 1-month cross-currency swap TRD-20261001-8842 executed yesterday.\n\nArtur Kowalski\nBaltic Invest",
        "output": {
            "client": "Baltic Invest",
            "currency": "USD/PLN",
            "trade_id": "TRD-20261001-8842",
            "intent": "rate_confirmation",
            "priority": "medium",
            "confidence": 0.99,
            "summary": "Baltic Invest requests the formal trade confirmation sheet for a 1-month USD/PLN cross-currency swap TRD-20261001-8842.",
            "recommended_action": "Generate and email the bilateral ISDA swap confirmation schedule for TRD-20261001-8842."
        }
    }
]


def generate_jsonl(output_path: Path):
    """Generates standard Google AI Studio JSONL tuning dataset."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for sample in TRAINING_SAMPLES:
            prompt_text = PROMPT_TEMPLATE.format(
                sender=sample["sender"],
                subject=sample["subject"],
                body=sample["body"]
            )
            output_text = json.dumps(sample["output"], ensure_ascii=False)
            
            # Google AI Studio standard tuning format:
            record = {
                "text_input": prompt_text,
                "output": output_text
            }
            f.write(json.dumps(record) + "\n")
            count += 1
            
    print(f"Generated {count} training samples at: {output_path}")


if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "training_dataset.jsonl"
    generate_jsonl(target)
