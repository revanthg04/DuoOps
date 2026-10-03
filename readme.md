# OpsPilot (DuoOps) — Intelligent Operations Request Management

> **Hackathon Track:** Operations Automation & AI  
> **Problem Statement:** MRF receives ~8,000 emails daily, and nearly 3,500 require operational action. Many involve repetitive, rule-based operations that can be automated through an AI-powered email-processing solution.  
> **Proposed Solution:** OpsPilot — an intelligent assistant that ingests operations emails, uses Google Gemini to extract structured entities, calculates risk priority, drafts recommended actions, and provides a Human-in-the-Loop (HITL) dashboard for one-click operator approval.

---

## 🏗️ System Architecture

```
                       [ Incoming Operations Emails ]
                                     │
                                     ▼
               ┌───────────────────────────────────────────┐
               │         OpsPilot Backend (FastAPI)        │
               │   • sample_emails.py (Raw Email Ingestion)│
               │   • models.py (Pydantic Strict Schemas)   │
               └─────────────────────┬─────────────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │    Google AI Studio Gemini  │
                      │  (model: gemini-3.5-flash)  │
                      │   • Entity Extraction       │
                      │   • Intent Classification   │
                      │   • Priority & Confidence   │
                      │   • Recommended Action      │
                      └──────────────┬──────────────┘
                                     │ Structured JSON
                                     ▼
               ┌───────────────────────────────────────────┐
               │              REST API Layer               │
               │  • GET  /api/health                       │
               │  • GET  /api/requests                     │
               │  • POST /api/extract (Live Simulation)    │
               │  • POST /api/requests/{id}/status         │
               └─────────────────────┬─────────────────────┘
                                     │
                              Vite API Proxy
                                     │
                                     ▼
               ┌───────────────────────────────────────────┐
               │        OpsPilot Frontend (React 18)       │
               │  • Tailwind CSS Dashboard                 │
               │  • RequestCard Component                  │
               │  • Priority Badges & Confidence Meter     │
               │  • Human-in-the-Loop Approve / Reject     │
               │  • Real-Time Email Extraction Drawer      │
               └───────────────────────────────────────────┘
```

---

## 👥 Team Roles & Responsibilities

| Role | Teammate | Tech Stack | Deliverables |
| :--- | :--- | :--- | :--- |
| **App Dev** | Frontend Lead | React 18, Vite, Tailwind CSS | Dashboard UI, Request Cards, live state management, interactive testing drawer |
| **AI / ML** | Backend Lead | Python 3.14, FastAPI, `google-genai` | Gemini AI prompt engineering, structured extraction, REST endpoints, CLI tester |

---

## 📋 Agreed JSON Contract (API Schema)

Every email processed by the AI conforms to this strict data contract:

```jsonc
{
  "id": "req-001",                           // Unique request identifier
  "received_at": "2026-10-03T09:14:00Z",     // ISO 8601 timestamp
  "from": "raj.sharma@alphahedge.fake",       // Client email sender
  "subject": "Urgent — settlement failure TRD-20261003-4821",
  "client": "Alpha Hedge Fund",              // Extracted client / institution
  "currency": "USD/INR",                     // Currency or currency pair (null if none)
  "trade_id": "TRD-20261003-4821",           // Extracted trade reference (null if none)
  "intent": "settlement_query",              // settlement_query | rate_confirmation | new_trade_request | statement_request | dispute
  "priority": "high",                        // high | medium | low
  "confidence": 0.98,                        // Float between 0.0 and 1.0
  "summary": "Alpha Hedge Fund reports an overdue settlement causing exposure breach.",
  "recommended_action": "Check Nostro account status and trace counterparty settlement leg.",
  "status": "pending"                        // pending | approved | rejected
}
```

---

## 🚦 How Priority is Defined

Priority is determined using financial operations risk parameters:

* **`HIGH` (Red Badge):**
  * **Triggers:** Settlement failures, overdue fund deliveries, margin call disputes, exposure breaches, imminent market cutoffs.
  * **Action SLA:** Immediate (< 15 minutes).
* **`MEDIUM` (Amber Badge):**
  * **Triggers:** New order execution requests, spot trade bookings, rate confirmation inquiries.
  * **Action SLA:** Standard (< 1–2 hours).
* **`LOW` (Green Badge):**
  * **Triggers:** Monthly statement requests, ledger exports, routine inquiries.
  * **Action SLA:** Routine (End of Day).

---

## 🔘 Human-in-the-Loop: What Happens on "Approve"

Because financial regulations forbid unverified autonomous trade actions, OpsPilot uses **Human-in-the-Loop (HITL)**:
1. **AI handles 90% of manual effort:** Reads the email, extracts entities, prioritizes, and drafts the next operational step.
2. **Operator does 10%:** Reviews the card and clicks **Approve** or **Reject**.
3. **Downstream Automation Dispatched:**
   * **Settlement Query:** Queries Nostro bank balance and sends status to client.
   * **Rate Confirmation:** Pulls trade blotter and sends rate letter.
   * **New Trade Request:** Routes pre-filled ticket to FX trading desk blotter.
   * **Dispute:** Escalates urgent ticket to Risk & Valuation Desk.
   * **Statement:** Auto-generates ledger PDF and emails to client.

---

## 🚀 Quickstart Guide

### Prerequisites
* **Node.js** (v18+ or v22+)
* **Python** (v3.11+)
* **Google AI Studio API Key** (Free from [aistudio.google.com](https://aistudio.google.com/app/apikey))

---

### 1. Setup Backend (Python + FastAPI)

```powershell
# Navigate to backend directory
cd "c:\Users\Vijaya Sravya\Hackathon\DuoOps\backend"

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r ..\requirements.txt

# Configure your Gemini API Key in backend/.env:
# GEMINI_API_KEY=AIzaSyYourActualKeyHere

# (Optional) Verify Gemini API key via CLI tester:
.\venv\Scripts\python.exe test_gemini.py

# Launch FastAPI Server on port 8000:
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
* **API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **API Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

### 2. Setup Frontend (React + Vite + Tailwind)

In a **second terminal**:

```powershell
# Navigate to frontend directory
cd "c:\Users\Vijaya Sravya\Hackathon\DuoOps\frontend"

# Install node dependencies (first time only)
npm install

# Start Vite dev server
npm run dev
```

* **Live Dashboard:** [http://localhost:5173/](http://localhost:5173/)

---

## 🧪 Testing Features on the Live Dashboard

1. **Active AI Status:** Check the top right badge — should show **"Gemini AI Active"** (pulsing green).
2. **Review Extracted Cards:** Inspect priority badges, currency pairs, trade IDs, and AI confidence meters.
3. **Approve / Reject Action:** Click Approve or Reject on any card — observe the real-time state update and undo capability.
4. **Live Email Simulation:** Click **"+ Test Gemini Extraction"** in the top navbar:
   * Paste any custom email text or use the pre-filled template.
   * Click **"Run Gemini AI Extraction"**.
   * Watch Gemini analyze the text and prepend a brand new request card onto your live dashboard.

---

## 📁 Repository Structure

```
DuoOps/
├── README.md                 # Complete system documentation & guide
├── requirements.txt          # Python backend dependencies & frontend notes
├── .gitignore                # Ignores venv, node_modules, .env
├── backend/
│   ├── .env                  # Private Gemini API key (never commit)
│   ├── .env.example          # Template for environment variables
│   ├── gemini_service.py     # Gemini SDK client & extraction logic
│   ├── main.py               # FastAPI application with REST endpoints
│   ├── models.py             # Pydantic schemas conforming to JSON contract
│   ├── sample_emails.py      # Unstructured fictional test emails
│   └── test_gemini.py        # CLI diagnostic script for Gemini
└── frontend/
    ├── index.html            # Vite HTML mount entry point
    ├── vite.config.js        # Vite config with backend proxy (/api -> 8000)
    ├── tailwind.config.js    # Tailwind CSS layout configuration
    ├── package.json          # Frontend packages & scripts
    └── src/
        ├── main.jsx          # React DOM entry
        ├── App.jsx           # Main dashboard & live simulation drawer
        ├── index.css         # Global Tailwind directives
        ├── components/
        │   └── RequestCard.jsx # Request card UI with priority & action logic
        └── data/
            └── sampleRequests.js # Offline fallback sample data
```

