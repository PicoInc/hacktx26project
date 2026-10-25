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
        <h1>Choose a customer</h1>
        <p className="muted">Each one is a demo customer with synthetic data. Open one to see their dashboard.</p>
      </div>
      {!result && <p className="muted">Loading customers…</p>}
      {result?.error && <ErrorState title="Couldn't load customers" onRetry={retry} />}
      {result?.list && (
        <ul className="persona-list">
          {result.list.map((p) => (
            <li key={p.customer_id}>
              <Link to={`/customer/${p.customer_id}`} className="persona-row">
                <h2 className="persona-name">{p.name}</h2>
                <span>
                  <span className="persona-vehicle">{p.vehicleLabel}</span>
                  {/* Taglines arrive as "A · B · C"; read them as a sentence */}
                  <span className="persona-tagline">{p.tagline.split(' · ').join(', ')}</span>
                </span>
                <span className="persona-cta">Open dashboard</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
