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

const LOAN = 'Monthly payment = standard loan payment: P = r × PV ÷ (1 − (1 + r)^−n), where r = APR ÷ 12, PV = amount financed and n = term in months.'
const LEASE = 'Monthly payment = depreciation + finance charge: (cap cost − residual) ÷ n + (cap cost + residual) × money factor.'

// "How we calculated this", by option kind (static text from the plan, §5)
const HOW = {
  lease_buyout: `${LOAN} The amount financed is the residual plus the purchase option fee.`,
  refinance: `${LOAN} The amount financed is today's payoff at the new APR.`,
  trade_in_upgrade: `${LOAN} The amount financed is the new car's price minus your equity.`,
  extend_term: `${LOAN} Your payoff is spread over the remaining months plus the extension.`,
  return_new_lease: `${LEASE} Upfront = over-mileage fee + disposition fee.`,
  buy_miles_new_lease: `${LEASE} Upfront = prepaid extra miles + disposition fee.`,
  return_walk_away: 'No new payment. Upfront = over-mileage fee + disposition fee.',
  keep: 'Your current payment, unchanged, until the loan is paid off.',
  payment_deferral: '$0 for the deferred months, then your current payment; the skipped months are added to the end. It is ranked on its average monthly cost over the first year.',
  talk_to_advisor: 'Nothing is calculated here: a specialist reviews your situation with you.',
  recall_service: 'Nothing to pay: safety recall repairs are free at any Toyota dealer.',
}

// Kinds where the payment + fuel + upfront line doesn't apply (deferral averages its first year)
const NO_EFFECTIVE_LINE = new Set(['payment_deferral', 'talk_to_advisor', 'recall_service'])

// Live options carry `kind`; the hand-written sample JSON only has the id ("kind:target")
const kindOf = (option) => option.kind ?? option.id.split(':')[0]

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

function Calculation({ option }) {
  const kind = kindOf(option)
  const showEffective = !NO_EFFECTIVE_LINE.has(kind)
  return (
    <>
      {HOW[kind] && <p>{HOW[kind]}</p>}
      {showEffective && (
        <p className="calc-line">
          Effective monthly = {formatCurrency(option.monthly_payment)} payment + {formatCurrency(option.fuel_monthly)} fuel
          + {formatCurrency(option.upfront_cost)} upfront ÷ 12 = <strong>{formatCurrency(option.effective_monthly)}</strong>
        </p>
      )}
    </>
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

          <section className="drawer-section">
            <h3>How we calculated this</h3>
            <Calculation option={option} />
          </section>

          <p className="drawer-footer">Calculated by our finance engine · explained by AI · AI cannot change numbers</p>
        </div>
      )}
    </dialog>
  )
}
