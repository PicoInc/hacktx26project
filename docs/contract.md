# API contract

All money values are numbers in USD, rounded to 2 decimals by the API. The frontend never computes money.
Full samples for persona p1 live in `docs/sample_responses/`. Exact persona numbers: backlog Appendix B.
**Changing a shape?** Update this file and the sample JSON in its own small PR, and tell the team.

## `GET /api/health`
`{ "status": "ok" }`

## `GET /api/personas` → `personas.json`
`[{ customer_id, name, tagline }]`

## `GET /api/customers/:id/dashboard` → `dashboard_p1.json`
`{ customer, goals, vehicle, contract, finances, equity, equity_timeline }`
- `contract.type`: `"lease" | "loan"`
- `finances.source`: `"mock" | "nessie"`
- `equity.status`: `"positive" | "negative"`
- `equity_timeline`: `[{ month, value, payoff }]` (empty until NM-23)
- Unknown id → `404 { "error": "customer not found" }`

## `POST /api/customers/:id/recommendations` → `recommendations_p1.json`
Body: `{ "life_event": null }` or `{ "life_event": { "type": "new_baby" | "income_drop" | "longer_commute", "params": {} } }`

Response: `{ recommendations, considered, relief_needed, life_event_applied, finances_after_event }`
- `recommendations`: top 3, each with `id, rank, previous_rank, title, vehicle_label, keeps_vehicle, monthly_payment, delta_monthly, upfront_cost, term_months, total_cost, fuel_monthly, effective_monthly, equity_used, affordable, rejection_reason, tradeoffs[], assumptions{}, action{kind,label,confirmation}, explanation, explanation_source`
- `action.kind`: `"self_service" | "follow_up" | "offer"`
- `action.confirmation`: one customer-facing sentence shown in a toast after the button is clicked ("Buyout started — a TFS specialist will confirm within 1 business day")
- `considered`: every option evaluated, including rejected ones with `rejection_reason`
- `life_event_applied`: `null` or a one-line summary string
- `finances_after_event`: `null` or a `finances` object after the event
- Invalid life event → `400 { error, allowed: [...] }`
