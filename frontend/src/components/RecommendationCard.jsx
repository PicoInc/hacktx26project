import { formatCurrency, formatSignedWholeCurrency } from '../format.js'
import Stat from './Stat.jsx'

// Button look per action kind: self-service = solid red, follow-up = outline, offer = solid black
const KIND_CLASS = {
  self_service: 'btn btn-primary',
  follow_up: 'btn btn-outline',
  offer: 'btn btn-dark',
}

export default function RecommendationCard({ rec, top = false, onAction, onWhyThis }) {
  const { action } = rec
  const isOffer = action.kind === 'offer'
  // Paying the same or less than today is good news; more is a caution, not an error
  const deltaClass = rec.delta_monthly <= 0 ? 'rec-delta delta-good' : 'rec-delta delta-warn'

  return (
    <article className={top ? 'card rec-card rec-card-top' : 'card rec-card'}>
      {top && <div className="ribbon">Best move</div>}

      <div className="rec-main">
        <div className="rec-head">
          <span className="badge">#{rec.rank}</span>
          {isOffer && <span className="badge badge-offer">Offer</span>}
        </div>
        <h3 className="rec-title">{rec.title}</h3>
        <p className="rec-vehicle muted">{rec.vehicle_label}</p>

        <p className="rec-price">
          {formatCurrency(rec.monthly_payment)}
          <span className="rec-per">/mo</span>
        </p>
        <p className={deltaClass}>{formatSignedWholeCurrency(rec.delta_monthly)}/mo vs today</p>

        <dl className="stats rec-stats">
          <Stat label="Upfront" value={formatCurrency(rec.upfront_cost)} />
          <Stat label="Term" value={rec.term_months ? `${rec.term_months} mo` : '—'} />
          <Stat label="Total cost" value={formatCurrency(rec.total_cost)} />
        </dl>
      </div>

      <div className="rec-body">
        <p className="rec-explanation">{rec.explanation}</p>
        <ul className="rec-tradeoffs">
          {rec.tradeoffs.slice(0, 3).map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>

        <div className="rec-actions">
          <button type="button" className={KIND_CLASS[action.kind]} onClick={() => onAction(rec)}>
            {action.label}
          </button>
          <button type="button" className="link-button" onClick={() => onWhyThis?.(rec)}>
            Why this?
          </button>
        </div>
      </div>
    </article>
  )
}
