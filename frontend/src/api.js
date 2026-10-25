// Talks to the Flask API through Vite's /api proxy (see vite.config.js).
// VITE_USE_SAMPLE=true serves the bundled sample JSON instead, so the UI runs without the backend.
import dashboardP1 from './sample/dashboard_p1.json'
import dashboardP2 from './sample/dashboard_p2.json'
import dashboardP3 from './sample/dashboard_p3.json'
import personas from './sample/personas.json'
import recommendationsP1 from './sample/recommendations_p1.json'

const USE_SAMPLE = import.meta.env.VITE_USE_SAMPLE === 'true'
const sampleDashboards = { p1: dashboardP1, p2: dashboardP2, p3: dashboardP3 }

// status is the HTTP status, or 0 when the server couldn't be reached at all
export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, options) {
  let response
  try {
    response = await fetch(`/api${path}`, options)
  } catch {
    throw new ApiError("Couldn't reach the server", 0)
  }
  // Error bodies are JSON from Flask, but plain text when the Vite proxy can't reach Flask
  const body = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(body?.error ?? `Request failed (${response.status})`, response.status)
  return body
}

export async function getPersonas() {
  if (USE_SAMPLE) return personas
  return request('/personas')
}

export async function getDashboard(id) {
  if (USE_SAMPLE) {
    if (!sampleDashboards[id]) throw new ApiError('customer not found', 404)
    return sampleDashboards[id]
  }
  return request(`/customers/${encodeURIComponent(id)}/dashboard`)
}

export async function getRecommendations(id, lifeEvent) {
  // Only p1 has sample recommendations; the live API covers every persona
  if (USE_SAMPLE) return recommendationsP1
  return request(`/customers/${encodeURIComponent(id)}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ life_event: lifeEvent ?? null }),
  })
}
