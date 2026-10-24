import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getDashboard, getRecommendations } from '../api.js'
import ComparisonTable from '../components/ComparisonTable.jsx'
import EquityChart from '../components/EquityChart.jsx'
import WhatIfPanel from '../components/WhatIfPanel.jsx'

export default function Dashboard() {
  const { id } = useParams()
  const [dashboard, setDashboard] = useState(null)
  const [recs, setRecs] = useState(null)
  const [lifeEvent, setLifeEvent] = useState(null)

  useEffect(() => {
    getDashboard(id).then(setDashboard)
  }, [id])

  useEffect(() => {
    getRecommendations(id, lifeEvent).then(setRecs)
  }, [id, lifeEvent])

  if (!dashboard || !recs) return <main>Loading…</main>

  return (
    <main>
      <Link to="/">Switch customer</Link>
      <h1>{dashboard.customer.name}</h1>
      <WhatIfPanel value={lifeEvent} onChange={setLifeEvent} summary={recs.life_event_applied} />
      <ComparisonTable considered={recs.considered} />
      <EquityChart timeline={dashboard.equity_timeline} contractType={dashboard.contract.type} />
    </main>
  )
}
