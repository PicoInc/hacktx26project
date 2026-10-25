import { useState } from 'react'
import { Link } from 'react-router-dom'
import '../styles/landing.css'

const REPO_URL = 'https://github.com/PicoInc/hacktx26project'

// Figures come from the engine's verified runs on the synthetic demo data (see the backlog's demo table).
// Only the pick and blocked options carry a figure: it's the one the customer acts on or the one that was ruled out.
const TRIPS = [
  {
    id: 'p1',
    who: 'Maya',
    start: 'Maya’s Corolla',
    situation: 'Lease ends in 4 months, 5,100 miles over the limit',
    lanes: [
      {
        status: 'pick',
        name: 'Buy out the Corolla',
        figure: '$294/mo',
        note: 'Avoids the $1,275 over-mileage fee',
      },
      {
        status: 'considered',
        name: 'Lease a 2027 Corolla',
        note: '$1,160 upfront to prepay your extra miles',
      },
      {
        status: 'considered',
        name: 'Return it and walk away',
        note: 'You’d give up about $4,300 in equity',
      },
    ],
  },
  {
    id: 'p2',
    who: 'The Reyes family',
    start: 'The Reyes’ RAV4',
    situation: 'Baby on the way, 38 months left on the loan',
    lanes: [
      {
        status: 'pick',
        name: 'Keep the RAV4',
        figure: '$565/mo',
        note: 'Your payment stays the same',
      },
      {
        status: 'blocked',
        name: 'Trade up to a Highlander',
        figure: '$797/mo',
        note: 'Adds $233 a month, over your $200 limit',
      },
      {
        status: 'blocked',
        name: 'Refinance',
        note: 'Your 4.9% rate is already below today’s 6.4%',
      },
    ],
  },
  {
    id: 'p3',
    who: 'Daniel',
    start: 'Daniel’s Camry',
    situation: 'High-rate loan, with more than you owe in equity',
    lanes: [
      {
        status: 'pick',
        name: 'Trade in for a Camry Hybrid',
        figure: '$465/mo',
        note: 'Puts about $8,400 of your equity to work',
      },
      {
        status: 'considered',
        name: 'Refinance',
        note: 'Same car, lower rate',
      },
    ],
  },
]

const STATUS_LABEL = { pick: 'Best move', considered: 'Considered', blocked: 'Blocked' }

const STEPS = [
  {
    title: 'We price every option',
    body: 'Buyout, refinance, trade-in, or keep: each one gets real numbers from a tested finance engine.',
  },
  {
    title: 'Guardrails keep only what you can afford',
    body: 'Options that don’t fit your budget are filtered out, and we show you why.',
  },
  {
    title: 'AI explains it, but never changes the numbers',
    body: 'You get a plain-English why. The math stays the engine’s.',
  },
]

const FEATURES = [
  {
    title: 'Lease and loan advisor',
    body: 'Compares every option and ranks the top 3.',
  },
  {
    title: '“What if?” simulator',
    body: 'New baby, income drop, or longer commute: the best move updates.',
  },
  {
    title: 'Equity tracker',
    body: 'Shows when your car is worth more than you owe.',
  },
  {
    title: 'Human handoff',
    body: 'Talk to a TFS specialist from any screen.',
  },
]

const LANE_H = 104 // px; keep in sync with --lane-h in landing.css

function RouteBoard() {
  const [tripId, setTripId] = useState(TRIPS[0].id)
  const trip = TRIPS.find((t) => t.id === tripId)
  const height = trip.lanes.length * LANE_H
  const mid = height / 2

  return (
    <div className="board">
      <div className="landing-inner">
        <div className="board-people" role="group" aria-label="Demo customers">
          {TRIPS.map((t) => (
            <button
              key={t.id}
              type="button"
              className="board-person"
              aria-pressed={t.id === tripId}
              onClick={() => setTripId(t.id)}
            >
              {t.who}
            </button>
          ))}
        </div>

        {/* key restarts the road-drawing animation for each customer */}
        <div className="route" key={trip.id} aria-live="polite">
          <div className="route-start">
            <p className="route-start-name">{trip.start}</p>
            <p className="route-start-note">{trip.situation}</p>
          </div>

          <svg
            className="route-roads"
            style={{ height }}
            viewBox={`0 0 100 ${height}`}
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            {trip.lanes.map((lane, i) => {
              const y = i * LANE_H + LANE_H / 2
              const d = `M0,${mid} C55,${mid} 45,${y} 100,${y}`
              const live = lane.status === 'pick'
              return (
                <g key={lane.name}>
                  <path
                    className={live ? 'road road-pick' : 'road'}
                    d={d}
                    vectorEffect="non-scaling-stroke"
                  />
                  <path className="road-line" d={d} vectorEffect="non-scaling-stroke" />
                </g>
              )
            })}
          </svg>

          <ul className="route-lanes">
            {trip.lanes.map((lane) => (
              <li key={lane.name} className={`lane lane-${lane.status}`}>
                <span className="lane-cap" aria-hidden="true" />
                <div className="lane-text">
                  <p className="lane-name">
                    {lane.name}
                    <span className="lane-status">{STATUS_LABEL[lane.status]}</span>
                  </p>
                  <p className="lane-note">{lane.note}</p>
                </div>
                {lane.figure && <p className="lane-figure">{lane.figure}</p>}
              </li>
            ))}
          </ul>
        </div>
        <p className="board-foot">Demo customers with synthetic data. Pick one to see their route.</p>
      </div>
    </div>
  )
}

export default function Landing() {
  return (
    <div className="landing">
      <section className="landing-hero" aria-labelledby="landing-title">
        <div className="landing-inner landing-hero-copy">
          <h1 id="landing-title">Every way forward, priced. NexMove picks the one you can afford.</h1>
          <div className="landing-hero-side">
            <p className="landing-lede">
              For your Toyota lease or loan: buy out, refinance, trade in, or keep. You get one
              recommendation with real numbers and a plain-English reason.
            </p>
            <Link to="/customers" className="btn btn-primary landing-cta">
              Try a demo customer
            </Link>
          </div>
        </div>
        <RouteBoard />
      </section>

      <section className="landing-inner landing-section" aria-labelledby="how-title">
        <h2 id="how-title">How it works</h2>
        <ol className="landing-steps">
          {STEPS.map((s) => (
            <li key={s.title} className="landing-step">
              <h3>{s.title}</h3>
              <p className="muted">{s.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing-inner landing-section landing-split" aria-labelledby="features-title">
        <h2 id="features-title">What you get</h2>
        <ul className="landing-features">
          {FEATURES.map((f) => (
            <li key={f.title} className="landing-feature">
              <h3>{f.title}</h3>
              <p className="muted">{f.body}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="landing-ai" aria-labelledby="ai-title">
        <div className="landing-inner landing-ai-grid">
          <div>
            <h2 id="ai-title">The engine decides. The AI explains.</h2>
            <p>
              Every number the AI writes is checked against the engine. If one doesn’t match, we show a
              standard explanation instead.
            </p>
          </div>
          <dl className="check">
            <div className="check-row">
              <dt>AI wrote</dt>
              <dd>“Buying out your Corolla keeps your payment at $294.34/mo.”</dd>
              <dd className="check-ok">The engine priced the buyout at $294.34, so this explanation is shown.</dd>
            </div>
            <div className="check-row">
              <dt>AI wrote</dt>
              <dd>“You’ll also skip a $1,500 over-mileage fee.”</dd>
              <dd className="check-bad">
                The engine says the fee is $1,275. The AI’s sentence is dropped and a standard
                explanation is shown instead.
              </dd>
            </div>
          </dl>
        </div>
      </section>

      <footer className="landing-inner landing-footer">
        <p>Built at HackTX 2026 with synthetic demo data.</p>
        <a href={REPO_URL} target="_blank" rel="noreferrer">
          View on GitHub
        </a>
      </footer>
    </div>
  )
}
