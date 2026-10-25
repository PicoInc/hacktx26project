import { formatSignedCurrency } from '../format.js'

export default function EquityBadge({ equity }) {
  const positive = equity.status === 'positive'

  return (
    <div className={positive ? 'equity-badge equity-positive' : 'equity-badge equity-negative'}>
      {formatSignedCurrency(equity.value)} equity
    </div>
  )
}
