import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import Toast from './Toast.jsx'
import useDialog from './useDialog.js'

// Fake scheduling: the next few business days at fixed call times
const CALL_HOURS = [10, 13, 16]
const BUSINESS_DAYS = 3

const dayFormat = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
const timeFormat = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

// [{ day: Date, slots: [Date, Date, Date] }] for the business days after `from` (weekends skipped)
export function nextBusinessDays(from, count = BUSINESS_DAYS) {
  const days = []
  const day = new Date(from)
  day.setHours(0, 0, 0, 0)
  while (days.length < count) {
    day.setDate(day.getDate() + 1)
    const weekday = day.getDay()
    if (weekday === 0 || weekday === 6) continue
    const slots = CALL_HOURS.map((hour) => {
      const slot = new Date(day)
      slot.setHours(hour)
      return slot
    })
    days.push({ day: new Date(day), slots })
  }
  return days
}

const HandoffContext = createContext({ openHandoff: () => {} })

// Any component can open the scheduler: const { openHandoff } = useHandoff()
export const useHandoff = () => useContext(HandoffContext)

function Scheduler({ onCancel, onConfirm }) {
  // Computed when the dialog opens, so the dates are always upcoming
  const [days] = useState(() => nextBusinessDays(new Date()))
  const [picked, setPicked] = useState(null)

  return (
    <form
      className="dialog-body"
      onSubmit={(event) => {
        event.preventDefault()
        if (picked) onConfirm(picked)
      }}
    >
      <div className="dialog-head">
        <h2 id="handoff-title">Talk to a TFS specialist</h2>
        <button type="button" className="dialog-close" aria-label="Close" onClick={onCancel}>
          ×
        </button>
      </div>
      <p className="muted">Pick a time and a specialist will call you. No commitment.</p>

      <fieldset className="slot-days">
        <legend className="visually-hidden">Available times</legend>
        {days.map(({ day, slots }) => (
          <div key={day.toISOString()} className="slot-day">
            <span className="slot-day-label">{dayFormat.format(day)}</span>
            <div className="slot-list">
              {slots.map((slot) => {
                const value = slot.toISOString()
                return (
                  <label key={value} className="slot">
                    <input
                      type="radio"
                      name="slot"
                      value={value}
                      checked={picked?.toISOString() === value}
                      onChange={() => setPicked(slot)}
                    />
                    <span>{timeFormat.format(slot)}</span>
                  </label>
                )
              })}
            </div>
          </div>
        ))}
      </fieldset>

      <div className="dialog-actions">
        <button type="button" className="btn btn-outline" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={!picked}>
          Confirm call
        </button>
      </div>
    </form>
  )
}

// Renders the scheduler dialog and its confirmation toast once for the whole app
export function HandoffProvider({ children }) {
  const [open, setOpen] = useState(false)
  const [toast, setToast] = useState(null)
  const openHandoff = useCallback(() => setOpen(true), [])
  const close = useCallback(() => setOpen(false), [])
  const dismissToast = useCallback(() => setToast(null), [])
  const dialogProps = useDialog(open, close)
  const value = useMemo(() => ({ openHandoff }), [openHandoff])

  const confirm = (slot) => {
    setOpen(false)
    setToast(`You're booked: ${dayFormat.format(slot)}, ${timeFormat.format(slot)} — a TFS specialist will call you.`)
  }

  return (
    <HandoffContext.Provider value={value}>
      {children}
      <dialog className="modal" aria-labelledby="handoff-title" {...dialogProps}>
        {/* Mounted only while open, so every visit starts with fresh dates and no pick */}
        {open && <Scheduler onCancel={close} onConfirm={confirm} />}
      </dialog>
      <Toast message={toast} onDismiss={dismissToast} />
    </HandoffContext.Provider>
  )
}

// The persistent header button (App.jsx renders it on every screen)
export function HandoffButton() {
  const { openHandoff } = useHandoff()
  return (
    <button type="button" className="btn btn-outline btn-small" onClick={openHandoff}>
      Talk to a TFS specialist
    </button>
  )
}
