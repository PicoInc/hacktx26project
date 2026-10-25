import { formatCurrency, formatNumber, formatPercent } from '../format.js'
import Stat from './Stat.jsx'
import useDialog from './useDialog.js'

const months = (n) => `${n} ${n === 1 ? 'month' : 'months'}`
const perMile = (n) => `${formatCurrency(n)} per mile`
const miles = (n) => `${formatNumber(n)} mi`

// How to label and format each key the engine puts in option.assumptions (engine/options.py).
// A new engine key still renders through the fallback below; add it here to give it a proper label.
const ASSUMPTIONS = {
  apr: { label: 'APR', format: formatPercent },
  previous_apr: { label: 'Current APR', format: formatPercent },
  term_months: { label: 'Term', format: months },
  extension_months: { label: 'Months added', format: months },
  deferral_months: { label: 'Months deferred', format: months },
  residual: { label: 'Residual value', format: formatCurrency },
  purchase_option_fee: { label: 'Purchase option fee', format: formatCurrency },
  disposition_fee: { label: 'Disposition fee', format: formatCurrency },
  fees: { label: 'Fees', format: formatCurrency },
  msrp: { label: 'MSRP', format: formatCurrency },
  trade_in_value: { label: 'Trade-in value', format: formatCurrency },
  payoff: { label: 'Payoff today', format: formatCurrency },
  money_factor: { label: 'Money factor', format: String },
  overage_rate: { label: 'Over-mileage rate', format: perMile },
  prepaid_miles_rate: { label: 'Prepaid miles rate', format: perMile },
  extra_miles: { label: 'Extra miles', format: miles },
  projected_miles: { label: 'Projected miles at lease end', format: miles },
  source: { label: 'Data', format: (v) => (v === 'synthetic' ? 'Synthetic demo data' : v) },
}

const humanize = (key) => key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')

function Assumptions({ assumptions = {} }) {
  const entries = Object.entries(assumptions)
  if (entries.every(([key]) => key === 'source')) {
    return <p className="muted">No calculation; this is a conversation with a specialist.</p>
  }
  return (
    <dl className="stats">
      {entries.map(([key, value]) => {
        const spec = ASSUMPTIONS[key]
        const shown = spec ? spec.format(value) : typeof value === 'number' ? formatNumber(value) : String(value)
        return <Stat key={key} label={spec?.label ?? humanize(key)} value={shown} />
      })}
    </dl>
  )
}

export default function WhyDrawer({ option, onClose }) {
  const dialogProps = useDialog(Boolean(option), onClose)

  return (
    <dialog className="drawer" aria-labelledby="why-title" {...dialogProps}>
      {option && (
        <div className="dialog-body">
          <div className="dialog-head">
            <div>
              <p className="drawer-kicker">#{option.rank} · Why this?</p>
              <h2 id="why-title">{option.title}</h2>
              {option.vehicle_label && <p className="muted drawer-vehicle">{option.vehicle_label}</p>}
            </div>
            <button type="button" className="dialog-close" aria-label="Close" onClick={onClose}>
              ×
            </button>
          </div>

          <section className="drawer-section">
            <h3>Why this option</h3>
            <p>{option.explanation}</p>
            <p className="drawer-source">
              {option.explanation_source === 'llm' ? 'Explained by AI · numbers checked' : 'Standard explanation'}
            </p>
          </section>

          <section className="drawer-section">
            <h3>What we assumed</h3>
            <Assumptions assumptions={option.assumptions} />
          </section>

          <p className="drawer-footer">Calculated by our finance engine · explained by AI · AI cannot change numbers</p>
        </div>
      )}
    </dialog>
  )
}
