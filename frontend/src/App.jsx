import { useState, useEffect } from 'react'
import defaultRequests from './data/sampleRequests'
import RequestCard from './components/RequestCard'

export default function App() {
  const [requests, setRequests] = useState(defaultRequests)
  const [backendStatus, setBackendStatus] = useState({
    connected: false,
    aiPowered: false,
    message: 'Checking backend status...'
  })
  const [isLoading, setIsLoading] = useState(false)
  const [showExtractForm, setShowExtractForm] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  // Form fields for new email extraction
  const [emailForm, setEmailForm] = useState({
    from: 'compliance@vanguardasset.fake',
    subject: 'Urgent: Settlement Delay TRD-20261003-9912',
    body: `Hello Ops Team,\n\nOur USD/JPY trade TRD-20261003-9912 for 1,200,000 USD is currently past its settlement cut-off time.\nWe suspect a Nostro account issue on the counterparty side. Please verify the correspondent bank swift message immediately and notify our treasury.\n\nRegards,\nVanguard Asset Management`
  })

  // Check backend health & fetch requests
  const loadRequests = async () => {
    setIsLoading(true)
    try {
      // 1. Health check
      const healthRes = await fetch('/api/health')
      if (healthRes.ok) {
        const health = await healthRes.json()
        setBackendStatus({
          connected: true,
          aiPowered: health.gemini_api_configured,
          message: health.message
        })
      }

      // 2. Fetch requests from backend
      const res = await fetch('/api/requests')
      if (res.ok) {
        const data = await res.json()
        if (data.requests && data.requests.length > 0) {
          setRequests(data.requests)
        }
      }
    } catch {
      setBackendStatus({
        connected: false,
        aiPowered: false,
        message: 'Backend server offline (showing local sample data)'
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadRequests()
  }, [])

  // Handle status update (Approve/Reject)
  const handleStatusChange = async (id, newStatus) => {
    setRequests(prev => prev.map(r => r.id === id ? { ...r, status: newStatus } : r))
    try {
      await fetch(`/api/requests/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      })
    } catch {
      // Offline fallback: local state already updated
    }
  }

  // Handle extracting a custom email with Gemini
  const handleExtractSubmit = async (e) => {
    e.preventDefault()
    setExtracting(true)
    setErrorMsg('')
    try {
      const res = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailForm)
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Extraction failed')
      }

      const data = await res.json()
      if (data.request) {
        setRequests(prev => [data.request, ...prev])
        setShowExtractForm(false)
      }
    } catch (err) {
      setErrorMsg(err.message)
    } finally {
      setExtracting(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100">
      {/* ── Top Navigation Bar ── */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-20 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-base shadow-sm">
              OP
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-800 text-lg">OpsPilot</span>
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">v1.0</span>
              </div>
              <p className="text-xs text-slate-400">Intelligent Operations Request Management</p>
            </div>
          </div>

          {/* Backend / Gemini Status Pill */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs">
              <span className={`w-2.5 h-2.5 rounded-full ${
                backendStatus.connected && backendStatus.aiPowered
                  ? 'bg-emerald-500 animate-pulse'
                  : backendStatus.connected
                  ? 'bg-amber-400'
                  : 'bg-slate-400'
              }`} />
              <span className="font-medium text-slate-600 hidden sm:inline">
                {backendStatus.connected && backendStatus.aiPowered
                  ? 'Gemini AI Active'
                  : backendStatus.connected
                  ? 'Backend Connected (Add Gemini Key)'
                  : 'Demo Mode (Offline)'}
              </span>
            </div>

            <button
              onClick={() => setShowExtractForm(!showExtractForm)}
              className="rounded-lg bg-blue-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 transition"
            >
              {showExtractForm ? 'Close Form' : '+ Test Gemini Extraction'}
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Container ── */}
      <main className="max-w-5xl mx-auto px-4 py-6">

        {/* API Key Notification Banner (if backend is connected but key is missing) */}
        {backendStatus.connected && !backendStatus.aiPowered && (
          <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
            <div>
              <p className="font-semibold text-amber-900">Google AI Studio API Key Needed for Live Gemini Extraction</p>
              <p className="text-xs text-amber-700 mt-0.5">
                Paste your free key into <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">backend/.env</code> as <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">GEMINI_API_KEY=your_key</code> to enable real-time LLM parsing.
              </p>
            </div>
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noreferrer"
              className="inline-flex whitespace-nowrap rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-700 transition"
            >
              Get Free Key &rarr;
            </a>
          </div>
        )}

        {/* ── Test Gemini Form (Drawer) ── */}
        {showExtractForm && (
          <div className="mb-6 bg-white border border-blue-200 rounded-2xl shadow-sm p-6">
            <h2 className="text-base font-bold text-slate-800">Simulate Incoming Email & Extract with Gemini</h2>
            <p className="text-xs text-slate-500 mb-4">
              Enter any raw operations email text. Gemini AI will analyze the message, extract trade parameters, priority, and draft an action recommendation.
            </p>

            {errorMsg && (
              <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleExtractSubmit} className="space-y-4 text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">From / Sender</label>
                  <input
                    type="email"
                    value={emailForm.from}
                    onChange={e => setEmailForm({ ...emailForm, from: e.target.value })}
                    required
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Subject</label>
                  <input
                    type="text"
                    value={emailForm.subject}
                    onChange={e => setEmailForm({ ...emailForm, subject: e.target.value })}
                    required
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Email Body</label>
                <textarea
                  rows={4}
                  value={emailForm.body}
                  onChange={e => setEmailForm({ ...emailForm, body: e.target.value })}
                  required
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-mono focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowExtractForm(false)}
                  className="rounded-lg border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={extracting}
                  className="rounded-lg bg-blue-600 px-5 py-2 text-xs font-semibold text-white hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {extracting ? 'Processing with Gemini...' : 'Run Gemini AI Extraction'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* ── Section Heading & Count ── */}
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-800">Incoming Operations Requests</h1>
            <p className="text-sm text-slate-500 mt-0.5">
              AI-parsed and prioritized requests requiring operational action.
            </p>
          </div>
          <span className="text-xs bg-white border border-slate-200 text-slate-600 px-3 py-1 rounded-full font-medium">
            {requests.length} Requests
          </span>
        </div>

        {/* ── Request Card List ── */}
        <div className="flex flex-col gap-4">
          {requests.map((request) => (
            <RequestCard
              key={request.id}
              request={request}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      </main>
    </div>
  )
}
