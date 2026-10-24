import { formatCurrency } from '../format.js'
import Stat from './Stat.jsx'

const SOURCE_LABELS = { mock: 'mock', nessie: 'Nessie' }

export default function FinanceSnapshot({ finances }) {
  return (
    <section className="card">
      <h2 className="card-title">
        Your money
        <span className="tag">Source: {SOURCE_LABELS[finances.source] ?? finances.source}</span>
      </h2>
      <dl className="stats">
        <Stat hero label="Left over each month" value={formatCurrency(finances.monthly_surplus)} />
        <Stat label="Monthly income" value={formatCurrency(finances.monthly_income)} />
        <Stat label="Monthly bills" value={formatCurrency(finances.monthly_bills)} />
        <Stat label="Monthly spending" value={formatCurrency(finances.monthly_spending)} />
        <Stat label="Savings" value={formatCurrency(finances.savings)} />
      </dl>
    </section>
  )
}
