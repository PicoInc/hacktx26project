import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getDashboard, getRecommendations } from '../api.js'
import ComparisonTable from '../components/ComparisonTable.jsx'
import ContractCard from '../components/ContractCard.jsx'
import EquityBadge from '../components/EquityBadge.jsx'
import EquityChart from '../components/EquityChart.jsx'
import ErrorState from '../components/ErrorState.jsx'
import FinanceSnapshot from '../components/FinanceSnapshot.jsx'
import RecommendationList from '../components/RecommendationList.jsx'
import RecommendationSkeleton from '../components/RecommendationSkeleton.jsx'
import VehicleCard from '../components/VehicleCard.jsx'
import WhatIfPanel from '../components/WhatIfPanel.jsx'
import WhyDrawer from '../components/WhyDrawer.jsx'

// Identifies one recommendations request, so a slow response for an old request is never shown
const recsKey = (id, lifeEvent, attempt) => `${id}|${JSON.stringify(lifeEvent)}|${attempt}`

export default function Dashboard() {
  const { id } = useParams()
  // Results are tagged with the request they belong to, so switching customers never shows stale data
  const [dashboard, setDashboard] = useState(null)
  const [recs, setRecs] = useState(null)
  const [lifeEvent, setLifeEvent] = useState(null)
  // Bumped by the Retry buttons to re-run a request
  const [dashboardAttempt, setDashboardAttempt] = useState(0)
  const [recsAttempt, setRecsAttempt] = useState(0)
  // The card whose "Why this?" drawer is open, by id (looked up in the current response below)
  const [whyId, setWhyId] = useState(null)

  useEffect(() => {
    let ignore = false
    getDashboard(id)
      .then((data) => !ignore && setDashboard({ id, data }))
      .catch((error) => !ignore && setDashboard({ id, error }))
    return () => {
      ignore = true
    }
  }, [id, dashboardAttempt])

  useEffect(() => {
    let ignore = false
    const key = recsKey(id, lifeEvent, recsAttempt)
    getRecommendations(id, lifeEvent)
      .then((data) => !ignore && setRecs({ key, data }))
      .catch((error) => !ignore && setRecs({ key, error }))
    return () => {
      ignore = true
    }
  }, [id, lifeEvent, recsAttempt])

  if (dashboard?.id !== id) return <main className="page muted">Loading your dashboard…</main>

  if (dashboard.error?.status === 404) {
    return (
      <main className="page">
        <h1>Customer not found</h1>
        <Link to="/customers">← Back to customers</Link>
      </main>
    )
  }

  if (dashboard.error) {
    return (
      <main className="page">
        <ErrorState
          title="Couldn't load your dashboard"
          onRetry={() => {
            setDashboard(null)
            setDashboardAttempt((n) => n + 1)
          }}
        />
      </main>
    )
  }

  const { customer, vehicle, contract, finances, equity, equity_timeline } = dashboard.data
  const recsReady = recs?.key === recsKey(id, lifeEvent, recsAttempt)
  const recsData = recsReady ? recs.data : null
  // After a What-if change the drawer shows the same option's new numbers, or closes if it's gone
  const whyOption = recsData?.recommendations.find((r) => r.id === whyId) ?? null

  return (
    <main className="page">
      <header className="header">
        <div className="header-left">
          <Link to="/customers" className="back-link">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M15 5l-7 7 7 7" />
            </svg>
            Switch customer
          </Link>
          <h1>Hi, {customer.name}</h1>
        </div>
        <EquityBadge equity={equity} />
      </header>

      <div className="grid-3 snapshot">
        <VehicleCard vehicle={vehicle} />
        <ContractCard contract={contract} />
        <FinanceSnapshot finances={finances} />
      </div>

      <section className="section">
        <h2>Your best moves</h2>
        <WhatIfPanel value={lifeEvent} onChange={setLifeEvent} summary={recsData?.life_event_applied ?? null} />
        {!recsReady && <RecommendationSkeleton />}
        {recsReady && recs.error && (
          <ErrorState title="Couldn't load recommendations" onRetry={() => setRecsAttempt((n) => n + 1)} />
        )}
        {recsData && (
          <>
            <RecommendationList
              recommendations={recsData.recommendations}
              considered={recsData.considered}
              onWhyThis={(rec) => setWhyId(rec.id)}
            />
            {/* Anchor for the "We also considered N other options" link */}
            <div id="all-options">
              <ComparisonTable considered={recsData.considered} />
            </div>
          </>
        )}
        <EquityChart timeline={equity_timeline} contractType={contract.type} />
      </section>
      <WhyDrawer option={whyOption} onClose={() => setWhyId(null)} />
    </main>
  )
}
