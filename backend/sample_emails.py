"""Sample fictional incoming emails representing operations emails at MRF."""

SAMPLE_RAW_EMAILS = [
    {
        "id": "req-001",
        "received_at": "2026-10-03T09:14:00Z",
        "from": "raj.sharma@alphahedge.fake",
        "subject": "Urgent — settlement failure TRD-20261003-4821",
        "body": """Hi Ops Team,

Our USD/INR trade with reference TRD-20261003-4821 was scheduled to settle yesterday at 15:00 UTC. However, our custodians report that funds have not been credited yet and the counterparty leg appears unfulfilled.

This is causing an exposure breach on our end. Please investigate immediately, verify the Nostro account status, and confirm settlement today without fail.

Regards,
Raj Sharma
Head of Settlements, Alpha Hedge Fund
raj.sharma@alphahedge.fake"""
    },
    {
        "id": "req-002",
        "received_at": "2026-10-03T09:47:00Z",
        "from": "priya.nair@betacapital.fake",
        "subject": "FX rate confirmation needed — TRD-20261002-3317",
        "body": """Hello Operations,

Could you please confirm the agreed spot EUR/USD exchange rate for trade TRD-20261002-3317 executed on 2 Oct 2026? 

Our middle office requires written confirmation of the rate and value date for our end-of-day reconciliation.

Thanks,
Priya Nair
Beta Capital
priya.nair@betacapital.fake"""
    },
    {
        "id": "req-003",
        "received_at": "2026-10-03T10:02:00Z",
        "from": "ankit.verma@gammafunds.fake",
        "subject": "New trade request — GBP/JPY spot",
        "body": """Dear Desk,

Please execute a spot buy order for 500,000 GBP against JPY at best available market rate for portfolio account GF-2291.

Please acknowledge execution and provide trade ticket details once filled.

Best regards,
Ankit Verma
Gamma Funds
ankit.verma@gammafunds.fake"""
    },
    {
        "id": "req-004",
        "received_at": "2026-10-03T10:31:00Z",
        "from": "sara.ali@deltainvest.fake",
        "subject": "Statement request — Sep 2026",
        "body": """Hi Support,

Could you please generate and email us our FX trading and ledger statement for the month of September 2026? 

Account ID: DELTA-FX-889.

Warm regards,
Sara Ali
Delta Investments
sara.ali@deltainvest.fake"""
    },
    {
        "id": "req-005",
        "received_at": "2026-10-03T11:15:00Z",
        "from": "mohan.das@epsilontrading.fake",
        "subject": "Discrepancy in margin call — TRD-20261001-7743",
        "body": """Attention Operations Risk,

We have received a margin call notice citing USD 45,000 for trade TRD-20261001-7743 (AUD/USD). According to our internal valuation and collateral agreement, the variation margin should not exceed USD 18,200.

We formally dispute this calculation and request an immediate margin recalculation sheet before any transfer is initiated.

Mohan Das
Treasury & Collateral, Epsilon Trading
mohan.das@epsilontrading.fake"""
    }
]
