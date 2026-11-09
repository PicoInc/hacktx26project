// Car value vs. what's still owed, month by month (NM-23). Owner: Rodrigo.
import {
  Area,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { formatCurrency } from '../format.js'
import './EquityChart.css'

// Same colors as tokens.css (SVG lines need plain color values)
const VALUE_COLOR = '#2D5D8C'   // --color-blue (Cavalry Blue)
const EQUITY_FILL = '#DCE8EE'   // --color-heritage-bg (Heritage Blue)
const PAYOFF_COLOR = '#1C2127'  // --color-ink (Attitude Black)
const TODAY_COLOR = '#EB0A1E'   // --color-red (Toyota red)

function monthLabel(month) {
  return month === 0 ? 'Today' : `In ${month} months`
}

export default function EquityChart({ timeline = [], contractType }) {
  if (timeline.length === 0) return null

  const payoffName = contractType === 'lease' ? 'Residual (buyout price)' : 'Still owed'

  // "gap" holds [bottom, top] so the Area fills the space between the two lines
  const chartData = timeline.map((point) => ({ ...point, gap: [point.payoff, point.value] }))

  return (
    <section className="card equity-chart" aria-label="Car value compared to what you owe over time">
      <h3 className="card-title">Your car's value vs. what you owe</h3>
      <p className="muted equity-chart-note">
        The shaded blue area is your equity: how much your car is worth beyond what you owe.
      </p>

      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={chartData} margin={{ top: 16, right: 24, bottom: 8, left: 8 }}>
          <XAxis dataKey="month" tickFormatter={(month) => `${month} mo`} />
          <YAxis tickFormatter={(amount) => formatCurrency(amount)} width={80} domain={['auto', 'auto']} />
          <Tooltip
            labelFormatter={monthLabel}
            formatter={(amount, name) => [formatCurrency(amount), name]}
          />
          <Legend />

          <Area
            dataKey="gap"
            fill={EQUITY_FILL}
            stroke="none"
            legendType="none"
            tooltipType="none"
            isAnimationActive={false}
          />
          <Line dataKey="value" name="Car value" stroke={VALUE_COLOR} strokeWidth={2} dot={false} />
          <Line dataKey="payoff" name={payoffName} stroke={PAYOFF_COLOR} strokeWidth={2} dot={false} />

          <ReferenceLine x={0} stroke={TODAY_COLOR} label={{ value: 'Today', position: 'top', fill: TODAY_COLOR }} />
        </ComposedChart>
      </ResponsiveContainer>
    </section>
  )
}