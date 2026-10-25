import { useCallback, useState } from 'react'
import RecommendationCard from './RecommendationCard.jsx'
import Toast from './Toast.jsx'

// Used only if the API hasn't sent action.confirmation yet (see contract.md)
const fallbackConfirmation = (action) =>
  `${action.label} — a TFS specialist will follow up within 1 business day`

export default function RecommendationList({ recommendations, considered, onWhyThis }) {
  const [toast, setToast] = useState(null)
  const dismissToast = useCallback(() => setToast(null), [])

  const top3 = [...recommendations].sort((a, b) => a.rank - b.rank).slice(0, 3)
  const shownIds = new Set(top3.map((r) => r.id))
  const others = considered.filter((o) => !shownIds.has(o.id)).length

  const handleAction = (rec) => setToast(rec.action.confirmation ?? fallbackConfirmation(rec.action))

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
