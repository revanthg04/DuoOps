/**
 * sampleRequests.js
 *
 * Fictional sample data that matches the agreed JSON contract between
 * the frontend (App Dev) and the backend (AI/ML).
 *
 * When the Python backend is ready, this file will be replaced by a
 * real API call:  GET /api/requests  → { requests: [...] }
 *
 * Fields:
 *   id              — unique request ID
 *   received_at     — ISO 8601 timestamp
 *   from            — sender email (fictional)
 *   subject         — email subject line
 *   client          — extracted client name
 *   currency        — extracted currency pair
 *   trade_id        — extracted trade reference number
 *   intent          — what the sender wants (enum string)
 *   priority        — "high" | "medium" | "low"
 *   confidence      — 0.0–1.0 (AI confidence in its extraction)
 *   summary         — one-sentence AI-generated summary
 *   recommended_action — what the system suggests doing
 *   status          — "pending" | "approved" | "rejected"
 */

const sampleRequests = [
  {
    id: "req-001",
    received_at: "2026-10-03T09:14:00Z",
    from: "raj.sharma@alphahedge.fake",
    subject: "Urgent — settlement failure TRD-20261003-4821",
    client: "Alpha Hedge Fund",
    currency: "USD/INR",
    trade_id: "TRD-20261003-4821",
    intent: "settlement_query",
    priority: "high",
    confidence: 0.95,
    summary: "Client reports USD/INR trade TRD-20261003-4821 is overdue for settlement.",
    recommended_action: "Check Nostro account status and reply with settlement confirmation or revised date.",
    status: "pending",
  },
  {
    id: "req-002",
    received_at: "2026-10-03T09:47:00Z",
    from: "priya.nair@betacapital.fake",
    subject: "FX rate confirmation needed — TRD-20261002-3317",
    client: "Beta Capital",
    currency: "EUR/USD",
    trade_id: "TRD-20261002-3317",
    intent: "rate_confirmation",
    priority: "medium",
    confidence: 0.88,
    summary: "Client needs written confirmation of the agreed EUR/USD rate for a trade booked on 2 Oct 2026.",
    recommended_action: "Pull trade from blotter and send rate confirmation email.",
    status: "pending",
  },
  {
    id: "req-003",
    received_at: "2026-10-03T10:02:00Z",
    from: "ankit.verma@gammafunds.fake",
    subject: "New trade request — GBP/JPY spot",
    client: "Gamma Funds",
    currency: "GBP/JPY",
    trade_id: null,
    intent: "new_trade_request",
    priority: "medium",
    confidence: 0.82,
    summary: "Client requests a spot GBP/JPY trade for 500,000 GBP at best available rate for account GF-2291.",
    recommended_action: "Forward to FX desk for execution; confirm price with client.",
    status: "pending",
  },
  {
    id: "req-004",
    received_at: "2026-10-03T10:31:00Z",
    from: "sara.ali@deltainvest.fake",
    subject: "Statement request — Sep 2026",
    client: "Delta Investments",
    currency: null,
    trade_id: null,
    intent: "statement_request",
    priority: "low",
    confidence: 0.97,
    summary: "Client is requesting their FX trading statement for September 2026.",
    recommended_action: "Generate and email the Sep 2026 account statement.",
    status: "approved",
  },
  {
    id: "req-005",
    received_at: "2026-10-03T11:15:00Z",
    from: "mohan.das@epsilontrading.fake",
    subject: "Discrepancy in margin call — TRD-20261001-7743",
    client: "Epsilon Trading",
    currency: "AUD/USD",
    trade_id: "TRD-20261001-7743",
    intent: "dispute",
    priority: "high",
    confidence: 0.79,
    summary: "Client disputes margin call amount on AUD/USD trade TRD-20261001-7743, claiming miscalculation.",
    recommended_action: "Escalate to risk desk for margin recalculation review.",
    status: "pending",
  },
];

export default sampleRequests;
