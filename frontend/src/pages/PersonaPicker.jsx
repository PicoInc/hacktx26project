import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard, getPersonas } from '../api.js'

export default function PersonaPicker() {
  const [personas, setPersonas] = useState([])

  useEffect(() => {
    let ignore = false
    // personas.json has no vehicle, so pull it from each customer's dashboard
    getPersonas()
      .then((list) =>
        Promise.all(
          list.map(async (p) => {
            const { vehicle } = await getDashboard(p.customer_id)
            return { ...p, vehicleLabel: `${vehicle.year} ${vehicle.model} ${vehicle.trim}` }
          }),
        ),
      )
      .then((list) => {
        if (!ignore) setPersonas(list)
      })
    return () => {
      ignore = true
    }
  }, [])

  return (
    <main className="page">
      <div className="picker-intro">
        <h1>Welcome back</h1>
        <p className="muted">Choose a customer to sign in as.</p>
      </div>
      <div className="grid-3">
        {personas.map((p) => (
          <Link key={p.customer_id} to={`/customer/${p.customer_id}`} className="card persona-card">
            <h2 className="persona-name">{p.name}</h2>
            <span className="persona-vehicle">{p.vehicleLabel}</span>
            <span className="muted">{p.tagline}</span>
            <span className="persona-cta">Sign in →</span>
          </Link>
        ))}
      </div>
    </main>
  )
}
