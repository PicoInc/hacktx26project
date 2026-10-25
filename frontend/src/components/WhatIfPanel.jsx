import { useEffect, useRef, useState } from 'react'
import '../styles/whatif.css'

// Line pictograms on a 24px grid, drawn in currentColor so they follow the chip's state
const ICONS = {
  // Pram: bowl, hood, two wheels (no handle, which reads as a shopping cart)
  new_baby: (
    <>
      <path d="M4 11a7.5 5.5 0 0 0 15 0Z" />
      <path d="M11.5 11V3.5a7.5 7.5 0 0 1 7.5 7.5" />
      <circle cx="8" cy="20" r="2" />
      <circle cx="15" cy="20" r="2" />
    </>
  ),
  // Falling trend line
  income_drop: (
    <>
      <path d="m3 7 6 6 4-4 8 8" />
      <path d="M21 11v6h-6" />
    </>
  ),
  // A winding route from start to destination
  longer_commute: (
    <>
      <circle cx="5" cy="19" r="2" />
      <path d="M7 19h6a3 3 0 0 0 0-6h-2a3 3 0 0 1 0-6h6" />
      <circle cx="19" cy="7" r="2" />
    </>
  ),
}

// Event types must match backend/engine/events.py ALLOWED_EVENTS
const EVENTS = [
  { type: 'new_baby', label: 'New baby' },
  { type: 'income_drop', label: 'Income drop' },
  { type: 'longer_commute', label: 'Longer commute' },
]

const PCT_MIN = 10
const PCT_MAX = 40
const PCT_DEFAULT = 20
// Each change re-calls the API (and the LLM), so the slider waits until the user stops dragging
const DEBOUNCE_MS = 300

/**
 * Controlled by Dashboard: `value` is the current life event ({ type, params } or null),
 * `onChange` sets it (which re-fetches recommendations), and `summary` is the API's
 * `life_event_applied` line (null while a request is in flight).
 */
export default function WhatIfPanel({ value, onChange, summary }) {
  const active = value?.type ?? null
  const [pct, setPct] = useState(value?.params?.pct ?? PCT_DEFAULT)
  const timer = useRef(null)

  // Keep the slider in sync when the event is cleared or set from outside
  useEffect(() => {
    if (value?.type === 'income_drop' && typeof value.params?.pct === 'number') setPct(value.params.pct)
    if (!value) setPct(PCT_DEFAULT)
  }, [value])

  // Never fire a stale debounced update after unmount
  useEffect(() => () => clearTimeout(timer.current), [])

  function select(type) {
    clearTimeout(timer.current)
    if (type === active) return onChange(null) // clicking the active chip turns it off
    if (type === 'income_drop') {
      setPct(PCT_DEFAULT)
      return onChange({ type, params: { pct: PCT_DEFAULT } })
    }
    onChange({ type, params: {} }) // engine applies its own defaults
  }

  function slide(next) {
    setPct(next)
    clearTimeout(timer.current)
    timer.current = setTimeout(() => onChange({ type: 'income_drop', params: { pct: next } }), DEBOUNCE_MS)
  }

  function reset() {
    clearTimeout(timer.current)
    onChange(null)
  }

  return (
    <div className="whatif">
      <div className="whatif-row">
        <span className="whatif-label">What if…</span>
        <div className="whatif-chips" role="group" aria-label="Try a life change">
          {EVENTS.map((e) => (
            <button
              key={e.type}
              type="button"
              className={`whatif-chip${active === e.type ? ' is-active' : ''}`}
              aria-pressed={active === e.type}
              onClick={() => select(e.type)}
            >
              <svg className="whatif-icon" viewBox="0 0 24 24" aria-hidden="true">
                {ICONS[e.type]}
              </svg>
              {e.label}
            </button>
          ))}
        </div>
        {active && (
          <button type="button" className="link-button whatif-reset" onClick={reset}>
            Reset
          </button>
        )}
      </div>

      {active === 'income_drop' && (
        <label className="whatif-slider">
          <span>
            Income drops by <strong>{pct}%</strong>
          </span>
          <input
            type="range"
            min={PCT_MIN}
            max={PCT_MAX}
            step={5}
            value={pct}
            onChange={(e) => slide(Number(e.target.value))}
          />
        </label>
      )}

      {active && summary && (
        <p className="whatif-banner" role="status">
          {summary}
        </p>
      )}
    </div>
  )
}