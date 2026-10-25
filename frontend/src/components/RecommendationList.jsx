import { useCallback, useState } from 'react'
import { useHandoff } from './HumanHandoff.jsx'
import RecommendationCard from './RecommendationCard.jsx'
import Toast from './Toast.jsx'

// Used only if the API hasn't sent action.confirmation yet (see contract.md)
const fallbackConfirmation = (action) =>
  `${action.label} — a TFS specialist will follow up within 1 business day`

// follow_up actions mean "a TFS specialist takes it from here", except a recall repair (NM-27),
// which is booked with a dealer, not a TFS call. Sample JSON has no `kind`, so fall back to the id.
const NOT_A_TFS_CALL = new Set(['recall_service'])
const opensScheduler = (rec) =>
  rec.action.kind === 'follow_up' && !NOT_A_TFS_CALL.has(rec.kind ?? rec.id.split(':')[0])

export default function RecommendationList({ recommendations, considered, onWhyThis }) {
  const [toast, setToast] = useState(null)
  const dismissToast = useCallback(() => setToast(null), [])

  const top3 = [...recommendations].sort((a, b) => a.rank - b.rank).slice(0, 3)
  const shownIds = new Set(top3.map((r) => r.id))
  const others = considered.filter((o) => !shownIds.has(o.id)).length

  const { openHandoff } = useHandoff()

  // "Talk to a specialist"-type actions open the same scheduler as the header button
  const handleAction = (rec) => {
    if (opensScheduler(rec)) openHandoff()
    else setToast(rec.action.confirmation ?? fallbackConfirmation(rec.action))
  }

  return (
    <>
      <div className="rec-list">
        {top3.map((rec, i) => (
          <RecommendationCard key={rec.id} rec={rec} top={i === 0} onAction={handleAction} onWhyThis={onWhyThis} />
        ))}
      </div>
      {others > 0 && (
        <a href="#all-options" className="considered-note">
          We also considered {others} other {others === 1 ? 'option' : 'options'}
        </a>
      )}
      <Toast message={toast} onDismiss={dismissToast} />
    </>
  )
}
