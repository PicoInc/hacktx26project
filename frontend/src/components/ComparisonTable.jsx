// All options the engine considered, including rejected ones and why (NM-22). Owner: Rodrigo.
import { formatCurrency, formatSignedCurrency } from '../format.js'
import './ComparisonTable.css'

function sortByRank(options) {
  return [...options].sort((a, b) => {
    if (a.rank == null && b.rank == null) return 0
    if (a.rank == null) return 1
    if (b.rank == null) return -1
    return a.rank - b.rank
  })
}

export default function ComparisonTable({ considered = [] }) {
  if (considered.length === 0) return null
  const options = sortByRank(considered)

  return (
    <section className="card comparison" aria-label="All options we considered">
      <h3 className="card-title">All options we considered ({options.length})</h3>

      <div className="comparison-scroll">
        <table className="comparison-table">
          <thead>
            <tr>
            <th scope="col">Option</th>
            <th scope="col">Monthly payment</th>
            <th scope="col">Change per month</th>
            <th scope="col">Due upfront</th>
            <th scope="col">Total cost</th>
            <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {options.map((option) => (
              <tr key={option.id} className={option.affordable ? '' : 'is-rejected'}>
                <td>{option.title}</td>
                <td>{formatCurrency(option.monthly_payment)}</td>
                <td>{formatSignedCurrency(option.delta_monthly)}</td>
                <td>{formatCurrency(option.upfront_cost)}</td>
                <td>{formatCurrency(option.total_cost)}</td>
                <td>
                  {option.affordable ? (
                    <span className="status status-ok">Affordable</span>
                  ) : (
                    <>
                      <span className="status status-rejected">Not recommended</span>
                      <div className="status-reason">{option.rejection_reason}</div>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}