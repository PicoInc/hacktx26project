import { formatCurrency, formatNumber } from '../format.js'
import Stat from './Stat.jsx'

export default function VehicleCard({ vehicle }) {
  return (
    <section className="card">
      <h2 className="card-title">Your car</h2>
      <p className="card-headline">
        {vehicle.year} {vehicle.model} {vehicle.trim}
      </p>
      <dl className="stats">
        <Stat label="Mileage" value={`${formatNumber(vehicle.mileage)} mi`} />
        <Stat label="Estimated value" value={formatCurrency(vehicle.est_value)} />
      </dl>
    </section>
  )
}
