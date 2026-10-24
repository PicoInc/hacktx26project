import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPersonas } from '../api.js'

export default function PersonaPicker() {
  const [personas, setPersonas] = useState([])

  useEffect(() => {
    getPersonas().then(setPersonas)
  }, [])

  return (
    <main>
      <h1>Who are you?</h1>
      <ul>
        {personas.map((p) => (
          <li key={p.customer_id}>
            <Link to={`/customer/${p.customer_id}`}>{p.name}</Link> · {p.tagline}
          </li>
        ))}
      </ul>
    </main>
  )
}
