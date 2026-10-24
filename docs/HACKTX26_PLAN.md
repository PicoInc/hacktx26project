# Next Move — HackTX 26 Execution Plan

> **Challenge:** Toyota Financial Services, *"What's Your Next Move?"* (primary)
> **Stretch:** Capital One, *Best Use of Nessie* (secondary, only if time allows)
> **Team:** Samu, Jose, Rodrigo
> **Final submission:** Sun 11:30 AM on hacktx26.devpost.com · **Soft submission:** Sat 11:30 PM · **Judging:** Sun 2–5 PM (WEL)

---

## 1. What we're building (one paragraph)

A **"Next Move" dashboard** for a Toyota customer. They log in and see their vehicle and their loan or lease, plus a snapshot of their finances. The app then shows **2–3 ranked recommendation cards** answering *"Given my situation today, what's the smartest next move for me and my Toyota?"* Each card has the numbers, a plain-English explanation, and one action button (self-service, schedule a follow-up, or an eligible offer). A **"What if?"** panel lets them simulate a life event and see the recommendations change.

### How we score against Toyota's four criteria

| Criterion | How we hit it |
|---|---|
| **Personalize** | Each persona has a vehicle, a contract and a financial profile. Recommendations are computed from all three. |
| **Simplify** | Side-by-side options with monthly payment, total cost and trade-offs. The LLM writes the plain-English "why". |
| **Guide** | Every card ends in exactly one action: self-service, follow-up, or offer. There is always a human handoff. |
| **Value** | Pitch slide: end-of-lease retention, upgrades timed to real equity, fewer support calls. |
| *Responsible AI* | All math is in deterministic Python. The LLM only explains. Assumptions are always shown, and a validator rejects any LLM text containing numbers we didn't compute. |

---

## 2. MVP definition (what must exist at the demo)

**Must have (MVP):**
1. Persona picker (3 personas) acting as "login".
2. Dashboard: vehicle card, contract card, financial snapshot, equity gauge.
3. Recommendation engine: options compared, ranked, with affordability guardrails.
4. 2–3 recommendation cards with numbers, an LLM explanation, an assumptions drawer, and an action button.
5. "What if?" simulator with at least 2 life events wired end-to-end.

**Should have:** an option comparison table, an equity-over-time chart (Recharts), a "Why this recommendation?" drawer, and a fallback template explanation if the LLM fails.

**Stretch (only after MVP is solid):**
- Live Nessie data (Capital One track).
- English/Spanish toggle.
- NHTSA recalls ("You have an open recall, book service") as an extra card.
- fueleconomy.gov MPG for hybrid upgrade savings.
- Deployment to a public URL.

**Cut list if we fall behind (cut in this order):** Spanish → recalls/MPG → live Nessie → equity chart → 3rd life event.

---

## 3. Architecture

```
frontend/  React (Vite) + Recharts
   │  fetch /api/*
backend/   Flask
   ├── routes.py            API endpoints (contract in §4)
   ├── engine/
   │   ├── finance.py       amortization, lease math, payoff, equity
   │   ├── options.py       builds candidate options per contract type
   │   ├── events.py        life-event adjustments ("What if?")
   │   ├── guardrails.py    affordability rules + ranking
   │   └── tests/           pytest for every formula
   ├── services/
   │   ├── profile.py       get_financial_profile(customer_id) ← single entry point
   │   ├── nessie.py        live Nessie client (stretch)
   │   └── llm.py           explanation generation + number validator
   └── data/
       ├── toyota_profiles.json   synthetic vehicles + contracts (linked to customer_id)
       ├── vehicle_values.json    synthetic market values / depreciation
       ├── offers.json            synthetic eligible offers
       └── mock_bank/             Nessie-shaped mock data per persona
```

**Key decision: the data adapter.** `get_financial_profile(customer_id)` returns the same normalized object whether data comes from mock JSON or live Nessie. Controlled by an env var:

```
DATA_MODE=mock    # default; we build everything against this
DATA_MODE=nessie  # flip when/if Nessie is reachable
```

Nessie was unreachable at 3 PM Saturday (`api.nessieisreal.com` timed out). Nothing in the MVP may depend on it. The mock files mirror Nessie's shapes (accounts, deposits, purchases, bills, loans), so switching over is a one-file change.

---

## 4. API contract (agree on this first, then everyone works in parallel)

### `GET /api/personas`
```json
[{ "customer_id": "p1", "name": "Maya Lopez", "tagline": "Student · Corolla lease · over on miles" }]
```

### `GET /api/customers/:id/dashboard`
```json
{
  "customer": { "id": "p1", "name": "Maya Lopez" },
  "vehicle":  { "year": 2023, "model": "Corolla", "trim": "LE", "mileage": 31200, "est_value": 19800 },
  "contract": {
    "type": "lease",                       // "lease" | "loan"
    "monthly_payment": 289, "months_remaining": 4, "apr": 4.9,
    "residual": 16500, "payoff": 17656,
    "miles_allowed_per_year": 10000, "miles_projected_at_end": 35500
  },
  "finances": {
    "monthly_income": 2100, "monthly_bills": 1150, "monthly_spending": 520,
    "monthly_surplus": 430, "savings": 1800, "checking": 640,
    "source": "mock"                       // "mock" | "nessie"
  },
  "equity": { "value": 2144, "status": "positive" }   // value − payoff
}
```

### `POST /api/customers/:id/recommendations`
Request: `{ "life_event": null }` or `{ "life_event": { "type": "income_drop", "params": { "pct": 20 } } }`
```json
{
  "recommendations": [
    {
      "id": "buyout",
      "rank": 1,
      "title": "Buy out your Corolla",
      "headline_numbers": { "monthly_payment": 312, "delta_monthly": 23, "total_cost": 18720, "term_months": 60 },
      "affordable": true,
      "tradeoffs": ["Avoid $1,375 over-mileage fee", "Own the car at end of term"],
      "assumptions": { "apr": 6.9, "term_months": 60, "est_value": 19800, "source": "synthetic" },
      "action": { "kind": "self_service", "label": "Start buyout" },   // self_service | follow_up | offer
      "explanation": "Plain-English text from the LLM (or template fallback)"
    }
  ],
  "considered": [ /* every option evaluated, incl. rejected ones with reason */ ]
}
```

**Rule:** the frontend never computes money. It only renders what the API returns.

---

## 5. Engine spec (what the math must cover)

| Function | Formula / rule |
|---|---|
| Loan payment | `P = r·PV / (1 − (1+r)^−n)`, r = APR/12 |
| Payoff | remaining principal from the amortization schedule |
| Lease payment | depreciation `(cap_cost − residual)/n` + finance charge `(cap_cost + residual)·money_factor` (MF = APR/2400) |
| Lease-end options | **return** (mileage overage fee + disposition fee) · **buyout** (residual + fees, financed) · **new lease** (new model) |
| Loan options | **keep** · **refinance** (new APR/term) · **extend term** · **trade in / upgrade** (equity rolls into new loan) · **payment deferral** |
| Equity | `est_value − payoff` → positive / negative |
| Mileage | `projected_end_miles − allowed` × $0.25/mi |

**Guardrails (responsible AI):**
- An option is **affordable** only if the new car payment is ≤ 15% of monthly income, the payment increase is ≤ 50% of monthly surplus, and savings stay ≥ 1 month of bills after any upfront cost.
- Unaffordable options are never ranked #1. They go in `considered` with a reason.
- Every option exposes its `assumptions`.
- If the income drop leaves no affordable option, the top card becomes **"Talk to a TFS advisor"** (human handoff).

**Life events ("What if?")** modify inputs before the engine runs:

| Event | Effect |
|---|---|
| `income_drop` | income × (1 − pct) |
| `new_baby` | +$X/month spending, flags need for a bigger vehicle (Corolla → RAV4/Highlander) |
| `longer_commute` | +miles/year → affects lease mileage and fuel cost |
| `job_change` / `move` | income change ± and/or commute change |

---

## 6. LLM layer

- **Model:** Gemini API (free tier, and it also qualifies for MLH's *Best Use of Gemini*) or whichever key we already have.
- **Input:** the computed recommendation JSON. **Output:** a 2–3 sentence explanation per card, plus a "Why this?" paragraph.
- **Prompt rules:** use only numbers present in the input, no new rates or promises, mention one trade-off, end with the action.
- **Validator:** extract every number in the LLM output and reject the text if a number isn't in the input JSON. Fall back to a template sentence. This is a strong demo moment ("our AI can't make up numbers").
- **Cache** explanations per (persona, life_event) so the demo is instant and never waits on the API live.

---

## 7. Personas (synthetic Toyota data + mock bank data)

> Exact numbers and expected outcomes live in `HACKTX26_BACKLOG.md`, Appendix B.

| ID | Persona | Vehicle / contract | Finances | Expected top move |
|---|---|---|---|---|
| `p1` | **Maya**, college student | 2023 Corolla LE **lease**, 4 months left, projected ~5,500 mi over | Part-time income, small surplus | Buy out the car or buy extra miles (avoids the overage fee) |
| `p2` | **The Reyes family**, baby on the way | 2022 RAV4 **loan**, 38 months left | Two incomes, moderate surplus | Baseline: keep. "New baby" → Highlander **rejected as unaffordable**, keep stays #1. "Income drop" → talk to an advisor + term extension |
| `p3` | **Daniel**, positive equity | 2021 Camry **loan**, high APR from 2021, strong market value | Strong surplus and savings | Trade in to a new Camry Hybrid using equity, or refinance |

Each persona has `vehicle`, `contract`, `customer_id` in `toyota_profiles.json` and a matching `mock_bank/<id>.json` with Nessie-shaped `accounts`, `deposits`, `purchases`, `bills`.

---

## 8. Roles

Three roles of about 21 story points each. Every file has exactly one owner (full map in `HACKTX26_BACKLOG.md` → "Roles & file ownership"). Swap names freely, but keep the split.

### Samu: Engine + decision UX
- `backend/engine/**`: finance math, option builder, affordability guardrails, ranking, life events, `recommend()`
- pytest coverage for every formula (judges love "we tested the math")
- Frontend: `WhatIfPanel.jsx`, the UI that exposes his life events
- Leads the pitch deck

### Rodrigo: Data + backend + data viz
- All synthetic data: `toyota_profiles.json`, `vehicle_catalog.json`, `offers.json`, `mock_bank/*`
- `services/profile.py` adapter, then live Nessie (stretch) and NHTSA recalls (stretch)
- Flask app: `app.py`, `routes.py`, `requirements.txt`, CORS, `.env`
- Persona tuning (with Samu), equity timeline
- Frontend: `ComparisonTable.jsx`, `EquityChart.jsx` (Recharts)
- Records the demo video

### Jose: AI + frontend core
- `services/llm.py`: prompt, number validator, template fallback, explanation cache
- Frontend shell: routing, `api.js`, persona picker, dashboard, recommendation cards, "Why this?" drawer, human handoff, UI polish
- Works against a **hard-coded copy of the contract JSON** until the backend is live, so he's never blocked
- Devpost write-up and screenshots

**Seams between owners:** Rodrigo's route calls `recommend()` (Samu) and `explain_all()` (Jose). Jose's `Dashboard.jsx` renders Samu's and Rodrigo's components through fixed props.

**Shared:** rehearsal, code freeze, and someone goes to the **Toyota workshop at 6 PM (GDC 1.304)** to ask what they want to see and whether they have sample data.

---

## 9. Milestones (Sat 3 PM → Sun 11:30 AM)

| # | Deadline | Milestone | Done when |
|---|---|---|---|
| **M0** | Sat **3:45 PM** | Setup | Repo has `frontend/` + `backend/`, both run locally, API contract committed as `docs/contract.md` + sample JSON, issues created |
| **M1** | Sat **7:00 PM** | Pieces work alone | Engine returns ranked options for p1 in a pytest; Flask serves `/personas` + `/dashboard` from mock data; UI renders the dashboard from hard-coded JSON |
| **M2** | Sat **10:30 PM** | End-to-end, 1 persona | p1 goes from picker → dashboard → 2–3 real recommendation cards with LLM explanations via the live API |
| 📤 | Sat **11:30 PM** | **Soft submission** | Devpost draft submitted (title, one-liner, screenshots, repo link) |
| **M3** | Sun **3:00 AM** | Full MVP | All 3 personas, "What if?" with ≥ 2 events, guardrails visible, assumptions drawer, LLM validator + fallback |
| **M4** | Sun **8:30 AM** | Polish + stretch | UI polish, equity chart, then stretch in order: live Nessie → Spanish → recalls |
| 🧊 | Sun **10:30 AM** | **Code freeze** | Only bug fixes after this |
| 📤 | Sun **11:30 AM** | **Final submission** | Devpost complete: description, demo video (≤ 2 min), screenshots, tracks selected (Toyota + Capital One if Nessie is used), repo public |
| 🎤 | Sun **2:00 PM** | Judging | Demo runs locally from cache, no Wi-Fi needed; everyone can give the 2-minute pitch |

**Checkpoints:** a 5-minute sync at **7 PM, 10:30 PM, 3 AM, 8:30 AM**. Each person says what's done, what's next, and what's blocking them. If a milestone slips by more than 1h, apply the cut list.

---

## 10. Task checklist

The full task list (stories NM-1 to NM-32, with owners, dependencies, acceptance criteria and exact persona numbers) lives in **`HACKTX26_BACKLOG.md`** and on the GitHub board. That file is the source of truth for who does what.

---

## 11. Git workflow

- `main` always runs. Work on `feat/<area>-<thing>` branches and open small PRs.
- **Merge at least every 2 hours.** Nobody holds a branch overnight.
- The other two owners skim each PR; for small PRs, merging without review is fine.
- Commit the sample JSON first. If the contract changes, update `docs/contract.md` in the same PR.

---

## 12. Demo script (2 minutes)

1. **Hook (15s):** "Every month, Toyota customers wonder whether to keep, trade, refinance or return. Most just call support. We built the answer."
2. **Maya (30s):** lease ending, over on miles → buyout beats return by $X. Open "Why this?" → assumptions.
3. **Reyes family (35s):** "What if… new baby?" → Highlander is shown but **rejected as unaffordable**, so the app recommends refinancing instead. This is the responsible-AI moment.
4. **Daniel (20s):** positive equity → upgrade offer, with a follow-up action.
5. **Under the hood (10s):** math is deterministic and tested; the LLM only explains; a validator blocks invented numbers.
6. **Value (10s):** retention at lease end, upgrades timed to real equity, fewer support calls.

---

## 13. Reference

- **Nessie (Capital One mock bank API):** fake but realistic customers, accounts, deposits, purchases, bills, loans. Key is passed as `?key=`. Base URL: `api.nessieisreal.com` (down at 3 PM Sat) or `api.reimaginebanking.com`; confirm with Capital One in the WEL hallway / Discord.
- **Optional free real data:** NHTSA vPIC (VIN decode), NHTSA Recalls API, fueleconomy.gov (MPG). No keys needed.
- **Event:** hacktx.com · Discord · Devpost: hacktx26.devpost.com · up to 3 tracks per project.
