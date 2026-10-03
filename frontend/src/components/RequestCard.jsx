import { useState } from 'react'

/**
 * RequestCard — displays a single operations request extracted from an email.
 *
 * Props:
 *   request  (object)  — one item from the sampleRequests array (or API response)
 *
 * Concepts demonstrated here:
 *   - Props: data flows in from the parent (App.jsx) via the `request` prop
 *   - Destructuring: we pull out individual fields at the top
 *   - Conditional styling: priority badge changes colour based on value
 *   - useState: we track whether the card is pending/approved/rejected locally
 *   - Derived values: confidence percentage is computed from the raw 0–1 number
 */
export default function RequestCard({ request, onStatusChange }) {
  // ── Destructure all fields from the request prop ──────────────────────────
  const {
    id,
    received_at,
    from,
    subject,
    client,
    currency,
    trade_id,
    intent,
    priority,
    confidence,
    summary,
    recommended_action,
    status: initialStatus,   // rename to avoid shadowing the state variable
  } = request

  // ── Local state: track approve / reject actions ───────────────────────────
  const [status, setStatus] = useState(initialStatus)

  const handleStatusChange = (newStatus) => {
    setStatus(newStatus)
    onStatusChange?.(id, newStatus)
  }

  // ── Derived values ────────────────────────────────────────────────────────
  const confidencePct = Math.round(confidence * 100) // e.g. 0.91 → 91

  // Format the ISO timestamp into a readable local string
  const receivedDate = new Date(received_at).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })

  // ── Helper: map intent to a readable label ────────────────────────────────
  const intentLabel = {
    settlement_query:   'Settlement Query',
    rate_confirmation:  'Rate Confirmation',
    new_trade_request:  'New Trade Request',
    statement_request:  'Statement Request',
    dispute:            'Dispute',
  }[intent] ?? intent   // fallback: show the raw string if unrecognised

  // ── Helper: priority → Tailwind badge classes ─────────────────────────────
  // This is the "conditional styling" concept in action
  const priorityBadge = {
    high:   'bg-red-100 text-red-700 ring-red-600/20',
    medium: 'bg-amber-100 text-amber-700 ring-amber-600/20',
    low:    'bg-green-100 text-green-700 ring-green-600/20',
  }[priority] ?? 'bg-gray-100 text-gray-700 ring-gray-600/20'

  // ── Helper: status → card border colour ──────────────────────────────────
  const statusBorder = {
    pending:  'border-l-slate-400',
    approved: 'border-l-emerald-500',
    rejected: 'border-l-rose-500',
  }[status] ?? 'border-l-slate-400'

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-slate-200 border-l-4 ${statusBorder} p-5 flex flex-col gap-4`}>

      {/* ── Row 1: Header — subject, ID, timestamp ── */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-1">
        <div>
          <p className="text-xs text-slate-400 font-mono">{id}</p>
          <h3 className="text-base font-semibold text-slate-800 leading-snug">{subject}</h3>
          <p className="text-xs text-slate-500 mt-0.5">From: {from}</p>
        </div>
        <p className="text-xs text-slate-400 whitespace-nowrap">{receivedDate}</p>
      </div>

      {/* ── Row 2: Tags — priority, intent ── */}
      <div className="flex flex-wrap gap-2">
        {/* Priority badge */}
        <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${priorityBadge}`}>
          {priority.toUpperCase()} PRIORITY
        </span>
        {/* Intent tag */}
        <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-600/20">
          {intentLabel}
        </span>
        {/* Status tag */}
        <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
          status === 'approved' ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' :
          status === 'rejected' ? 'bg-rose-50 text-rose-700 ring-rose-600/20' :
                                  'bg-slate-100 text-slate-600 ring-slate-400/20'
        }`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* ── Row 3: Key fields — client, currency, trade ID ── */}
      <div className="grid grid-cols-3 gap-3 text-sm">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">Client</p>
          <p className="font-medium text-slate-700">{client}</p>
        </div>
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">Currency</p>
          <p className="font-medium text-slate-700">{currency ?? '—'}</p>
        </div>
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">Trade ID</p>
          <p className="font-medium text-slate-700 font-mono text-xs">{trade_id ?? '—'}</p>
        </div>
      </div>

      {/* ── Row 4: AI Summary ── */}
      <div className="bg-slate-50 rounded-lg p-3 text-sm text-slate-700">
        <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">AI Summary</p>
        {summary}
      </div>

      {/* ── Row 5: Recommended action ── */}
      <div className="text-sm">
        <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Recommended Action</p>
        <p className="text-slate-700">{recommended_action}</p>
      </div>

      {/* ── Row 6: Confidence bar ── */}
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">
          AI Confidence — {confidencePct}%
        </p>
        <div className="w-full bg-slate-200 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full ${
              confidence >= 0.85 ? 'bg-emerald-500' :
              confidence >= 0.65 ? 'bg-amber-400' : 'bg-rose-400'
            }`}
            style={{ width: `${confidencePct}%` }}
          />
        </div>
      </div>

      {/* ── Row 7: Action buttons (only shown when pending) ── */}
      {status === 'pending' && (
        <div className="flex gap-3 pt-1">
          <button
            onClick={() => handleStatusChange('approved')}
            className="flex-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors"
          >
            ✓ Approve
          </button>
          <button
            onClick={() => handleStatusChange('rejected')}
            className="flex-1 rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 transition-colors"
          >
            ✕ Reject
          </button>
        </div>
      )}

      {/* ── Resolved message ── */}
      {status !== 'pending' && (
        <div className={`text-center text-sm font-medium py-2 rounded-lg ${
          status === 'approved' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
        }`}>
          {status === 'approved' ? '✓ Action approved' : '✕ Request rejected'}
          {' '}
          <button
            onClick={() => handleStatusChange('pending')}
            className="underline text-xs font-normal opacity-70 hover:opacity-100"
          >
            undo
          </button>
        </div>
      )}
    </div>
  )
}
