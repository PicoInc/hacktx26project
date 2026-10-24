import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getDashboard, getRecommendations } from '../api.js'
import ComparisonTable from '../components/ComparisonTable.jsx'
import ContractCard from '../components/ContractCard.jsx'
import EquityBadge from '../components/EquityBadge.jsx'
import EquityChart from '../components/EquityChart.jsx'
import FinanceSnapshot from '../components/FinanceSnapshot.jsx'
import RecommendationList from '../components/RecommendationList.jsx'
import VehicleCard from '../components/VehicleCard.jsx'
import WhatIfPanel from '../components/WhatIfPanel.jsx'

export default function Dashboard() {
  const { id } = useParams()
  // Results are tagged with the id they belong to, so switching customers never shows stale data
  const [dashboard, setDashboard] = useState(null)
  const [recs, setRecs] = useState(null)
  const [lifeEvent, setLifeEvent] = useState(null)

  useEffect(() => {
    let ignore = false
    getDashboard(id)
      .then((data) => !ignore && setDashboard({ id, data }))
      .catch(() => !ignore && setDashboard({ id, data: null }))
    return () => {
      ignore = true
    }
  }, [id])

  useEffect(() => {
    let ignore = false
    getRecommendations(id, lifeEvent).then((data) => !ignore && setRecs({ id, data }))
    return () => {
      ignore = true
    }
  }, [id, lifeEvent])

  if (dashboard?.id !== id || recs?.id !== id) return <main className="page muted">Loading…</main>

  if (!dashboard.data) {
    return (
      <main className="page">
        <h1>Customer not found</h1>
        <Link to="/">← Back to customers</Link>
      </main>
    )
  }

  const { customer, vehicle, contract, finances, equity, equity_timeline } = dashboard.data

  return (
    <main className="page">
      <header className="header">
        <div className="header-left">
          <Link to="/" className="back-link">← Switch customer</Link>
          <h1>Hi, {customer.name}</h1>
        </div>
        <EquityBadge equity={equity} />
      </header>

      <div className="grid-3">
        <VehicleCard vehicle={vehicle} />
        <ContractCard contract={contract} />
        <FinanceSnapshot finances={finances} />
      </div>

      <section className="section">
        <h2>Your next move</h2>
        <WhatIfPanel value={lifeEvent} onChange={setLifeEvent} summary={recs.data.life_event_applied} />
        <RecommendationList recommendations={recs.data.recommendations} considered={recs.data.considered} />
        {/* Anchor for the "We also considered N other options" link */}
        <div id="all-options">
          <ComparisonTable considered={recs.data.considered} />
        </div>
        <EquityChart timeline={equity_timeline} contractType={contract.type} />
      </section>
    </main>
  )
}
