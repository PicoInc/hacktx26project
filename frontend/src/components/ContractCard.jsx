import { formatCurrency, formatPercent } from '../format.js'
import MileageBar from './MileageBar.jsx'
import Stat from './Stat.jsx'

export default function ContractCard({ contract }) {
  const isLease = contract.type === 'lease'

  return (
    <section className="card">
      <h2 className="card-title">
        Your contract
        <span className={isLease ? 'badge badge-lease' : 'badge'}>{contract.type}</span>
      </h2>
      <dl className="stats">
        <Stat hero label="Monthly payment" value={formatCurrency(contract.monthly_payment)} />
        <Stat label="Months remaining" value={contract.months_remaining} />
        <Stat label="APR" value={formatPercent(contract.apr)} />
      </dl>
      {isLease && (
        <MileageBar allowed={contract.miles_allowed_total} projected={contract.miles_projected_at_end} />
      )}
    </section>
  )
}
