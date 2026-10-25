import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard, getPersonas } from '../api.js'
import ErrorState from '../components/ErrorState.jsx'

export default function PersonaPicker() {
  // null while loading, { list } or { error } once done
  const [result, setResult] = useState(null)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let ignore = false
    // /personas has no vehicle, so pull it from each customer's dashboard
    getPersonas()
      .then((list) =>
        Promise.all(
          list.map(async (p) => {
            const { vehicle } = await getDashboard(p.customer_id)
            return { ...p, vehicleLabel: `${vehicle.year} ${vehicle.model} ${vehicle.trim}` }
          }),
        ),
      )
      .then((list) => !ignore && setResult({ list }))
      .catch((error) => !ignore && setResult({ error }))
    return () => {
      ignore = true
    }
  }, [attempt])

  const retry = () => {
    setResult(null)
    setAttempt((n) => n + 1)
  }

  return (
    <main className="page">
      <div className="picker-intro">
        <h1>Welcome back</h1>
        <p className="muted">Choose a customer to sign in as.</p>
      </div>
      {!result && <p className="muted">Loading customers…</p>}
      {result?.error && <ErrorState title="Couldn't load customers" onRetry={retry} />}
      {result?.list && (
        <div className="grid-3">
          {result.list.map((p) => (
            <Link key={p.customer_id} to={`/customer/${p.customer_id}`} className="card persona-card">
              <h2 className="persona-name">{p.name}</h2>
              <span className="persona-vehicle">{p.vehicleLabel}</span>
              <span className="muted">{p.tagline}</span>
              <span className="persona-cta">Sign in →</span>
            </Link>
          ))}
        </div>
      )}
    </main>
  )
}
