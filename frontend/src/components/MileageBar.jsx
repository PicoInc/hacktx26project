import { formatNumber } from '../format.js'

// Projected vs allowed lease miles. The ratios only size the bar; no money involved.
export default function MileageBar({ allowed, projected }) {
  const over = projected > allowed
  const scale = Math.max(allowed, projected)

  return (
    <div className={over ? 'mileage mileage-over' : 'mileage'}>
      <div className="mileage-label">
        <span>Miles at lease end</span>
        <span>
          <strong>{formatNumber(projected)}</strong> / {formatNumber(allowed)} allowed
        </span>
      </div>
      <div
        className="mileage-track"
        role="meter"
        aria-label="Projected lease miles"
        aria-valuemin={0}
        aria-valuemax={scale}
        aria-valuenow={projected}
      >
        <div className="mileage-fill" style={{ width: `${(projected / scale) * 100}%` }} />
        {over && <div className="mileage-limit" style={{ left: `${(allowed / scale) * 100}%` }} />}
      </div>
      {over && <p className="mileage-label"><strong>Over your mileage allowance</strong></p>}
    </div>
  )
}
