// Static sample data for now. NM-15 swaps these bodies for fetch('/api/...').
import personas from './sample/personas.json'
import dashboardP1 from './sample/dashboard_p1.json'
import dashboardP2 from './sample/dashboard_p2.json'
import dashboardP3 from './sample/dashboard_p3.json'
import recommendationsP1 from './sample/recommendations_p1.json'

const dashboards = { p1: dashboardP1, p2: dashboardP2, p3: dashboardP3 }

export async function getPersonas() {
  return personas
}

export async function getDashboard(id) {
  const dashboard = dashboards[id]
  // Mirrors the API's 404 for unknown ids
  if (!dashboard) throw new Error('customer not found')
  return dashboard
}

export async function getRecommendations(_id, _lifeEvent) {
  // Only p1 has sample recommendations; the live API covers every persona
  return recommendationsP1
}
