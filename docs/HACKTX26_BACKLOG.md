# Next Move — Scrum Backlog (HackTX 26)

> **Product goal:** A Toyota customer opens the app and gets their smartest next move, with real numbers, a plain-English why, and one clear action.
> **Team:** Samu (Engine + decision UX) · Rodrigo (Data + backend + data viz) · Jose (AI + frontend core)
> **Full plan & API contract:** `HACKTX26_PLAN.md` · **Shared numbers:** see the Appendix at the bottom of this file
>
> **Status (Sat 3:25 PM):** Sprint 0 ✅ done · **Sprint 1 in progress** (ends 7:00 PM stand-up) · Roles rebalanced: ~21 pts each

---

## How we work

**Sprints** are short timeboxes that end at a milestone. Each sprint ends with a 5-minute **stand-up**: what I finished, what I'm doing next, what's blocking me.

| Sprint | Timebox | Sprint goal | Ends with |
|---|---|---|---|
| ✅ **Sprint 0** | Sat 3:00 → 3:45 PM | Everyone can code without blocking anyone | **Done** — skeleton pushed, contract agreed |
| **Sprint 1** | Sat 3:45 → 7:00 PM | Each layer works on its own | Stand-up 7 PM |
| **Sprint 2** | Sat 7:00 → 10:30 PM | One persona works end to end | Stand-up 10:30 PM + **soft submission 11:30 PM** |
| **Sprint 3** | Sat 10:30 PM → Sun 3:00 AM | Full MVP (3 personas + What-if) | Stand-up 3 AM |
| **Sprint 4** | Sun 3:00 → 8:30 AM | Polish + stretch goals | Stand-up 8:30 AM |
| **Sprint 5** | Sun 8:30 → 11:30 AM | Ship it | **Code freeze 10:30 AM**, final submission 11:30 AM |

**Story points:** 1 = ~15 min · 2 = ~30 min · 3 = ~1 h · 5 = ~2 h. Anything bigger gets split.

**Board columns** (GitHub Projects): `Backlog → To Do → In Progress → Review → Done`

**Each story has:** *Context* (why it matters), *Blocked by* (what must be merged first), *Files* (what you touch; you own them), *Spec* (signatures, shapes, rules), *Tasks* (checklist), *Acceptance criteria* (how we know it's done), *How to verify* (the exact check).

**Definition of Done (applies to every story):**
- [ ] Meets every acceptance criterion
- [ ] Merged into `main`, and `main` still runs (`npm run dev` + `flask run`)
- [ ] No secrets committed (`.env` stays local)
- [ ] Engine stories: `pytest` passes
- [ ] If the API shape changed, `docs/contract.md` and the sample JSON were updated in the same PR

**Priority labels:** `P0` = MVP must-have · `P1` = should-have · `P2` = stretch (only if all P0 is Done)

**If a sprint slips by more than 1 h:** drop P2 stories first, then P1. Cut order: Spanish → recalls → live Nessie → equity chart → 3rd life event.

---

## Epics

| Epic | Description | Owner |
|---|---|---|
| **E0** Setup | Repo, skeleton, contract | All |
| **E1** Engine | Finance math, options, guardrails, ranking, life events | Samu |
| **E2** Data & API | Synthetic data, bank data, Flask API, data adapter, persona tuning | Rodrigo |
| **E3** AI Explanations | LLM, number validator, fallback, cache | Jose |
| **E4** Frontend | Shell, dashboard, cards, drawer (Jose) · What-if panel (Samu) · comparison table, equity chart (Rodrigo) | Jose (lead) |
| **E5** Capital One (stretch) | Live Nessie | Rodrigo |
| **E6** Demo & Submission | Devpost (Jose) · video (Rodrigo) · pitch deck (Samu) | All |

### Roles & file ownership (each file has exactly one owner)

| Person | Role | Owns (only they edit) |
|---|---|---|
| **Samu** | Engine + decision UX | `backend/engine/**` (math, options, guardrails, ranking, life events, tests) · `frontend/src/components/WhatIfPanel.jsx` |
| **Rodrigo** | Data + backend + data viz | `backend/app.py`, `backend/routes.py`, `backend/requirements.txt`, `backend/data/**`, `backend/services/profile.py`, `nessie.py`, `equity.py`, `recalls.py`, `backend/scripts/seed_nessie.py` · `frontend/src/components/ComparisonTable.jsx`, `EquityChart.jsx` |
| **Jose** | AI + frontend core | `backend/services/llm.py`, `templates.py`, `cache.py`, `backend/prompts/**`, `backend/scripts/warm_cache.py`, `backend/cache/**` · `frontend/package.json`, `App.jsx`, `api.js`, `pages/**`, `styles/**`, and every other component |

**Why this split:** Samu owns the decision logic *and* the UI that exposes it (What-if), Rodrigo owns everything data from raw JSON to API to charts, and Jose owns the AI layer and the app shell everything plugs into.

**Cross-owner seams (agree on these, then never touch each other's files):**
- **Engine → API:** Rodrigo's route calls only `engine.recommend.recommend(profile, life_event) -> dict` (Samu).
- **API → LLM:** Rodrigo's route calls only `services.llm.explain_all(recommendations, profile, life_event) -> dict[option_id, {"text", "source"}]` (Jose).
- **Dashboard → components:** `Dashboard.jsx` (Jose) holds the `lifeEvent` state and renders other people's components with these props:
  - `<WhatIfPanel value={lifeEvent} onChange={setLifeEvent} summary={recs.life_event_applied} />` (Samu)
  - `<ComparisonTable considered={recs.considered} />` (Rodrigo)
  - `<EquityChart timeline={dashboard.equity_timeline} contractType={dashboard.contract.type} />` (Rodrigo)
  - In NM-9, Jose creates these three files as stubs (`export default function X() { return null }`) so imports work from day one.
- **Dependencies:** need a new npm package? Ask Jose (he owns `package.json`; he adds `react-router-dom` and `recharts` up front). Need a Python package? Ask Rodrigo (he owns `requirements.txt`; he adds `flask`, `flask-cors`, `python-dotenv`, `requests`, `pytest`, `google-genai` up front).

### Dependency map (what unblocks what)

```
NM-4 ─► NM-5 ─► NM-11 ─► NM-17 ─► NM-18
                  │
NM-6 ─► NM-7 ─► NM-8 ─► NM-12 ─► NM-13 ─► NM-14 ─► NM-21
                            │
NM-9 ─► NM-10 ──────────────┴─► NM-15 ─► NM-19, NM-20 ─► NM-30 ─► NM-31
```

Rule of thumb: **Samu and Rodrigo meet at NM-12** (Rodrigo's endpoint calls Samu's engine), **Jose plugs the LLM into it at NM-13**, and **everyone meets at NM-15** when the UI switches from sample JSON to the live API.

---

## Sprint 0 — Setup (Sat 3:00 → 3:45 PM) ✅ DONE

### ✅ NM-1 · Repo skeleton `E0` `P0` · 2 pts · **Jose**
*As a team, we want every file stubbed in the repo so we never edit the same file.*

**Context:** Merge conflicts mostly come from two people creating or editing the same file. Stubbing every file up front, with one owner per folder, removes that.

**Tasks:**
- [x] `frontend/` (Vite scaffold) + `backend/` (Flask) folder tree with empty stubs
- [x] `.gitignore` (`.env`, `node_modules`, `__pycache__`, `dist`), `.env.example`
- [x] `README.md` with how to run both apps

**Acceptance criteria:**
- [x] All three can clone, run `npm run dev` and `flask run`, and see no errors.

### ✅ NM-2 · API contract `E0` `P0` · 2 pts · **All**
*As a developer, I want agreed JSON shapes so I can build against them without waiting.*

**Tasks:**
- [x] `docs/contract.md` with the 3 endpoints (`/personas`, `/dashboard`, `/recommendations`)
- [x] `docs/sample_responses/*.json` for persona p1

**Acceptance criteria:**
- [x] Everyone has read and agreed. Any later change goes through its own small PR.

### ✅ NM-3 · Board & branches `E0` `P0` · 1 pt · **Samu**

**Tasks:**
- [x] GitHub Project board with these stories as issues, labels P0/P1/P2, owners assigned
- [x] Branch naming agreed: `feat/<area>-<thing>`

---

## Sprint 1 — Layers work alone (Sat 3:45 → 7:00 PM)

### NM-4 · Core finance math `E1` `P0` · 3 pts · **Samu**
*As the engine, I need correct payment math so every recommendation is trustworthy.*

**Context:** Every number a customer sees comes from these functions. The judges' responsible-AI question will be "how do you know the numbers are right?", and the answer is these tested pure functions. They're the foundation for NM-5, NM-11 and NM-17.

**Blocked by:** nothing. Start immediately.

**Files:** `backend/engine/finance.py`, `backend/engine/constants.py`, `backend/engine/tests/test_finance.py`

**Spec:** pure functions only (no I/O, no Flask, no globals except constants). Round only at the API boundary, not inside these functions.
```python
def loan_payment(principal: float, apr_pct: float, term_months: int) -> float
    # P = r·PV / (1 − (1+r)^−n), r = apr/1200; if apr == 0 → principal / n

def loan_balance(principal: float, apr_pct: float, term_months: int, payments_made: int) -> float
    # remaining principal after k payments: PV(1+r)^k − P·((1+r)^k − 1)/r

def lease_payment(cap_cost: float, residual: float, money_factor: float, term_months: int) -> float
    # depreciation fee (cap − residual)/n  +  finance charge (cap + residual)·MF

def apr_to_money_factor(apr_pct: float) -> float           # apr / 2400
def projected_end_miles(current_miles: int, months_elapsed: int, months_remaining: int) -> int
    # current + (current / months_elapsed) · months_remaining
def mileage_overage_fee(projected_miles: int, allowed_miles: int, rate_per_mile: float) -> float   # max(0, …)
def equity(market_value: float, payoff: float) -> float     # value − payoff (can be negative)
def monthly_fuel_cost(miles_per_year: int, mpg: float, fuel_price: float) -> float
```
`constants.py` holds **every** assumption from the Appendix (rates, fees, thresholds). No magic numbers anywhere else in the engine.

**Tasks:**
- [ ] Create `constants.py` with the full Appendix A table
- [ ] Implement the 8 functions above with docstrings
- [ ] Unit tests using the reference values below
- [ ] Edge cases: APR 0, term 1, payments_made == term (balance ≈ 0), negative equity

**Acceptance criteria:**
- [ ] `pytest backend/engine/tests/test_finance.py` passes
- [ ] Reference values match to the cent (±$0.01):
  - `loan_payment(30000, 4.9, 60)` → **564.76**
  - `loan_balance(30000, 4.9, 60, 22)` → **≈ 19,841**
  - `loan_payment(22000, 9.9, 72)` → **406.46**
  - `lease_payment(22500, 14600, 0.00175, 36)` → **284.37**
  - `mileage_overage_fee(35100, 30000, 0.25)` → **1,275.00**

**How to verify:** run pytest, and paste one case into an online loan calculator (e.g. bankrate.com) as a sanity check.

### NM-5 · Option builder `E1` `P0` · 5 pts · **Samu**
*As a customer, I want every realistic option compared so I can see my choices side by side.*

**Context:** This is what turns "a car + a contract + finances" into the list of possible moves. NM-11 then filters and ranks this list. Each option must carry everything the UI card and the LLM need, so nobody downstream does math.

**Blocked by:** NM-4

**Files:** `backend/engine/options.py`, `backend/engine/tests/test_options.py`

**Spec:**
```python
def build_options(profile: dict) -> list[dict]
    # profile = the /dashboard response (customer, vehicle, contract, finances, goals)
```
Which options to generate:

| Contract | Option `id` | When generated | Math |
|---|---|---|---|
| lease | `lease_buyout` | always | finance `residual + PURCHASE_OPTION_FEE` at `USED_AUTO_APR` over `BUYOUT_TERM` |
| lease | `return_new_lease` | always | upfront = overage fee + `DISPOSITION_FEE`; new lease on the same model's new year |
| lease | `buy_miles_new_lease` | if overage > 0 | upfront = overage miles × `PREPAID_MILES_RATE` + `DISPOSITION_FEE`; new lease |
| lease | `return_walk_away` | always | upfront = overage fee + disposition; `keeps_vehicle: false` |
| loan | `keep` | always | current payment, remaining payments |
| loan | `refinance` | only if `contract.apr > REFI_APR` | payoff at `REFI_APR` over months remaining |
| loan | `trade_in_upgrade` | for each target in `vehicle_targets` | new price − equity, financed at `NEW_AUTO_APR` over `NEW_TERM` |
| loan | `extend_term` | only when `relief_needed` (see NM-11) | payoff at current APR over months remaining + `EXTENSION_MONTHS` |
| loan | `payment_deferral` | only when `relief_needed` | 0 for `DEFERRAL_MONTHS`, then current payment; months added to the end |

Every option returns this exact shape (it becomes a card):
```json
{
  "id": "lease_buyout",
  "title": "Buy out your Corolla",
  "vehicle_label": "2023 Corolla LE",
  "keeps_vehicle": true,
  "monthly_payment": 294.34,
  "delta_monthly": 9.97,
  "upfront_cost": 0,
  "term_months": 60,
  "total_cost": 17660.40,
  "fuel_monthly": 93.75,
  "effective_monthly": 388.09,
  "equity_used": 0,
  "tradeoffs": ["Avoids the $1,275 over-mileage fee", "You own the car; repairs after warranty are on you"],
  "assumptions": { "apr": 6.9, "term_months": 60, "residual": 14600, "fees": 300, "source": "synthetic" },
  "action": { "kind": "self_service", "label": "Start buyout", "confirmation": "Buyout started — a TFS specialist will confirm within 1 business day" }
}
```
> **Added in NM-10:** `action.confirmation` is the one-sentence toast the card shows after the button is clicked. It's in `docs/contract.md` and both `recommendations_p1.json` samples. Until `options.py` emits it, the card falls back to "`{label}` — a TFS specialist will follow up within 1 business day".
`effective_monthly = monthly_payment + fuel_monthly + upfront_cost / 12`. This is the "first-year monthly burden" used for ranking in NM-11.

Action kinds: `self_service` (buyout, refinance, extra miles, extension), `follow_up` (talk to an advisor, deferral, recall), `offer` (trade-in / new lease using `offers.json`).

**Tasks:**
- [ ] Lease option generators (4)
- [ ] Loan option generators (5), relief options behind a flag
- [ ] Trade-offs: 1–3 short strings per option, written from the numbers (no LLM)
- [ ] Assumptions dict on every option
- [ ] `action.confirmation` on every option: one customer-facing sentence about what happens next, no numbers (added by NM-10; see the p1 sample for wording)
- [ ] Tests per persona (use the fixtures in Appendix B)

**Acceptance criteria:**
- [ ] p1 produces `lease_buyout` at **$294.34/mo** and `buy_miles_new_lease` with upfront **$1,160**
- [ ] p2 produces `keep` at **$564.76** and `trade_in_upgrade` (Highlander) at **≈ $797.33**, and **no** `refinance` (4.9% < 6.4%)
- [ ] p3 produces `refinance` at **≈ $386.06**, `trade_in_upgrade` (Camry Hybrid) at **≈ $465.09**, equity used **≈ $8,385**
- [ ] Every option has all fields in the shape above (a test asserts the keys)

**How to verify:** `pytest backend/engine/tests/test_options.py -v` and print the options for each persona.

### NM-6 · Synthetic Toyota data `E2` `P0` · 3 pts · **Rodrigo**
*As a demo, we need 3 believable customers whose data produces the story we want to tell.*

**Context:** TFS has no public API, so the challenge explicitly asks for synthetic data. These files are the Toyota side of every persona. The numbers below were checked so each persona lands on its intended top move. Copy them exactly, and change them only together with Samu (NM-18).

**Blocked by:** nothing. Start immediately.

**Files:** `backend/data/toyota_profiles.json`, `backend/data/vehicle_catalog.json`, `backend/data/offers.json`

**Spec:**
- `toyota_profiles.json`: an array with one object per persona: `customer_id`, `name`, `tagline`, `goals`, `vehicle`, `contract`, `miles_per_year`, `vehicle_targets` (model keys from the catalog). All values are in **Appendix B**.
- `vehicle_catalog.json`: keyed by model id → `{ "label", "msrp", "mpg", "lease_residual_pct" }`. Values are in **Appendix A**.
- `offers.json`: 2–3 synthetic offers (e.g. "Loyalty: 0.5% APR reduction on a new Toyota", "Prepaid miles at $0.15/mi before lease end"), each `{ id, title, applies_to, terms, disclaimer: "Synthetic offer for demo purposes" }`.

**Tasks:**
- [ ] Write the 3 JSON files from Appendix A and B
- [ ] Add `"source": "synthetic"` at the top level of each file
- [ ] Load-test: a tiny script that loads each file and prints persona names

**Acceptance criteria:**
- [ ] Every field used by the contract's `vehicle` and `contract` objects exists for p1, p2 and p3
- [ ] The values match Appendix B exactly
- [ ] The files parse with `json.load` without errors

**How to verify:** `python -c "import json; print([p['name'] for p in json.load(open('backend/data/toyota_profiles.json'))['profiles']])"`

### NM-7 · Mock bank data + adapter `E2` `P0` · 3 pts · **Rodrigo**
*As the engine, I need one normalized financial profile no matter where the data comes from.*

**Context:** Nessie was unreachable at 3 PM. This story makes the app work without it: mock files shaped exactly like Nessie's responses, plus one adapter function. NM-25 later swaps in live Nessie by flipping an env var, and nothing else changes.

**Blocked by:** nothing (needs the persona numbers from Appendix B).

**Files:** `backend/data/mock_bank/p1.json`, `p2.json`, `p3.json`, `backend/services/profile.py`

**Spec:**
Mock file shape (mirrors Nessie):
```json
{
  "customer": { "_id": "p1", "first_name": "Maya", "last_name": "Lopez" },
  "accounts": [ { "_id": "a1", "type": "Checking", "balance": 640 }, { "_id": "a2", "type": "Savings", "balance": 2600 } ],
  "deposits":  [ { "amount": 1050, "transaction_date": "2026-10-01", "description": "Payroll" } ],
  "purchases": [ { "amount": 64.2, "purchase_date": "2026-10-03", "description": "H-E-B" } ],
  "bills":     [ { "payment_amount": 850, "payee": "Rent", "status": "recurring" } ]
}
```
Use the **last 3 months** of deposits and purchases (enough rows to look real; about 20–40 purchases each).

Adapter:
```python
def get_financial_profile(customer_id: str) -> dict
    # reads DATA_MODE env var: "mock" (default) → data/mock_bank/<id>.json; "nessie" → services/nessie.py (NM-25)
    # returns:
    # { monthly_income, monthly_bills, monthly_spending, monthly_surplus, savings, checking, source }
```
Normalization rules:
- `monthly_income` = sum(deposits over 3 months) / 3
- `monthly_bills` = sum of recurring bills, **including the car payment**
- `monthly_spending` = sum(purchases over 3 months) / 3
- `monthly_surplus` = income − bills − spending
- `savings` / `checking` = balances by account type

**Tasks:**
- [ ] Generate the 3 mock files (a small script with a fixed random seed is fine) so the normalized totals match Appendix B within ±$5
- [ ] Implement `get_financial_profile`
- [ ] Unit test: normalized output for each persona matches Appendix B

**Acceptance criteria:**
- [ ] p1 → income ≈ 2,100, bills ≈ 1,150, spending ≈ 520, surplus ≈ 430, savings 2,600
- [ ] p2 and p3 match Appendix B the same way
- [ ] `DATA_MODE` unset defaults to `mock`; `DATA_MODE=nessie` raises a clear "not implemented yet" error (until NM-25)

**How to verify:** `python -c "from services.profile import get_financial_profile as g; print(g('p1'))"`

### NM-8 · Flask endpoints (read) `E2` `P0` · 2 pts · **Rodrigo**
*As the frontend, I need the persona list and a full dashboard payload from the API.*

**Context:** These two endpoints let Rodrigo switch off the sample JSON early (NM-15). The dashboard payload is also the exact input the engine takes, so it's the "profile" object everyone shares.

**Blocked by:** NM-6, NM-7

**Files:** `backend/app.py`, `backend/routes.py`

**Spec:**
- `GET /api/personas` → `[{ customer_id, name, tagline }]`
- `GET /api/customers/<id>/dashboard` → `{ customer, vehicle, contract, finances, equity, goals }`, exactly the contract shape
  - `contract.payoff` comes from `engine.finance.loan_balance` (loans) or `residual` (leases)
  - `equity = { value, status: "positive" | "negative" }`
- Unknown id → `404 { "error": "customer not found" }`
- CORS enabled for `http://localhost:5173`

**Tasks:**
- [ ] Flask app factory, CORS (`flask-cors`), JSON error handler
- [ ] Both routes, composed from `toyota_profiles.json` + `get_financial_profile()`
- [ ] Ask Samu for `loan_balance` (or temporarily stub it, then swap in NM-4)

**Acceptance criteria:**
- [ ] `curl localhost:5000/api/personas` returns 3 personas
- [ ] `curl localhost:5000/api/customers/p1/dashboard` matches `docs/sample_responses/dashboard_p1.json` key for key
- [ ] `curl localhost:5000/api/customers/nope/dashboard` → 404 JSON

**How to verify:** run the three curls above. The frontend can also hit them from the browser without CORS errors.

### ✅ NM-9 · Persona picker + dashboard (static) `E4` `P0` · 5 pts · **Jose**
*As a customer, I want to see my car, my contract and my money at a glance.*

**Context:** This is the first screen judges see. It has to make the customer's situation obvious in about 5 seconds, before any recommendation appears. It's built against the sample JSON so it never waits on the backend.

**Blocked by:** NM-2 (done)

**Files:** `frontend/package.json`, `frontend/src/App.jsx` (router only), `frontend/src/pages/PersonaPicker.jsx`, `frontend/src/pages/Dashboard.jsx`, `frontend/src/components/VehicleCard.jsx`, `ContractCard.jsx`, `FinanceSnapshot.jsx`, `EquityBadge.jsx`, `frontend/src/api.js`, `frontend/src/styles/tokens.css` · **stubs for others:** `WhatIfPanel.jsx` (Samu), `ComparisonTable.jsx`, `EquityChart.jsx` (Rodrigo)

**Spec:**
- **Picker:** 3 large cards (name, tagline, car model), click → `/customer/:id`. Treat it as the "login".
- **Dashboard layout (desktop first):** top row = Vehicle card · Contract card · Finance snapshot; equity badge in the header; the recommendations area sits below (NM-10).
  - Vehicle: year, model, trim, mileage, estimated value
  - Contract: lease/loan badge, monthly payment, months remaining, APR; for leases, a **mileage bar** (projected vs allowed, red when over)
  - Finances: income, bills, spending, **surplus** (largest number), savings; small "Source: mock / Nessie" tag
  - Equity: green "+$4,300 equity" or red "−$X"
- **`api.js`:** `getPersonas()`, `getDashboard(id)`, `getRecommendations(id, lifeEvent)`. For now they return the imported sample JSON; NM-15 swaps them for `fetch`.
- **Style:** Toyota-ish palette in `tokens.css` (red `#EB0A1E`, near-black `#1A1A1A`, white, gray `#F2F2F2`), system font, 8px spacing grid. All money is formatted with `Intl.NumberFormat('en-US', {style:'currency', currency:'USD'})`.

**Tasks:**
- [x] `npm i react-router-dom recharts` (do it now so nobody else edits `package.json`)
- [x] Stub files for `WhatIfPanel`, `ComparisonTable`, `EquityChart`, rendered in `Dashboard.jsx` with the props from the ownership section; commit and push these first so Samu and Rodrigo can start
- [x] React Router with 2 routes
- [x] 4 components + 2 pages above
- [x] Currency/number formatting helper
- [x] Mileage bar for leases

**Acceptance criteria:**
- [x] Picker shows all 3 personas; clicking p1 opens a complete dashboard
- [x] No money is computed in the frontend; it only formats what the JSON gives
- [x] Readable on a 13" laptop at 100% zoom (that's the judging setup)

**How to verify:** `npm run dev` → click through all 3 personas (fake sample data for p2/p3 is fine at this stage).

### NM-10 · Recommendation cards (static) `E4` `P0` · 3 pts · **Jose**
*As a customer, I want 2–3 clear cards telling me what to do.*

**Context:** The card is the product. It must answer "what should I do, what does it cost me, why, and what do I click" without scrolling.

**Blocked by:** NM-9

**Files:** `frontend/src/components/RecommendationCard.jsx`, `RecommendationList.jsx`, `frontend/src/sample/recommendations_p1.json`

**Spec (one card):**
- Rank badge (#1 gets a "Best move" ribbon)
- Title ("Buy out your Corolla") + vehicle label
- Big number: `monthly_payment`/mo, with `delta_monthly` as "+$10/mo vs today" (green if ≤ 0, amber if > 0)
- Secondary row: upfront cost, term, total cost
- Explanation paragraph (2–3 sentences from the API)
- Trade-offs as 1–3 bullets
- Action button, styled by `action.kind`: `self_service` = solid red, `follow_up` = outline, `offer` = solid black with an "Offer" tag
- "Why this?" link (opens the NM-20 drawer; a no-op for now)

The list shows the top 3 `recommendations`. Below it, a muted line: "We also considered N other options" (leads to NM-22).

**Tasks:**
- [x] Write `recommendations_p1.json` by hand using the NM-5 option shape plus `rank` and `explanation`
- [x] Card + list components
- [x] Action button click → `alert()` / toast saying what would happen ("Buyout started — a TFS specialist will confirm within 1 business day")

**Acceptance criteria:**
- [ ] 3 cards render from the sample; the #1 card is visually dominant
- [x] Each action kind looks different
- [x] All fields come from JSON; nothing is hard-coded in JSX

**How to verify:** open p1's dashboard → 3 cards below the summary row.

**What changed (read this if you build on NM-10):**
- **Contract change:** `action` is now `{ kind, label, confirmation }`. `confirmation` is the toast text. Updated in `docs/contract.md`, `docs/sample_responses/recommendations_p1.json` and `frontend/src/sample/recommendations_p1.json` (the two samples are kept identical). Samu: `options.py` needs to emit it (task added to NM-5).
- **Layout:** #1 spans the full width (numbers on the left, explanation + action on the right) with a red border and a "Best move" ribbon; #2 and #3 sit side by side below. Everything is one column under 900px.
- **Components:** `RecommendationList({ recommendations, considered, onWhyThis })` shows the top 3 by `rank` and owns the toast. `RecommendationCard({ rec, top, onAction, onWhyThis })` renders one card. `Toast({ message, onDismiss })` is a reusable bottom-center toast that auto-dismisses after 4 s.
- **"We also considered N other options":** N = `considered` items whose `id` isn't in the top 3 (p1 → 1). It links to `#all-options`, a wrapper `<div>` around `<ComparisonTable>` in `Dashboard.jsx`.
- **Formatting:** `formatSignedWholeCurrency` in `format.js` rounds the delta to whole dollars (9.97 → "+$10"). The amber delta uses the new `--color-warning` / `--color-warning-bg` tokens. A `term_months` of 0 shows as "—".
- **Not done yet:** `previous_rank` ("↑ was #2") isn't rendered (NM-19), and "Why this?" is a no-op until NM-20 passes `onWhyThis`.

---

## Sprint 2 — One persona end to end (Sat 7:00 → 10:30 PM)

> **6 PM: someone attends the Toyota workshop (GDC 1.304).** Ask: (1) what makes a winning demo for them, (2) do they have sample data or real fee/APR ranges we should use, (3) which next steps (self-service vs follow-up) matter most to TFS. Post the answers in the team chat.

### NM-11 · Affordability guardrails + ranking `E1` `P0` · 3 pts · **Samu**
*As a customer, I only want recommendations I can actually afford, in a sensible order.*

**Context:** This is the responsible-AI core and the main judging point. The engine, not the LLM, decides what's affordable and what ranks first, and it always says why something was rejected.

**Blocked by:** NM-5

**Files:** `backend/engine/guardrails.py`, `backend/engine/recommend.py`, `backend/engine/tests/test_guardrails.py`

**Spec:**
```python
def check_affordability(option: dict, finances: dict, current_payment: float) -> tuple[bool, str | None]
def rank_options(options: list[dict], goals: list[str]) -> list[dict]
def recommend(profile: dict, life_event: dict | None = None) -> dict
    # the ONLY function Rodrigo's route calls → { "recommendations": [...top 3...], "considered": [...all...], "relief_needed": bool }
```
**Affordability rules** (an option fails if any rule fails; the first failing rule is the reason):
1. `monthly_payment ≤ PAYMENT_TO_INCOME_MAX × monthly_income` (15%), else "Payment would be X% of your income (limit 15%)"
2. `delta_monthly ≤ SURPLUS_SHARE_MAX × monthly_surplus` (50%), else "Adds $X/mo; your monthly surplus is $Y"
3. `savings − upfront_cost ≥ MIN_BUFFER_MONTHS × monthly_bills` (1 month), else "Upfront cost of $X would leave less than one month of bills in savings"

Rules 1–2 skip options that *lower* the payment (relief options, refinance).

**Relief mode:** `relief_needed = monthly_surplus < RELIEF_SURPLUS_MIN` ($0, i.e. the customer is short every month). Only then does NM-5 generate `extend_term` and `payment_deferral`. We don't push extensions on people who don't need them, since they cost more in total.

**Ranking (deterministic):**
1. Affordable options before unaffordable ones (unaffordable never rank in the top 3)
2. Options with `keeps_vehicle: false` go last unless `"no_car_needed"` is in goals
3. Options matching a customer goal come next (`newer_vehicle` → `trade_in_upgrade`/`return_new_lease`; `lower_payment` → `refinance`/`extend_term`; `more_space` → upgrades to a larger target)
4. Then by `effective_monthly`, ascending
5. Tie-break by `total_cost`, ascending

**Human handoff:** if `monthly_surplus < 0`, or no option passes affordability, the #1 recommendation becomes a synthetic `talk_to_advisor` card (`action.kind: follow_up`) and the real options follow it.

Every `considered` item gets `affordable: bool` and `rejection_reason: str | null`.

**Tasks:**
- [ ] Implement the 3 rules with human-readable reasons (numbers inside, formatted)
- [ ] Ranking function exactly as above
- [ ] `talk_to_advisor` card
- [ ] `recommend()` wiring: build options → check affordability → rank → top 3
- [ ] Tests for each rule, the handoff, and each persona's expected #1 (Appendix B)

**Acceptance criteria:**
- [ ] p1 → #1 `lease_buyout`, #2 `buy_miles_new_lease`, last `return_walk_away`; `return_new_lease` rejected by rule 3
- [ ] p2 → #1 `keep`, #2 `trade_in_upgrade` (Highlander, affordable at baseline)
- [ ] p3 → #1 `trade_in_upgrade` (goal `newer_vehicle`), #2 `refinance`, #3 `keep`
- [ ] Every rejected option has a non-empty `rejection_reason`

**How to verify:** `pytest backend/engine/tests -v`, then print `recommend(profile)` for each persona.

### NM-12 · Recommendations endpoint `E2` `P0` · 2 pts · **Rodrigo**
*As the frontend, I need ranked recommendations from one API call.*

**Context:** This is where the engine and the API meet. Keep the route thin: load the profile, call `recommend()`, attach explanations (NM-13), return. No math in the route.

**Blocked by:** NM-8, NM-11

**Files:** `backend/routes.py`

**Spec:** `POST /api/customers/<id>/recommendations`
- Body: `{ "life_event": null }` or `{ "life_event": { "type": "new_baby", "params": {} } }`
- Response: `{ recommendations, considered, relief_needed, life_event_applied }`, exactly the contract shape
- Invalid life event type → `400 { error, allowed: [...] }`
- Engine exceptions → `500 { error }`, logged with a traceback (never crash the demo)

**Tasks:**
- [ ] Route + body validation
- [ ] Call `engine.recommend.recommend(profile, life_event)`
- [ ] Call Jose's `services.llm.explain_all(recommendations, profile, life_event)` and copy `text` → `explanation`, `source` → `explanation_source` on each recommendation. Until NM-13 lands, Jose pushes a stub that returns template text, so this works from the start
- [ ] Also return `finances_after_event` (from Samu's `recommend()` output) so the finance snapshot can update during What-if
- [ ] Pass each option's `action` through unchanged, including `action.confirmation` (added by NM-10; the card shows it as the click toast)

**Acceptance criteria:**
- [ ] `curl -X POST .../p1/recommendations -H 'Content-Type: application/json' -d '{"life_event":null}'` returns 3 ranked recommendations with p1's numbers
- [ ] An invalid life event returns 400 with the allowed list

**How to verify:** the curl above, and compare against Samu's printed `recommend()` output.

### NM-13 · LLM explanations `E3` `P0` · 3 pts · **Jose**
*As a customer, I want a plain-English reason for each recommendation.*

**Context:** This is the only place AI is used, and it's limited to wording. It turns the option JSON into 2–3 friendly sentences. Judges should see that the AI explains and never decides.

**Blocked by:** NM-12. **Decide the LLM provider and get a key at the start of Sprint 2** (default: Gemini Flash, free tier, which also qualifies for MLH's Best Use of Gemini).

**Files:** `backend/services/llm.py`, `backend/prompts/explain.txt`

**Spec:**
```python
def explain_all(recommendations: list[dict], profile: dict, life_event: dict | None) -> dict[str, dict]
    # → { "<option_id>": { "text": "...", "source": "llm" | "template" } }   (this is the only function Rodrigo's route calls)
```
Push a stub of this function **first** (returning template text) so Rodrigo's NM-12 isn't blocked. Then send **one call per persona/event** with all top-3 options (cheaper and faster than one per card), asking for JSON output `{ "<option_id>": "<explanation>" }`.

Prompt rules (put them in `explain.txt`):
- You are explaining options already calculated by a financial engine. Do not calculate.
- Use **only** numbers that appear in the provided JSON, formatted the same way.
- 2–3 sentences, 8th-grade reading level, second person ("you").
- Mention exactly one trade-off.
- End by naming the action ("You can start the buyout online.").
- Never promise approval, never mention credit scores, never invent rates or offers.
- If an option was rejected, explain the reason kindly.

Pass the model only the fields it needs: title, monthly_payment, delta_monthly, upfront_cost, total_cost, tradeoffs, action.label, the customer's first name, and the life event.

**Tasks:**
- [ ] Provider client with a 6-second timeout
- [ ] Prompt file + JSON-mode parsing
- [ ] Replace the stub with the real call; NM-12's route doesn't change
- [ ] `.env`: `LLM_API_KEY`, `LLM_MODEL`

**Acceptance criteria:**
- [ ] p1's 3 cards show sensible explanations that use their numbers
- [ ] A timeout or error falls back to the template (NM-14) and the endpoint still returns 200

**How to verify:** call the endpoint for p1 and read the explanations out loud. Do they sound like a helpful TFS rep?

### NM-14 · Number validator + fallback `E3` `P0` · 2 pts · **Jose**
*As a responsible-AI feature, the LLM must never show a number we didn't compute.*

**Context:** This is our strongest demo line: "Our AI literally cannot make up a number." Any LLM sentence containing a number that isn't in the engine output gets thrown away and replaced by a deterministic template.

**Blocked by:** NM-13

**Files:** `backend/services/llm.py` (validator section), `backend/services/templates.py`, `backend/tests/test_validator.py`

**Spec:**
```python
def extract_numbers(text: str) -> set[float]      # handles $1,275 / 1,275.00 / 6.9% / 60-month
def allowed_numbers(option: dict) -> set[float]   # every numeric value in the option, incl. rounded variants (0 and 2 decimals)
def validate(text: str, option: dict) -> bool     # all extracted ⊆ allowed (ignore small integers 1–3 used as words, e.g. "2 options")
def template_explanation(option: dict) -> str     # "{title}: ${monthly_payment}/mo for {term_months} months. {tradeoffs[0]}. {action.label}."
```
Return `explanation_source: "llm" | "template"` on each recommendation (the UI can show a tiny badge in debug mode).

**Tasks:**
- [ ] Validator + template
- [ ] Tests, including a deliberately bad string ("only $199/mo at 2.9%") that must fail
- [ ] Log rejections (useful for the pitch: "we caught N hallucinations during testing")

**Acceptance criteria:**
- [ ] Bad string → rejected → template used
- [ ] Good LLM output → kept
- [ ] Endpoint never returns an empty explanation

**How to verify:** `pytest backend/tests/test_validator.py -v`

### NM-15 · Wire frontend to live API `E4` `P0` · 2 pts · **Jose**
*As a demo, the UI must show real engine output, not sample JSON.*

**Context:** This is the integration moment for Milestone M2. After this, everything on screen comes from the backend.

**Blocked by:** NM-8, NM-10, NM-12

**Files:** `frontend/src/api.js`, `frontend/vite.config.js` (proxy)

**Spec:**
- Vite proxy: `/api` → `http://localhost:5000` (avoids CORS issues and hard-coded hosts)
- `api.js` functions switch to `fetch`; keep the sample JSON as a fallback behind `VITE_USE_SAMPLE=true`
- Loading skeletons for the cards (recommendations may take 2–6 s with the LLM)
- Error state: "Couldn't load recommendations — retry" button

**Tasks:**
- [ ] Proxy + fetch calls
- [ ] Loading + error states (the card skeletons replace `<RecommendationList>` in `Dashboard.jsx` while loading)
- [ ] Remove any remaining hard-coded data from components
- [ ] Check that the live response carries `action.confirmation` (NM-10 contract change). If it doesn't, the toast quietly falls back to generic text, so check the wording on each card

**Acceptance criteria:**
- [ ] p1 flows picker → dashboard → live cards with LLM explanations
- [ ] Stopping Flask shows the error state, not a blank page

**How to verify:** run both servers, click through p1, then kill Flask and reload.

### NM-16 · Soft submission `E6` `P0` · 1 pt · **Rodrigo**
*As a team, we lock in a submission early so nothing can go wrong at 11:29 AM tomorrow.*

**Context:** The soft deadline is Sat 11:30 PM. A draft now means the final submission is just an edit.

**Blocked by:** nothing (submit whatever exists at 11 PM).

**Tasks:**
- [ ] Create the project on hacktx26.devpost.com, add Jose and Samu as teammates
- [ ] Name ("Next Move"), one-liner, 2 screenshots, GitHub link
- [ ] Select the Toyota track
- [ ] Placeholder sections: Inspiration / What it does / How we built it

**Acceptance criteria:**
- [ ] Submitted before **11:30 PM Saturday**, with all three of us listed

---

### NM-17 · Life events `E1` `P0` · 3 pts · **Samu**
*As a customer, I want to ask "what if?" and see my best move change.*

**Context:** The "What if?" simulator is our differentiator, and it creates the demo's key moment: the Reyes family's Highlander gets **rejected as unaffordable** after the baby.

**Blocked by:** NM-11

**Files:** `backend/engine/events.py`, `backend/engine/tests/test_events.py`

**Spec:**
```python
def apply_life_event(profile: dict, event: dict) -> dict   # returns a NEW profile (deep copy); never mutate
```

| `type` | `params` (defaults) | Effect on profile |
|---|---|---|
| `income_drop` | `{ "pct": 20 }` | `monthly_income × (1 − pct/100)`; recompute surplus |
| `new_baby` | `{ "monthly_cost": 500 }` | `monthly_spending + monthly_cost`; add goal `more_space`; add targets `highlander` |
| `longer_commute` | `{ "extra_miles_per_year": 6000 }` | `miles_per_year +=`; leases: re-project end miles; fuel cost rises |
| `job_change` *(P1)* | `{ "income_change_pct": 15 }` | income ± pct |
| `move` *(P1)* | `{ "extra_miles_per_year": 3000, "rent_change": 200 }` | miles and bills change |

`recommend()` applies the event before building options, and returns `life_event_applied` with a one-line human summary ("Income down 20% → monthly surplus now −$340").

**Tasks:**
- [ ] 3 P0 events (+2 P1 if time allows)
- [ ] Event summary string
- [ ] Tests per event against Appendix B's expected outcomes

**Acceptance criteria:**
- [ ] p2 + `new_baby` → surplus $900 → $400; Highlander (+$233/mo) **rejected** by rule 2 (limit $200); #1 is `keep`
- [ ] p2 + `income_drop` 20% → surplus −$340 → `relief_needed` → #1 `talk_to_advisor`, followed by `extend_term` (≈ $439.52) and `payment_deferral`
- [ ] p1 + `longer_commute` → overage grows to 7,100 mi; `buy_miles_new_lease` becomes rejected (rule 3); buyout stays #1
- [ ] The original profile object is unchanged after `apply_life_event`

**How to verify:** `pytest backend/engine/tests/test_events.py -v`

> NM-17 sits in Sprint 2 so Samu's evenings are balanced: it only needs NM-11, and finishing it early unblocks the What-if panel and persona tuning.

---

## Sprint 3 — Full MVP (Sat 10:30 PM → Sun 3:00 AM)

### NM-18 · Tune personas `E1`+`E2` `P0` · 2 pts · **Rodrigo + Samu**
*As a demo, each persona must tell a clean, believable story.*

**Context:** Appendix B's numbers were pre-checked, but real implementations drift (rounding, fees, mock-data noise). This story is the end-to-end check that the engine, the data and the demo script agree.

**Blocked by:** NM-11, NM-17, NM-7

**Files:** `backend/data/toyota_profiles.json`, `backend/data/mock_bank/*.json`, `backend/engine/tests/test_personas.py`

**Tasks:**
- [ ] Integration test: for every row of the Appendix B "expected outcomes" table, assert the #1 option id
- [ ] If an assertion fails, adjust **data**, not rules (change the constants only if the data can't fix it, and tell the team)
- [ ] Sanity-read every explanation for every persona/event combo

**Acceptance criteria:**
- [ ] `test_personas.py` passes for all 8 persona/event combinations in Appendix B
- [ ] Each persona's #1 card matches the demo script (plan §12)

### NM-19 · What-if panel `E4` `P0` · 3 pts · **Samu**
*As a customer, I want to try a life change and instantly see how my best move changes.*

**Context:** This is the most interactive part of the demo. It should feel instant (the cache from NM-21 helps) and make the change obvious.

**Blocked by:** NM-15, NM-17

**Files:** `frontend/src/components/WhatIfPanel.jsx` (yours; Jose's `Dashboard.jsx` already holds the `lifeEvent` state and passes `value`, `onChange`, `summary`), plus `backend/engine/recommend.py` for the `previous_rank` field

**Spec:**
- A row of chips: 👶 New baby · 📉 Income drop · 🚗 Longer commute (+ Job change, Move if NM-17's P1 is done)
- Income drop shows a slider (10–40%, default 20); other events use defaults
- Selecting a chip → `getRecommendations(id, lifeEvent)` → cards re-render; "Reset" clears it
- Banner above the cards with `life_event_applied` ("Income down 20% → monthly surplus now −$340")
- Changed-rank indicator: when a life event is applied, `recommend()` adds `previous_rank` (baseline rank, or `null` if new) to each recommendation; Jose's card renders "↑ was #2" / "New" from it (one line on his side, in the `rec-head` row of `RecommendationCard.jsx`; tell him when the field lands)
- Finance snapshot reflects the event: `recommend()` returns `finances_after_event`; Jose's `FinanceSnapshot` shows it when present

**Tasks:**
- [ ] Chips + slider + reset
- [ ] Re-fetch with debounce (300 ms on the slider)
- [ ] Banner showing `summary` (rendered inside `WhatIfPanel`)
- [ ] `previous_rank` + `finances_after_event` in `recommend()` output, with tests

**Acceptance criteria:**
- [ ] Works for all 3 personas
- [ ] p2 → New baby shows the Highlander moving to "considered — not affordable" and `keep` as #1
- [ ] Reset returns exactly to the baseline cards

**How to verify:** run the demo script's p2 segment end to end.

### NM-20 · "Why this?" + assumptions drawer `E4` `P0` · 2 pts · **Jose**
*As a customer, I want to see exactly what the recommendation assumes, and reach a human anytime.*

**Context:** Transparency is the second half of our responsible-AI story. Every number has a visible assumption behind it.

**Blocked by:** NM-15

**Files:** `frontend/src/components/WhyDrawer.jsx`, `frontend/src/components/HumanHandoff.jsx`

**Spec:**
- Clicking "Why this?" on a card opens a side drawer with:
  - Full explanation
  - Assumptions table (from `option.assumptions`): APR, term, residual/value, fees, source ("synthetic")
  - "How we calculated this": monthly payment = …, effective monthly = payment + fuel + upfront/12 (static text from the plan)
  - "Calculated by our finance engine · explained by AI · AI cannot change numbers"
- A persistent "Talk to a TFS specialist" button in the header on every screen → modal with fake scheduling (pick a time slot → confirmation toast)

**Already in place from NM-10:** every card's "Why this?" button calls `onWhyThis(rec)` with the full option (`explanation`, `assumptions`, numbers). Hold the selected option in `Dashboard.jsx` and pass `onWhyThis` to `<RecommendationList>`. For the handoff's confirmation toast, reuse `components/Toast.jsx` (`message`, `onDismiss`).

**Tasks:**
- [ ] Drawer component
- [ ] Handoff button + modal

**Acceptance criteria:**
- [ ] Every card's drawer shows its own assumptions
- [ ] The handoff is reachable from every screen in one click

### NM-21 · Explanation cache `E3` `P0` · 1 pt · **Jose**
*As a demo, nothing may depend on Wi-Fi or LLM latency during judging.*

**Context:** Judging is in a crowded hall with bad Wi-Fi. A cached demo is instant and identical every time.

**Blocked by:** NM-14

**Files:** `backend/services/cache.py`, `backend/scripts/warm_cache.py`, `backend/cache/*.json` (committed)

**Spec:**
- Cache key: `f"{customer_id}:{life_event_type or 'none'}:{params_hash}"` → the explanations dict
- `warm_cache.py` calls every persona × event combo from Appendix B and saves the results
- `CACHE_ONLY=true` env var: never call the LLM, read the cache only (template if missing)

**Tasks:**
- [ ] Disk cache read/write
- [ ] Warm script
- [ ] Commit the warmed cache files

**Acceptance criteria:**
- [ ] With Wi-Fi off and `CACHE_ONLY=true`, every demo path shows LLM-written explanations
- [ ] Cached responses return in < 200 ms

### NM-22 · Comparison table `E4` `P1` · 2 pts · **Rodrigo**
*As a customer, I want to see every option the app considered, including the ones it rejected, and why.*

**Context:** This proves the engine compared everything, not just the winners. It's especially powerful in the p2 "new baby" moment.

**Blocked by:** NM-15

**Files:** `frontend/src/components/ComparisonTable.jsx`

**Spec:** a collapsible section "All options we considered (N)". Columns: Option · Monthly · Δ vs today · Upfront · Total · Status. Status is a green "Affordable" or a gray "Not recommended" with `rejection_reason` as a tooltip or second line. Sorted by rank.

**From NM-10:** the cards' "We also considered N other options" link points to `#all-options`, a `<div>` that `Dashboard.jsx` already wraps around `<ComparisonTable>`, so you don't need to add an id. `considered` includes the top 3 as well as the rejected options. Rejected items carry only `id, title, monthly_payment, delta_monthly, upfront_cost, total_cost, affordable, rejection_reason` (no `rank`), so sort them after the ranked ones.

**Acceptance criteria:**
- [ ] Shows every `considered` item, with reasons for rejected ones
- [ ] Updates with the What-if panel

---

## Sprint 4 — Polish + stretch (Sun 3:00 → 8:30 AM)

### NM-23 · Equity / payment chart `E4` `P1` · 3 pts · **Rodrigo**
*As a customer, I want to see when my car is worth more than I owe.*

**Context:** Feeds the "Equity tracker" feature from our pitch. It's visual proof of why p3 should upgrade now.

**Blocked by:** NM-8 for the backend half (**start it in Sprint 2** while waiting on NM-11), and NM-15 for the chart. Rodrigo owns both halves; ask Samu to review the amortization use.

**Files:** `frontend/src/components/EquityChart.jsx`; backend: `services/equity.py` (`equity_timeline`, built on Samu's `engine.finance` functions), `routes.py` (add `equity_timeline` to the dashboard response)

**Spec:**
- Backend: `equity_timeline(profile, months=24) -> [{ month, value, payoff }]` (value depreciates at `DEPRECIATION_PER_YEAR`, payoff from the amortization schedule)
- Recharts `LineChart`: two lines (value, payoff), shaded area between them (green where value > payoff), a "Today" marker
- Lease customers: plot residual vs estimated value instead

**Acceptance criteria:**
- [ ] p3's chart clearly shows positive equity today
- [ ] Renders for all 3 personas without errors

### NM-24 · UI polish pass `E4` `P1` · 3 pts · **Jose**
*As judges, we should think "this could ship".*

**Tasks:**
- [ ] Consistent spacing and typography; Toyota-inspired palette (no official logos; use a text wordmark "Next Move")
- [ ] Empty, loading and error states on every screen
- [ ] Favicon, page titles, a nice persona-picker header
- [ ] Check at 1280×800 and on the projector resolution (1920×1080)
- [ ] Remove console errors and warnings

**Acceptance criteria:**
- [ ] No console errors on the full demo path
- [ ] A teammate who hasn't seen the UI can complete the demo path without help

### NM-25 · Live Nessie `E5` `P2` · 5 pts · **Rodrigo**
*As the Capital One track, the financial profile comes from real Nessie calls.*

**Context:** Only worth doing if Nessie is reachable. It qualifies us for Capital One's Best Use of Nessie ($250 per member), using the adapter built in NM-7.

**Blocked by:** NM-7, and Nessie being reachable (confirm the base URL with Capital One in the WEL hallway or on Discord)

**Files:** `backend/services/nessie.py`, `backend/scripts/seed_nessie.py`, `backend/data/nessie_ids.json`

**Spec:**
- Base URL from `.env` (`NESSIE_BASE_URL`); key from `NESSIE_KEY`, passed as `?key=`
- `seed_nessie.py`: for each persona, `POST /customers` → `POST /customers/{id}/accounts` (checking + savings) → `POST /accounts/{id}/deposits`, `/purchases`, `/bills` from the mock files; save the returned Nessie ids to `nessie_ids.json`
- `nessie.py`: `GET /customers/{id}/accounts`, `/accounts/{id}/deposits`, `/purchases`, `/bills` → the same normalization as NM-7
- Map our `customer_id` (p1) → Nessie id via `nessie_ids.json`
- 5-second timeout; on failure, fall back to mock and set `source: "mock (Nessie unavailable)"`

**Acceptance criteria:**
- [ ] `DATA_MODE=nessie` → the dashboard shows `source: "nessie"` with the same normalized numbers as mock (±$5)
- [ ] Unplugging the network still renders (fallback)

### NM-26 · Spanish toggle `E3`+`E4` `P2` · 3 pts · **Jose**
*As a Spanish-speaking customer, I want the app and explanations in Spanish.*

**Files:** `frontend/src/i18n.js`, `backend/prompts/explain.txt`

**Spec:**
- EN/ES toggle in the header; UI strings in a simple dictionary
- `?lang=es` passed to the recommendations endpoint → the LLM explains in Spanish (numbers unchanged; the validator still applies, using Spanish number formats)
- Warm the cache for `es` as well

**Acceptance criteria:**
- [ ] The full demo path works in Spanish with cached explanations

### NM-27 · Recall card `E2` `P2` · 2 pts · **Rodrigo**
*As a customer, I want to know if my car has an open safety recall.*

**Files:** `backend/services/recalls.py`, `backend/data/recalls_cache.json`

**Spec:**
- NHTSA Recalls API: `https://api.nhtsa.gov/recalls/recallsByVehicle?make=TOYOTA&model={model}&modelYear={year}` (no key needed)
- Cache responses to disk (demo-safe)
- If any recalls exist, add a `recall_service` card (`action.kind: follow_up`, "Book a free recall repair") pinned above the rankings. It's safety, not a financial option.

**Acceptance criteria:**
- [ ] Works offline from cache
- [ ] Shows the real recall title and NHTSA campaign number

### NM-28 · Engine hardening `E1` `P1` · 2 pts · **Samu**
*As a demo, the engine must never crash, whatever the slider says.*

**Tasks:**
- [ ] Edge cases: 0 months remaining, negative equity on trade-in (roll the negative equity into the new loan and say so in trade-offs), zero/negative surplus, income drop of 40%+, missing optional fields
- [ ] Fuzz test: random life-event params for all personas; assert no exceptions and that all numbers are finite
- [ ] Round money to 2 decimals at the API boundary only

**Acceptance criteria:**
- [ ] Fuzz test runs 500 random cases with no exceptions

---

## Sprint 5 — Ship (Sun 8:30 → 11:30 AM)

### NM-29 · Code freeze `E6` `P0` · **All**
*As a team, we stop adding features so the demo is stable.*

**Context:** 10:30 AM. After this, only bug fixes go in, and each one needs a second person's quick OK.

**Tasks:**
- [ ] Merge all open PRs or close them
- [ ] Re-warm the cache (NM-21) from `main`
- [ ] Tag `v1.0`
- [ ] Every teammate pulls `v1.0` and runs the demo path on their own laptop (backup machines)

**Acceptance criteria:**
- [ ] The demo runs from a clean clone with `CACHE_ONLY=true` on at least 2 laptops

### NM-30 · Demo video `E6` `P0` · 3 pts · **Rodrigo**
*As judges reviewing Devpost, we can see the product in under 2 minutes.*

**Blocked by:** NM-19, NM-20

**Spec:** follow the plan's §12 script. Screen recording (QuickTime / OBS) at 1080p, with voice-over. Upload to YouTube as unlisted.
- 0:00 Hook → 0:15 Maya (lease end, buyout) → 0:45 Reyes (new baby → Highlander rejected) → 1:20 Daniel (equity → upgrade) → 1:40 responsible AI (validator, assumptions) → 1:50 business value

**Acceptance criteria:**
- [ ] ≤ 2:00, audio clear, link added to Devpost

### NM-31 · Devpost final `E6` `P0` · 2 pts · **Jose (all review)**
*As a team, our submission explains the product clearly to judges who haven't seen the demo.*

**Blocked by:** NM-30

**Tasks:**
- [ ] **Inspiration:** customers face lease-end and payment decisions alone and default to calling support
- [ ] **What it does:** personas, ranked recommendations, What-if, equity, human handoff
- [ ] **How we built it:** React + Recharts, Flask, a deterministic finance engine with tests, LLM explanations behind a number validator, synthetic TFS data + Nessie-shaped banking data
- [ ] **Challenges:** Nessie downtime → adapter pattern; keeping the AI from inventing numbers
- [ ] **What's next:** real TFS data, credit pre-qualification, push alerts when equity turns positive
- [ ] **Built with** tags; screenshots of every screen; video link; public repo
- [ ] Tracks: Toyota (+ Capital One if NM-25 is done, + Gemini MLH prize if used)

**Acceptance criteria:**
- [ ] Submitted before **11:30 AM Sunday**; all 3 teammates confirm they're listed

### NM-32 · Pitch prep `E6` `P0` · 2 pts · **All**
*As presenters, each of us can deliver the demo confidently, alone if needed.*

**Tasks:**
- [ ] 5-slide deck (**Samu leads**, everyone reviews): Problem · Demo · Responsible AI (engine decides, AI explains, validator) · Business value (retention, upgrade revenue, fewer calls) · Team
- [ ] Each person rehearses the 2-minute pitch once out loud
- [ ] Prepare answers: "Where does the data come from?", "What if the LLM is wrong?", "How would TFS deploy this?", "Why these affordability thresholds?"
- [ ] Laptop setup for judging: charger, `CACHE_ONLY=true`, browser zoom tested, tabs pre-opened

**Acceptance criteria:**
- [ ] Every teammate can give the pitch solo
- [ ] Judging starts at 2 PM in WEL; we're at our table by 1:45 PM

---

## Points per person (check balance)

| | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 | **P0/P1 total** | P2 stretch |
|---|---|---|---|---|---|---|---|
| **Samu** | NM-4, NM-5 (8) | NM-11, NM-17 (6) | NM-19, NM-18* (5) | NM-28 (2) | pitch deck lead | **21** | — |
| **Rodrigo** | NM-6, NM-7, NM-8 (8) | NM-12, NM-16 + start NM-23 backend (3) | NM-18*, NM-22 (4) | NM-23 (3) | NM-30 (3) | **21** | NM-25, NM-27 (7) |
| **Jose** | NM-9, NM-10 (8) | NM-13, NM-14, NM-15 (7) | NM-20, NM-21 (3) | NM-24 (3) | NM-31 (2) | **23** | NM-26 (3) |

\* NM-18 is shared: Rodrigo leads (it's data), Samu supports (it's engine expectations). Counted for both.

Shared by everyone: NM-29 (code freeze) and NM-32 (pitch prep).

Whoever finishes a sprint early pulls the next P0 story from another epic before touching any P2.

---

## Appendix A — Shared constants (`backend/engine/constants.py`)

All values are **synthetic demo assumptions**, shown to users as such. Change them only via a PR that tells the whole team.

| Constant | Value | Used for |
|---|---|---|
| `OVERAGE_RATE_PER_MILE` | 0.25 | Lease over-mileage fee |
| `PREPAID_MILES_RATE` | 0.15 | Buying miles before lease end (synthetic TFS offer) |
| `DISPOSITION_FEE` | 395 | Returning a lease |
| `PURCHASE_OPTION_FEE` | 300 | Lease buyout |
| `USED_AUTO_APR` | 6.9 | Financing a buyout |
| `NEW_AUTO_APR` | 5.9 | Financing a new vehicle (trade-in) |
| `REFI_APR` | 6.4 | Refinance rate |
| `NEW_LEASE_MONEY_FACTOR` | 0.00200 | New lease (≈ 4.8% APR) |
| `NEW_LEASE_TERM` | 36 | New lease months |
| `BUYOUT_TERM` | 60 | Buyout financing months |
| `NEW_TERM` | 60 | New vehicle loan months |
| `EXTENSION_MONTHS` | 12 | Term extension |
| `DEFERRAL_MONTHS` | 2 | Payment deferral |
| `FUEL_PRICE` | 3.00 | $/gallon (Texas) |
| `DEPRECIATION_PER_YEAR` | 0.12 | Equity timeline |
| `PAYMENT_TO_INCOME_MAX` | 0.15 | Guardrail rule 1 |
| `SURPLUS_SHARE_MAX` | 0.50 | Guardrail rule 2 |
| `MIN_BUFFER_MONTHS` | 1 | Guardrail rule 3 |
| `RELIEF_SURPLUS_MIN` | 0 | Relief mode trigger (surplus below this) |

**Vehicle catalog (`vehicle_catalog.json`, synthetic prices):**

| id | Label | MSRP | MPG | Lease residual % |
|---|---|---|---|---|
| `corolla_le_2027` | 2027 Corolla LE | 23,500 | 35 | 62% |
| `rav4_xle_2022` | 2022 RAV4 XLE | — | 30 | — |
| `highlander_xle_2027` | 2027 Highlander XLE | 45,500 | 25 | 58% |
| `camry_se_2021` | 2021 Camry SE | — | 32 | — |
| `camry_hybrid_se_2027` | 2027 Camry Hybrid SE | 32,500 | 51 | 60% |
| `corolla_le_2023` | 2023 Corolla LE | — | 35 | — |

## Appendix B — Personas (exact numbers)

### p1 — Maya Lopez · "College senior · Corolla lease ending · over on miles"
- **Goals:** `["keep_a_car_after_graduation"]` · **Miles/year:** 11,700
- **Vehicle:** 2023 Corolla LE (`corolla_le_2023`), 31,200 mi, est. value **$18,900**
- **Contract:** lease · cap cost $22,500 · residual **$14,600** · MF 0.00175 · 36 mo · **32 elapsed / 4 remaining** · payment **$284.37** · allowed 30,000 mi total
- **Projected:** 35,100 mi at lease end → **5,100 over → $1,275 fee**
- **Finances:** income **$2,100** · bills **$1,150** (incl. car) · spending **$520** · surplus **$430** · savings **$2,600** · checking $640

### p2 — The Reyes family · "Expecting a baby · financed RAV4"
- **Goals:** `["keep_payments_predictable"]` · **Miles/year:** 13,000 · **Targets:** `["highlander_xle_2027"]`
- **Vehicle:** 2022 RAV4 XLE, 41,000 mi, est. value **$24,000**
- **Contract:** loan · $30,000 at **4.9%** · 60 mo · **22 paid / 38 remaining** · payment **$564.76** · payoff **≈ $19,841** → equity **≈ +$4,159**
- **Finances:** income **$6,200** · bills **$3,600** (incl. car) · spending **$1,700** · surplus **$900** · savings **$9,000** · checking $2,100

### p3 — Daniel Kim · "Positive equity · high-APR Camry loan"
- **Goals:** `["newer_vehicle", "lower_fuel_cost"]` · **Miles/year:** 12,000 · **Targets:** `["camry_hybrid_se_2027"]`
- **Vehicle:** 2021 Camry SE, 48,000 mi, est. value **$21,000**
- **Contract:** loan · $22,000 at **9.9%** · 72 mo · **36 paid / 36 remaining** · payment **$406.46** · payoff **≈ $12,615** → equity **≈ +$8,385**
- **Finances:** income **$6,500** · bills **$2,800** (incl. car) · spending **$1,500** · surplus **$2,200** · savings **$15,000** · checking $3,400

### Expected outcomes (NM-18 asserts these)

| Persona + event | Key numbers | Expected #1 | Notes |
|---|---|---|---|
| p1 baseline | buyout $294.34 (+$9.97) · buy-miles upfront $1,160 · return upfront $1,670 | `lease_buyout` | `return_new_lease` rejected (rule 3: $2,600 − $1,670 < $1,150) |
| p1 + longer_commute | +2,000 projected miles → 7,100 over · buy-miles upfront $1,460 | `lease_buyout` | Buy-miles now **rejected** too (rule 3: $2,600 − $1,460 < $1,150) |
| p2 baseline | keep $564.76 · Highlander ≈ $797.33 (+$233) | `keep` | Highlander affordable (#2); no refinance (4.9% < 6.4%) |
| p2 + new_baby | surplus $900 → $400 | `keep` | Highlander **rejected** (rule 2: $233 > $200) ← demo moment |
| p2 + income_drop 20% | surplus → −$340 | `talk_to_advisor` | Then `extend_term` ≈ $439.52, `payment_deferral` |
| p3 baseline | trade-in ≈ $465.09 (+$59, −$35 fuel) · refi ≈ $386.06 | `trade_in_upgrade` | Goal `newer_vehicle`; refi #2, keep #3 |
| p3 + income_drop 20% | surplus $2,200 → $900 | `trade_in_upgrade` | Still affordable; shows resilience |
| p3 + longer_commute | fuel savings grow | `trade_in_upgrade` | Hybrid advantage widens |
