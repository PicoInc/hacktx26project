import { Link } from 'react-router-dom'
import '../styles/landing.css'

const REPO_URL = 'https://github.com/PicoInc/hacktx26project'

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
    title: 'Lease & loan advisor',
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

export default function Landing() {
  return (
    <div className="landing">
      <section className="landing-hero" aria-labelledby="landing-title">
        <div className="landing-logo-band">
          <img className="landing-logo" src="/nexmove-logo.png" alt="NexMove" />
        </div>
        <div className="landing-inner landing-hero-copy">
          <h1 id="landing-title">Your smartest next move with your Toyota</h1>
          <p className="landing-lede">
            Buyout, refinance, trade-in, or keep, with real numbers, a plain-English why, and only
            options you can afford.
          </p>
          <Link to="/customers" className="btn btn-primary landing-cta">
            See it in action
          </Link>
        </div>
      </section>

      <section className="landing-inner landing-section" aria-labelledby="how-title">
        <h2 id="how-title">How it works</h2>
        <ol className="landing-steps">
          {STEPS.map((s, i) => (
            <li key={s.title} className="landing-step">
              <span className="landing-step-num" aria-hidden="true">
                {i + 1}
              </span>
              <h3>{s.title}</h3>
              <p className="muted">{s.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing-inner landing-section" aria-labelledby="features-title">
        <h2 id="features-title">What you get</h2>
        <ul className="landing-features">
          {FEATURES.map((f) => (
            <li key={f.title} className="card landing-feature">
              <h3>{f.title}</h3>
              <p className="muted">{f.body}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="landing-ai" aria-labelledby="ai-title">
        <div className="landing-inner">
          <p className="landing-kicker">Responsible AI</p>
          <h2 id="ai-title">The engine decides, the AI explains.</h2>
          <p>
            Every number the AI writes is checked against the engine; if one doesn’t match, we show a
            standard explanation instead.
          </p>
        </div>
      </section>

      <footer className="landing-inner landing-footer">
        <p>Built at HackTX 2026 · Synthetic demo data</p>
        <a href={REPO_URL} target="_blank" rel="noreferrer">
          View on GitHub
        </a>
      </footer>
    </div>
  )
}
