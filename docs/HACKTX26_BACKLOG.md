# Next Move — Scrum Backlog (HackTX 26)

> **Product goal:** A Toyota customer opens the app and gets their smartest next move, with real numbers, a plain-English why, and one clear action.
> **Team:** Samu (Engine + decision UX) · Rodrigo (Data + backend + data viz) · Jose (AI + frontend core)
> **Full plan & API contract:** `HACKTX26_PLAN.md` · **Shared numbers:** see the Appendix at the bottom of this file
>
> **Status (Sat 9:45 PM):** Sprints 0–1 ✅ · **Sprint 2 in progress** · Done: NM-4 to NM-14, NM-16, NM-17, NM-18 · NM-23 backend done (chart waits on NM-15)

---

## How we work

**Sprints** are short timeboxes that end at a milestone. Each sprint ends with a 5-minute **stand-up**: what I finished, what I'm doing next, what's blocking me.

| Sprint | Timebox | Sprint goal | Ends with |
|---|---|---|---|
| ✅ **Sprint 0** | Sat 3:00 → 3:45 PM | Everyone can code without blocking anyone | **Done** — skeleton pushed, contract agreed |
| ✅ **Sprint 1** | Sat 3:45 → 7:00 PM | Each layer works on its own | Stand-up 7 PM |
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
| **Rodrigo** | Data + backend + data viz | `backend/app.py`, `backend/routes.py`, `backend/requirements.txt`, `backend/data/**`, `backend/services/profile.py`, `customer_profile.py`, `nessie.py`, `equity.py`, `recalls.py`, `backend/scripts/seed_nessie.py`, `check_data.py`, `generate_mock_bank.py`, `backend/tests/test_profile.py` · `frontend/src/components/ComparisonTable.jsx`, `EquityChart.jsx` |
| **Jose** | AI + frontend core | `backend/services/llm.py`, `templates.py`, `cache.py`, `backend/prompts/**`, `backend/scripts/warm_cache.py`, `backend/cache/**` · `frontend/package.json`, `App.jsx`, `api.js`, `pages/**`, `styles/**`, and every other component |

**Why this split:** Samu owns the decision logic *and* the UI that exposes it (What-if), Rodrigo owns everything data from raw JSON to API to charts, and Jose owns the AI layer and the app shell everything plugs into.

**Cross-owner seams (agree on these, then never touch each other's files):**
- **Engine → API:** Rodrigo's route calls only `engine.recommend.recommend(profile, life_event) -> dict` (Samu).
- **API → LLM:** Rodrigo's route calls only `services.llm.explain_all(recommendations, profile, life_event) -> dict[option_id, {"text", "source"}]` (Jose).
- **Data → Engine:** `services.customer_profile.build_profile(customer_id)` (Rodrigo) builds the profile the engine takes. Engine tests can use it instead of hand-typed fixtures.
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

### ✅ NM-4 · Core finance math `E1` `P0` · 3 pts · **Samu**
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
- [x] Create `constants.py` with the full Appendix A table
- [x] Implement the 8 functions above with docstrings
- [x] Unit tests using the reference values below
- [x] Edge cases: APR 0, term 1, payments_made == term (balance ≈ 0), negative equity

**Acceptance criteria:**
- [x] `pytest backend/engine/tests/test_finance.py` passes
- [x] Reference values match to the cent (±$0.01):
  - `loan_payment(30000, 4.9, 60)` → **564.76**
  - `loan_balance(30000, 4.9, 60, 22)` → **≈ 19,841**
  - `loan_payment(22000, 9.9, 72)` → **406.46**
  - `lease_payment(22500, 14600, 0.00175, 36)` → **284.37**
  - `mileage_overage_fee(35100, 30000, 0.25)` → **1,275.00**

**How to verify:** run pytest, and paste one case into an online loan calculator (e.g. bankrate.com) as a sanity check.

**Done (Samu, merged into `dev`):** `constants.py`, `finance.py` and `test_finance.py`. Every reference value above is asserted and passes on `dev` (564.76, ≈19,841, 406.46, ≈12,615, 284.37, 35,100, 1,275.00, 294.34, 93.75), plus the edge cases (APR 0, final payment, bad input).
- Since `5b72de3` (Rodrigo), `VEHICLE_CATALOG` is loaded from `backend/data/vehicle_catalog.json`, so car specs have one source of truth. The rate, fee and guardrail constants still live in `constants.py`.

### ✅ NM-5 · Option builder `E1` `P0` · 5 pts · **Samu**
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
- [x] Lease option generators (4)
- [x] Loan option generators (5), relief options behind a flag
- [x] Trade-offs: 1–3 short strings per option, written from the numbers (no LLM)
- [x] Assumptions dict on every option
- [x] `action.confirmation` on every option: one customer-facing sentence about what happens next, no numbers (added by NM-10; see the p1 sample for wording)
- [x] Tests per persona (use the fixtures in Appendix B)

**Acceptance criteria:**
- [x] p1 produces `lease_buyout` at **$294.34/mo** and `buy_miles_new_lease` with upfront **$1,160** *(the new-lease payment is now $310.40 after the 2027 Corolla MSRP change in `7682bff`)*
- [x] p2 produces `keep` at **$564.76** and `trade_in_upgrade` (Highlander) at **≈ $797.33**, and **no** `refinance` (4.9% < 6.4%)
- [x] p3 produces `refinance` at **≈ $386.06**, `trade_in_upgrade` (Camry Hybrid) at **≈ $465.09**, equity used **≈ $8,385**
- [x] Every option has all fields in the shape above (a test asserts the keys)

> **Changed in NM-18:** the 2027 Corolla MSRP is now 22,500, so p1's new lease (`buy_miles_new_lease` / `return_new_lease`) is **$310.40/mo** (was $324.20). `test_options.py` was updated to match.

**How to verify:** `pytest backend/engine/tests/test_options.py -v` and print the options for each persona.

**Done (Samu, merged into `dev`):** `options.py` builds all 9 option kinds through a single `_option()` factory, and `engine/tests/fixtures.py` holds the 3 personas in the dashboard shape. Covered by `test_options.py`.
- **ids:** options carry `kind` (the type: use it for logic and tests) and `target` (catalog id or `null`). `id` is `kind` or `kind:target` (e.g. `trade_in_upgrade:highlander_xle_2027`), so ids are unique.
- **p1's new-lease payment is now $310.40, not $324.20.** `7682bff` (Rodrigo) lowered the 2027 Corolla MSRP to $22,500. Upfront costs are unchanged ($1,160 prepaid miles, $1,670 return).
- **Relief options** (`extend_term`, `payment_deferral`) are only generated with `include_relief=True`. `payment_deferral` gets a first-year average `effective_monthly`, so a $0 payment never looks "free" in the ranking.
- **Longer commute (NM-17):** lease projections add `extra_miles_per_year × months_remaining / 12`.

### ✅ NM-6 · Synthetic Toyota data `E2` `P0` · 3 pts · **Rodrigo**
*As a demo, we need 3 believable customers whose data produces the story we want to tell.*

**Context:** TFS has no public API, so the challenge explicitly asks for synthetic data. These files are the Toyota side of every persona. The numbers below were checked so each persona lands on its intended top move. Copy them exactly, and change them only together with Samu (NM-18).

**Blocked by:** nothing. Start immediately.

**Files:** `backend/data/toyota_profiles.json`, `backend/data/vehicle_catalog.json`, `backend/data/offers.json`, `backend/scripts/check_data.py`

**Spec:**
- `toyota_profiles.json`: an array with one object per persona: `customer_id`, `name`, `tagline`, `goals`, `vehicle`, `contract`, `miles_per_year`, `vehicle_targets` (model keys from the catalog). All values are in **Appendix B**.
- `vehicle_catalog.json`: keyed by model id → `{ "label", "msrp", "mpg", "lease_residual_pct" }`. Values are in **Appendix A**.
- `offers.json`: 2–3 synthetic offers (e.g. "Loyalty: 0.5% APR reduction on a new Toyota", "Prepaid miles at $0.15/mi before lease end"), each `{ id, title, applies_to, terms, disclaimer: "Synthetic offer for demo purposes" }`.

**Tasks:**
- [x] Write the 3 JSON files from Appendix A and B
- [x] Add `"source": "synthetic"` at the top level of each file
- [x] Load-test: `backend/scripts/check_data.py`

**Acceptance criteria:**
- [x] Every field used by the contract's `vehicle` and `contract` objects exists for p1, p2 and p3
- [x] The values match Appendix B exactly (except the 2027 Corolla MSRP, changed in NM-18)
- [x] The files parse with `json.load` without errors

**How to verify:** `python3 backend/scripts/check_data.py`

**What changed / what to know (read this if you build on NM-6):**
- **Structure:** each file is `{ "source": "synthetic", "<main key>": ... }` → `profiles` (list), `vehicles` (keyed by model id), `offers` (list).
- **The catalog has more fields than the spec:** `label, year, model, trim, msrp, mpg, lease_residual_pct`. Cars customers already own have `msrp` and `lease_residual_pct` set to `null`. `lease_residual_pct` is a decimal (0.62, not 62).
- **The catalog is the single source of truth:** since NM-18, `engine/constants.py` loads `VEHICLE_CATALOG` from this JSON. Change car data **only here**.
- **Profiles store raw inputs only** (`cap_cost`, `money_factor`, `principal`, `payments_made`, …). Computed values (payoff, lease APR, projected miles, equity) are calculated in NM-8, never stored. Key names match the contract: `est_value`, `miles_allowed_total`. The car is referenced by `vehicle.model_id`.
- **Offers:** `applies_to` uses the engine's option kinds (`buy_miles_new_lease`, `trade_in_upgrade`, `lease_buyout`), and every rate in `terms` matches Appendix A. If a constant changes, update the offer text too.
- **`check_data.py`** checks the required profile keys and that every `model_id` and `vehicle_targets` entry exists in the catalog. Run it after any data change.

### ✅ NM-7 · Mock bank data + adapter `E2` `P0` · 3 pts · **Rodrigo**
*As the engine, I need one normalized financial profile no matter where the data comes from.*

**Context:** Nessie was unreachable at 3 PM. This story makes the app work without it: mock files shaped exactly like Nessie's responses, plus one adapter function. NM-25 later swaps in live Nessie by flipping an env var, and nothing else changes.

**Blocked by:** nothing (needs the persona numbers from Appendix B).

**Files:** `backend/data/mock_bank/p1.json`, `p2.json`, `p3.json`, `backend/scripts/generate_mock_bank.py`, `backend/services/profile.py`, `backend/tests/test_profile.py`

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
- [x] Generate the 3 mock files with a seeded script so the normalized totals match Appendix B within ±$5
- [x] Implement `get_financial_profile`
- [x] Unit tests: `backend/tests/test_profile.py` (5 tests)

**Acceptance criteria:**
- [x] p1 → income 2,100 · bills 1,149.37 · spending 520 · surplus 430.63 · savings 2,600
- [x] p2 and p3 match Appendix B the same way
- [x] `DATA_MODE` unset defaults to `mock`; `DATA_MODE=nessie` raises `NotImplementedError`; an unknown mode raises `ValueError`

**How to verify:** from `backend/`: `python -c "from services.profile import get_financial_profile as g; print(g('p1'))"` and `python -m pytest tests/test_profile.py -v`

**What changed / what to know (read this if you build on NM-7):**
- **Don't edit the mock files by hand.** Change the `PERSONAS` settings in `scripts/generate_mock_bank.py` and rerun it. `random.Random(customer_id)` makes the output identical every run.
- **Data window:** Jul 24 → Oct 23, 2026 (91 days). 6 biweekly paychecks; purchases are random amounts scaled to the exact 3-month spending total.
- **Bills include the car payment** as payee "Toyota Financial Services". Totals: p1 1,149.37 · p2 3,599.76 · p3 2,801.46.
- **The adapter is split for NM-25:** `load_mock_bank_data()` reads the file and `calculate_monthly_finances()` does the math. Live Nessie only needs a new loader; the math is reused.
- **Test layout:** non-engine tests live in `backend/tests/`; engine tests stay in `backend/engine/tests/`.

### ✅ NM-8 · Flask endpoints (read) `E2` `P0` · 2 pts · **Rodrigo**
*As the frontend, I need the persona list and a full dashboard payload from the API.*

**Context:** These two endpoints let the frontend switch off the sample JSON early (NM-15). The dashboard payload is also the exact input the engine takes, so it's the "profile" object everyone shares.

**Blocked by:** NM-6, NM-7

**Files:** `backend/app.py`, `backend/routes.py`, `backend/services/customer_profile.py`

**Spec:**
- `GET /api/personas` → `[{ customer_id, name, tagline }]`
- `GET /api/customers/<id>/dashboard` → `{ customer, vehicle, contract, finances, equity, goals }`, exactly the contract shape
  - `contract.payoff` comes from `engine.finance.loan_balance` (loans) or `residual` (leases)
  - `equity = { value, status: "positive" | "negative" }`
- Unknown id → `404 { "error": "customer not found" }`
- CORS enabled for `http://localhost:5173`

**Tasks:**
- [x] Flask app factory, CORS (`flask-cors`), JSON error handlers
- [x] Both routes, composed from `toyota_profiles.json` + `vehicle_catalog.json` + `get_financial_profile()`
- [x] Uses Samu's real `loan_balance` and `projected_end_miles` (no stub needed)
- [ ] **Keep these lines in `create_app()`** (added by Jose in NM-13): `from services.llm import warm_up` then `warm_up()`. Confirm they survived the NM-8 `app.py` rewrite. They open the LLM connection in the background at startup so the first recommendations request is fast. They do nothing without `LLM_API_KEY`
- [x] `backend/.env` needs `LLM_API_KEY` and `LLM_MODEL=gemini-3.5-flash-lite` for real explanations (see `.env.example`); without them the API still works and returns template text

**Acceptance criteria:**
- [x] `curl localhost:5000/api/personas` returns 3 personas
- [x] `curl localhost:5000/api/customers/p1/dashboard` has every key from `docs/sample_responses/dashboard_p1.json` (plus 3 extras, below)
- [x] `curl localhost:5000/api/customers/nope/dashboard` → 404 JSON

**How to verify:** run the three curls above. The frontend can also hit them from the browser without CORS errors.

**What changed / what to know (read this if you build on NM-8):**
- **`services/customer_profile.py` → `build_profile(customer_id)`** is the single place that builds a customer profile. It returns exactly the shape of the engine's `fixtures.py`, so **the engine and the dashboard share it**. Samu: engine tests can use `build_profile()` instead of hand-typed fixtures. `list_personas()` feeds `/api/personas`.
- **Dashboard = `build_profile()` + `equity` + `equity_timeline`.** Extra keys beyond the contract: `miles_per_year`, `vehicle_targets`, `vehicle.catalog_id`. The engine needs them; the UI can ignore them.
- **Computed fields:** lease `apr` = money factor × 2400 (4.2), lease `payoff` = residual, lease `miles_projected_at_end` via `projected_end_miles`; loan `payoff` via `loan_balance` (rounded to 2 decimals).
- **Error handling lives in `app.py`, not in routes:** `CustomerNotFound` → 404, Flask HTTP errors → JSON with their code, any other exception → logged traceback + `500 {"error": ...}`. Routes stay free of try/except.
- **Python 3.10+ is required** (the engine uses `str | None`). Create the venv with `python3.11 -m venv .venv`; macOS's built-in Python 3.9 crashes.
- **macOS:** if port 5000 returns 403, turn off System Settings → General → AirDrop & Handoff → AirPlay Receiver.

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

### ✅ NM-10 · Recommendation cards (static) `E4` `P0` · 3 pts · **Jose**
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
- [x] 3 cards render from the sample; the #1 card is visually dominant
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
- **Until NM-15:** every persona shows p1's sample cards (Maya's Corolla), because `api.js` returns `recommendations_p1.json` for all customers.

---

## Sprint 2 — One persona end to end (Sat 7:00 → 10:30 PM)

> **6 PM: someone attends the Toyota workshop (GDC 1.304).** Ask: (1) what makes a winning demo for them, (2) do they have sample data or real fee/APR ranges we should use, (3) which next steps (self-service vs follow-up) matter most to TFS. Post the answers in the team chat.

### ✅ NM-11 · Affordability guardrails + ranking `E1` `P0` · 3 pts · **Samu**
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
- [x] Implement the 3 rules with human-readable reasons (numbers inside, formatted)
- [x] Ranking function exactly as above
- [x] `talk_to_advisor` card
- [x] `recommend()` wiring: build options → check affordability → rank → top 3
- [x] Tests for each rule, the handoff, and each persona's expected #1 (Appendix B)

**Acceptance criteria:**
- [x] p1 → #1 `lease_buyout`, #2 `buy_miles_new_lease`; `return_new_lease` rejected by rule 3 *(`return_walk_away` is also rejected by rule 3, not ranked last; see the note below)*
- [x] p2 → #1 `keep`, #2 `trade_in_upgrade` (Highlander, affordable at baseline)
- [x] p3 → #1 `trade_in_upgrade` (goal `newer_vehicle`), #2 `refinance`, #3 `keep`
- [x] Every rejected option has a non-empty `rejection_reason`

> **Status after the NM-18 merge (found during NM-13):** `recommend(P1)` now returns `lease_buyout` #1 and `buy_miles_new_lease` #2 (the earlier rule 1 rejection is fixed), and the guardrails tests pass. Two things differ from the criteria above and from NM-10's 3-card p1 sample: p1 gets **2** recommendations, because `return_walk_away` is now rejected by rule 3 ("Upfront cost of $1,670 would leave $930 in savings, less than one month of bills ($1,150)"), and `return_new_lease` is rejected for the same reason. If the demo needs a third card for p1, that's a data or rule decision for Samu and Rodrigo. The cards and `RecommendationList` handle 2 cards fine. Reminder: the LLM repeats `rejection_reason` to the customer, so this wording is customer-facing.

**How to verify:** `pytest backend/engine/tests -v`, then print `recommend(profile)` for each persona.

**Done (Samu, merged into `dev`):** `guardrails.py` (`check_affordability`, `is_relief_needed`, `GOAL_MATCHES`, `rank_options`) and `recommend.py` (`recommend()`, the pinned `talk_to_advisor` card, `previous_rank`, `finances_after_event`). Covered by `test_guardrails.py`, and end to end by Rodrigo's `test_personas.py`.
- **Actual results on `dev`:** p1 → `lease_buyout`, `buy_miles_new_lease` (2 cards); `return_new_lease` **and** `return_walk_away` rejected by rule 3 ($930 left < $1,150 of bills). p2 → `keep`, `trade_in_upgrade`. p3 → `trade_in_upgrade`, `refinance`, `keep`. The first acceptance line expected `return_walk_away` last; it's rejected instead, which is intended (same $1,670 upfront).
- **Relief / handoff:** `relief_needed` when `monthly_surplus < 0` (`RELIEF_SURPLUS_MIN = 0`), and then `talk_to_advisor` is pinned at #1.
- **Open follow-up:** the rule 1 message still prints the percentage with no decimals, so a 15.4% payment reads "15% of your income (limit 15%)". It doesn't trigger for any persona today, but it's customer-facing through the LLM (see the NM-13 note). Fix: `{pct:.1f}%` in `check_affordability`.

### ✅ NM-12 · Recommendations endpoint `E2` `P0` · 2 pts · **Rodrigo**
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
- [x] Route + body validation (`read_life_event()`)
- [x] Call `engine.recommend.recommend(profile, life_event)`
- [x] Call Jose's `services.llm.explain_all(recommendations, profile, life_event)` and copy `text` → `explanation`, `source` → `explanation_source` on each recommendation
- [x] Also return `finances_after_event` (from Samu's `recommend()` output) so the finance snapshot can update during What-if
- [x] Pass each option's `action` through unchanged, including `action.confirmation` (added by NM-10; the card shows it as the click toast)
- [ ] `explain_all` (NM-13) is final and never raises; call it with `recommend()`'s top 3. **Round money once before calling it** so the text and the card show the same cents. Currently the route rounds *after*; fix: `result = round_money(recommend(profile, life_event))`, then call `explain_all`, then `return jsonify(result)`

**Acceptance criteria:**
- [x] `curl -X POST .../p1/recommendations -H 'Content-Type: application/json' -d '{"life_event":null}'` returns ranked recommendations with p1's numbers (**2 cards, not 3**: see NM-11 and NM-18)
- [x] An invalid life event returns 400 with the allowed list
- [ ] *(NM-13 end-to-end check)* with `LLM_API_KEY` set, the p1 response has `explanation_source: "llm"` on each card and the text uses p1's numbers; with the key unset or wrong, the response is still 200 and uses `"template"`. Use `gemini-3.5-flash-lite`: free tier is 5 requests per minute, so wait between curls

**How to verify:** the curl above, and compare against Samu's printed `recommend()` output.

**What changed / what to know (read this if you build on NM-12):**
- **Allowed events:** `ALLOWED_LIFE_EVENTS = ["new_baby", "income_drop", "longer_commute"]` in `routes.py`. Add `job_change` / `move` there if NM-17's P1 events ship.
- **A missing `params`** defaults to `{}` so the engine uses its defaults. A body that isn't JSON counts as no life event.
- **Rounding:** `round_money()` rounds every float to 2 decimals at the API boundary, **except keys in `NOT_MONEY_KEYS`** (`money_factor`, which would otherwise become 0.0). Add any other non-money decimal there.
- **Errors:** unknown customer → 404 and engine crash → logged 500, both handled by `app.py` (NM-8).
- **Verified:** p2 + `new_baby` → `keep` #1, Highlander rejected ("Adds $233/mo; your monthly surplus is $400 (limit $200)"); `life_event_applied` and `finances_after_event` are filled.

### ✅ NM-13 · LLM explanations `E3` `P0` · 3 pts · **Jose**
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
- [x] Provider client with a 6-second timeout
- [x] Prompt file + JSON-mode parsing
- [x] Replace the stub with the real call; NM-12's route doesn't change
- [x] `.env`: `LLM_API_KEY`, `LLM_MODEL`

**Acceptance criteria:**
- [x] p1's 3 cards show sensible explanations that use their numbers *(checked by calling `explain_all` directly on p1's options and on p2 + `new_baby`; the same check through the real endpoint is an NM-12 acceptance criterion)*
- [x] A timeout or error falls back to the template (NM-14) and the endpoint still returns 200 *(`explain_all` never raises; covered by `backend/tests/test_llm.py`; the endpoint part is an NM-12 acceptance criterion)*

**Other tasks affected by NM-13 (each has a note in its own section):** NM-8 and NM-12 (Rodrigo: `app.py` now calls `warm_up()`; round money before `explain_all`), NM-11 (Samu: p1 now gets 2 recommendations, not 3), NM-14 and NM-21 (Jose: validator hook, cache rules), NM-18 (check the explanations).

**How to verify:** call the endpoint for p1 and read the explanations out loud. Do they sound like a helpful TFS rep?

**What changed / what to know (read this if you build on NM-13):**
- **Setup:** put `LLM_API_KEY=<key>` (a Google AI Studio key, starts with `AIza`) and `LLM_MODEL=gemini-3.5-flash-lite` in `backend/.env`, with no quotes. The old default `gemini-2.5-flash` is no longer available to new accounts and returns a 404, which silently falls back to templates. `.env.example` and the code default now use `gemini-3.5-flash-lite`. We picked it over `gemini-3.8-flash` because it's about 1 s instead of 3.5–5 s, with equally good wording. Local Python env: `conda create -n hacktx26 python=3.12`, then `pip install -r backend/requirements.txt`.
- **One call per request, with a hard 6 s wait:** the Gemini API rejects deadlines under 10 s, so the SDK timeout is 10 s (`HTTP_TIMEOUT_MS`) and `explain_all` stops waiting after `TIMEOUT_S = 6` (`_call_with_deadline`, a worker thread). With flash-lite and `thinking_level="minimal"`, a call takes about 1 s once warmed (about 3.4 s cold). Slow-network runs can still pass 6 s and fall back to templates, so the cache (NM-21) is what makes the demo reliable. Don't use `thinking_budget=0`: 3.x models reject it with a 400.
- **Warm-up at Flask start:** `create_app()` in `backend/app.py` calls `services.llm.warm_up()`. **This is a one-line, Jose-approved edit to Rodrigo's file.** Rodrigo, keep it when you build NM-8/NM-12. In a background thread it creates the shared client and calls `models.get`, which opens the TLS connection without using generation quota. It runs once per process, so it's safe with Flask's reloader, and it does nothing without a key. It cut the first explanation from about 3.4 s to about 1 s.
- **Free-tier rate limit:** 5 requests per minute per model. Hitting it falls back to templates (logged as a warning), so run `warm_cache.py` (NM-21) slowly, about one call every 15 s.
- **What the model sees:** only `id, title, monthly_payment, delta_monthly, upfront_cost, total_cost, tradeoffs, action_label` (plus `rejection_reason` when set), the customer's first name and the raw `life_event`. Money is **pre-formatted strings** (`$294.34`, `$1,160`, `+$9.97`) from `templates.format_money`, so the model copies numbers instead of formatting them.
- **Fallback is per option:** a missing id, a non-string value, bad JSON, a missing key or any exception leaves that option on `template_explanation` with `source: "template"`.
- **Explanations may name rejected options:** the engine's `rejection_reason` text is passed through. The model repeats it kindly, so wording like "15% of your income (limit 15%)" comes from NM-11 and may need Samu to reword it.
- **NM-14 is wired in:** `explain_all` now runs `validate` on every LLM text (see NM-14's notes). The model has made small unsupported claims (for example, "set up payment reminders"), which is why the validator and the "use only facts in the JSON" prompt rule matter.

### ✅ NM-14 · Number validator + fallback `E3` `P0` · 2 pts · **Jose**
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

**Already done in NM-13:** `template_explanation` and `format_money` live in `backend/services/templates.py` and are tested in `backend/tests/test_llm.py`. `explain_all` has a `# NM-14` comment where `validate(text, rec)` goes: reject the text and keep the template when it returns False. The LLM is given money as formatted strings (`$1,275`, `$294.34`, `+$9.97`), so `allowed_numbers` must accept those forms as well as the raw numbers.

**Tasks:**
- [x] Validator (the template is done in NM-13)
- [x] Tests, including a deliberately bad string ("only $199/mo at 2.9%") that must fail
- [x] Log rejections (useful for the pitch: "we caught N hallucinations during testing")

**Acceptance criteria:**
- [x] Bad string → rejected → template used
- [x] Good LLM output → kept *(live Gemini output for p1 and p2 + `new_baby` through the real endpoint: all kept, 0 false rejections)*
- [x] Endpoint never returns an empty explanation *(Flask test-client tests with a hallucinating and a crashing LLM)*

**How to verify:** `pytest backend/tests/test_validator.py -v`

**What changed / what to know (read this if you build on NM-14):**
- **Where it lives:** the "Number validator" section of `backend/services/llm.py`: `extract_numbers`, `allowed_numbers` and `validate`. `explain_all` runs `validate` on every LLM text, and a failing option keeps its template (`source: "template"`); the other options keep their LLM text.
- **What counts as allowed:** every number in the **full** option, not just the fields sent to the model. That includes numbers written inside strings (`tradeoffs`, `title` such as "2027 Corolla", `vehicle_label`, `rejection_reason`, `assumptions`). Each is accepted raw, at 2 decimals and as a whole number ($294.34 may be said as "$294"), and signs are ignored ("$284.37 less" is fine). Small integers 1–3 are ignored, as specified.
- **Spec addition:** `validate(text, option, extra=frozenset())`. `explain_all` passes the life event's `params` numbers as `extra`, because the model is shown the life event, so "the extra $500 a month for the baby" is legitimate. Default params (an empty `{}`) add nothing.
- **Logging for the pitch:** each rejection logs a `WARNING` from `services.llm`: "Validator rejected LLM text for <id> (numbers not from the engine: [...]) ... Caught N so far", with the rejected text. The running count is `services.llm.hallucinations_caught`, reset when the server restarts. To get "we caught N during testing", grep the Flask log for `Validator rejected`, or print the counter after `warm_cache.py` (NM-21).
- **Prompt tweak (NM-13 file):** the model was writing "a delta monthly of +$9.97" and listing every number. `explain.txt` now forbids field names and asks for the one or two numbers that matter.
- **Known limit:** numbers written as words ("twelve months") aren't checked. Only digits are.

**Other tasks affected by NM-14 (each has a note in its own section):** NM-15 (loading and fallback timing), NM-19 (what the model can and can't quote), NM-20 (drawer copy), NM-21 (cache validated output, print the hallucination count), NM-24 (debug badge from `explanation_source`), NM-26 (the validator only understands US number formats, English-only templates, `lang` in the signature and cache key), NM-31 and NM-32 (Devpost and pitch wording).

### NM-15 · Wire frontend to live API `E4` `P0` · 2 pts · **Jose**
*As a demo, the UI must show real engine output, not sample JSON.*

**Context:** This is the integration moment for Milestone M2. After this, everything on screen comes from the backend.

**Blocked by:** NM-8, NM-10, NM-12 *(all done; the API is live)*

**Files:** `frontend/src/api.js`, `frontend/vite.config.js` (proxy)

**Spec:**
- Vite proxy: `/api` → `http://127.0.0.1:5000` (avoids CORS issues and hard-coded hosts; override with `VITE_API_PROXY`)
- `api.js` functions switch to `fetch`; keep the sample JSON as a fallback behind `VITE_USE_SAMPLE=true`
- Loading skeletons for the cards (recommendations may take 2–6 s with the LLM)
- Error state: "Couldn't load recommendations — retry" button

**Tasks:**
- [x] Proxy + fetch calls
- [x] Loading + error states (the card skeletons replace `<RecommendationList>` in `Dashboard.jsx` while loading)
- [x] Remove any remaining hard-coded data from components
- [x] Check that the live response carries `action.confirmation` (NM-10 contract change). If it doesn't, the toast quietly falls back to generic text, so check the wording on each card → *checked: the live API does **not** send it yet (Samu's NM-5 task is still open), so every toast currently shows the generic fallback*
- [x] Timing to plan the skeletons for (NM-13/NM-14): an LLM response takes about 1 s once the server has warmed up (up to about 3.5 s on the first request after a quiet period), and the backend stops waiting after 6 s and returns template text with `explanation_source: "template"`. The request still returns 200 with all explanations filled, so the UI never needs an "explanation failed" state; it only needs the normal loading and error states for the request itself
- [x] The POST can be slow while the free-tier LLM quota (5 requests per minute) is exhausted, but it still succeeds with templates. Don't auto-retry on every What-if click or you'll burn the quota; NM-21's cache removes the problem for the demo
- [x] The live API returns **2** cards for p1 (see NM-11), and the dashboard includes `equity_timeline` (NM-23) plus extra keys `miles_per_year`, `vehicle_targets`, `vehicle.catalog_id` (NM-8), which the UI can ignore

**Acceptance criteria:**
- [ ] p1 flows picker → dashboard → live cards with LLM explanations
- [ ] Stopping Flask shows the error state, not a blank page

**How to verify:** run both servers, click through p1, then kill Flask and reload.

**What changed / what to know (read this if you build on NM-15):**
- **How to run:** `cd backend && flask run` (port 5000), then `cd frontend && npm run dev`. The Vite proxy forwards `/api` to `http://127.0.0.1:5000`. It's `127.0.0.1` rather than `localhost` because Node can resolve `localhost` to IPv6 while Flask only listens on IPv4.
- **Different port (Samu, macOS):** Samu's earlier proxy pointed at 5001. It now defaults to 5000. Either turn off AirPlay Receiver, or run `flask run --port 5001` and put `VITE_API_PROXY=http://127.0.0.1:5001` in `frontend/.env.local` (gitignored; template in `frontend/.env.example`).
- **No backend:** `VITE_USE_SAMPLE=true` in `frontend/.env.local` serves the bundled sample JSON. Only p1 has sample recommendations, and the sample dashboards have an **empty `equity_timeline`**.
- **`api.js`:** `getPersonas()`, `getDashboard(id)` and `getRecommendations(id, lifeEvent)` (a POST with `{ life_event }`). Failures throw `ApiError` with `.status`: the HTTP code, or `0` when the server can't be reached. A 404 dashboard shows "Customer not found"; anything else shows a Retry box (`components/ErrorState.jsx`).
- **Loading:** the dashboard renders as soon as its own data arrives. The recommendations area shows `components/RecommendationSkeleton.jsx` (same layout as the cards) until the POST returns, including after every What-if change. Each request is keyed by customer, life event and retry attempt, so a slow old response is never shown.
- **What-if (NM-19):** `WhatIfPanel` gets `summary={null}` while a request is in flight, then that request's `life_event_applied`.
- **`ComparisonTable` (NM-22):** it's only rendered once recommendations have loaded, so it always gets a real `considered` array.
- **`EquityChart` (NM-23):** it gets the live `equity_timeline` straight from the dashboard. Handle an empty array, which is what sample mode sends.
- **Picker:** it shows "Loading customers…" and a Retry box on failure. It still calls each dashboard to get the car label, because `/api/personas` has no vehicle.
- **Fixed on the way (backend, Rodrigo and Samu's files):** three JSON readers (`customer_profile.py`, `profile.py`, `engine/constants.py`) opened files without `encoding="utf-8"`. On Windows the taglines showed "Â·". Now fixed, with a test in `backend/tests/test_data_encoding.py`. **Always pass `encoding="utf-8"` to `open()`.**

### ✅ NM-16 · Soft submission `E6` `P0` · 1 pt · **Rodrigo**
*As a team, we lock in a submission early so nothing can go wrong at 11:29 AM tomorrow.*

**Context:** The soft deadline is Sat 11:30 PM. A draft now means the final submission is just an edit.

**Blocked by:** nothing (submit whatever exists at 11 PM).

**Tasks:**
- [x] Create the project on hacktx26.devpost.com, add Jose and Samu as teammates
- [x] Name ("Next Move"), one-liner, 2 screenshots, GitHub link
- [x] Select the Toyota track
- [x] Placeholder sections: Inspiration / What it does / How we built it

**Acceptance criteria:**
- [x] Submitted before **11:30 PM Saturday**, with all three of us listed *(Jose and Samu: accept the Devpost invite if you haven't yet)*

---

### ✅ NM-17 · Life events `E1` `P0` · 3 pts · **Samu**
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
- [x] 3 P0 events *(the 2 P1 events, `job_change` and `move`, were not built)*
- [x] Event summary string
- [x] Tests per event against Appendix B's expected outcomes

**Acceptance criteria:**
- [x] p2 + `new_baby` → surplus $900 → $400; Highlander (+$233/mo) **rejected** by rule 2 (limit $200); #1 is `keep`
- [x] p2 + `income_drop` 20% → surplus −$340 → `relief_needed` → #1 `talk_to_advisor`, followed by `extend_term` (≈ $439.52) and `payment_deferral`
- [x] p1 + `longer_commute` → overage grows to 7,100 mi; `buy_miles_new_lease` becomes rejected (rule 3); buyout stays #1
- [x] The original profile object is unchanged after `apply_life_event`

**How to verify:** `pytest backend/engine/tests/test_events.py -v`

> NM-17 sits in Sprint 2 so Samu's evenings are balanced: it only needs NM-11, and finishing it early unblocks the What-if panel and persona tuning.
> If `job_change` / `move` ship, tell Rodrigo to add them to `ALLOWED_LIFE_EVENTS` in `routes.py` (NM-12).

---

**Done (Samu, merged into `dev`):** `events.py` (`ALLOWED_EVENTS`, `DEFAULT_PARAMS`, `apply_life_event`, `describe_life_event`) plus the commute miles in `options.py`. Covered by `test_events.py`. All four expected outcomes pass on `dev`:
- p2 + `new_baby` → "Baby on the way (+$500/mo) → monthly surplus now $400"; only `keep`; the Highlander is rejected with `previous_rank: 2`.
- p2 + `income_drop` 20% → "Income down 20% → monthly surplus now −$340"; `talk_to_advisor`, `extend_term`, `payment_deferral`.
- p1 + `longer_commute` → "projected 7,100 miles over your lease"; `lease_buyout` stays #1; prepaid miles ($1,460 upfront) rejected.
- The input profile is never mutated.
- **For NM-12 (Rodrigo):** import `ALLOWED_EVENTS` from `engine.events` for the 400 check. Invalid params raise `ValueError`, which maps to a 400.
- `job_change` and `move` (P1) were not built.

## Sprint 3 — Full MVP (Sat 10:30 PM → Sun 3:00 AM)

### ✅ NM-18 · Tune personas `E1`+`E2` `P0` · 2 pts · **Rodrigo + Samu**
*As a demo, each persona must tell a clean, believable story.*

**Context:** Appendix B's numbers were pre-checked, but real implementations drift (rounding, fees, mock-data noise). This story is the end-to-end check that the engine, the data and the demo script agree.

**Blocked by:** NM-11, NM-17, NM-7

**Files:** `backend/data/vehicle_catalog.json`, `backend/engine/constants.py`, `backend/engine/tests/test_personas.py`, `backend/engine/tests/test_options.py`

**Tasks:**
- [x] Integration test: for every row of the Appendix B "expected outcomes" table, assert the #1 option (`backend/engine/tests/test_personas.py`)
- [x] If an assertion fails, adjust **data**, not rules (2027 Corolla MSRP, see below)
- [ ] Sanity-read every explanation for every persona/event combo (now possible: NM-13/14 are merged). NM-13 notes: the model sometimes adds small unsupported claims, and it repeats `rejection_reason` verbatim, so reword confusing reasons in the engine, not the prompt
- [x] Decide whether p1 should show 3 cards: **keep 2** (`lease_buyout`, `buy_miles_new_lease`). `return_new_lease` and `return_walk_away` are correctly rejected by rule 3 for Maya's savings, and the UI handles 2 cards. Update the demo script (plan §12) and the NM-10 sample if they still show 3

**Acceptance criteria:**
- [x] `test_personas.py` passes for all 8 persona/event combinations in Appendix B (10 tests total)
- [x] Each persona's #1 card matches the demo script (plan §12)

**How to verify:** `cd backend && python -m pytest engine/tests/test_personas.py -v`

**What changed / what to know (read this if you build on NM-18):**
- **2027 Corolla LE MSRP 23,500 → 22,500.** At 23,500 the new lease was $324.20, which is 15.4% of Maya's income, so rule 1 rejected `buy_miles_new_lease`. Now it's **$310.40** and ranks #2. `test_options.py` was updated to 310.40 (Samu approved).
- **`constants.py` now loads `VEHICLE_CATALOG` from `backend/data/vehicle_catalog.json`** (Samu approved). The duplicate hand-typed catalog is gone, so car data lives in one place.
- **`test_personas.py` compares `kind`, not `id`**, because ids include the target car (`trade_in_upgrade:camry_hybrid_se_2027`).
- **Extra checks:** Maya's top 2 are `lease_buyout`, `buy_miles_new_lease`; Reyes + `new_baby` → Highlander `affordable: false` with a non-empty reason.
- **Uses the real pipeline:** `build_profile()` (data, NM-8) → `recommend()` (engine). If data or engine changes break the demo story, this test fails.

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

**From NM-13 / NM-14:** each What-if change calls the LLM again (about 1 s, or instant once NM-21's cache has that combination). The explanation model only sees the event's `type` and `params`, not `life_event_applied` or `finances_after_event`, so card text can mention "your new baby" or the event's own numbers (for example, an income drop of 20%) but can't quote the new surplus; that number belongs in your banner. Any number the model writes that isn't in the option or the event params is replaced by the template. The slider's debounce also protects the free-tier limit of 5 requests per minute.

**From NM-15:** every change to `lifeEvent` (via `onChange`) immediately re-requests recommendations. The cards switch to the loading skeleton until the response arrives, and `summary` is `null` meanwhile, so render no banner while it's `null`. Debounce the slider inside `WhatIfPanel` before calling `onChange`, since the Dashboard doesn't debounce for you.

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

**From NM-14:** the "AI cannot change numbers" line is now literally true. Every LLM sentence is checked by `services.llm.validate`, and any number not in the engine output swaps the text for the template. The drawer can show `explanation_source` honestly: "Explained by AI · numbers checked" for `"llm"`, "Standard explanation" for `"template"`.

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

**From NM-13:** the cache stores exactly what `llm.explain_all` returns (`{ option_id: { text, source } }`). `llm._call_llm` is the single function that talks to Gemini, so `CACHE_ONLY` should skip `explain_all`'s LLM call entirely. The free tier allows 5 requests per minute, so `warm_cache.py` must pause between calls (about 15 s), and it should skip writing entries whose `source` is `"template"` (a rate-limit or timeout fallback), so a bad run never gets cached.

**From NM-14:** cache the output of `explain_all`, never raw model text. It has already been through the number validator, so cached explanations are validated ones. A cached `"template"` entry may also mean the validator rejected the LLM text (see the `Validator rejected` log line), which is another reason to retry it rather than cache it. At the end of `warm_cache.py`, print `services.llm.hallucinations_caught`. That's the "we caught N hallucinations" number for the pitch (NM-32).

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

**From NM-15:** `<ComparisonTable considered={...} />` is only rendered once the recommendations request has succeeded, so `considered` is always a real array (while loading, the skeleton shows instead). It sits inside `<div id="all-options">`, the target of the cards' "We also considered N other options" link.

**From NM-10:** the cards' "We also considered N other options" link points to `#all-options`, a `<div>` that `Dashboard.jsx` already wraps around `<ComparisonTable>`, so you don't need to add an id. `considered` includes the top 3 as well as the rejected options. Rejected items carry only `id, title, monthly_payment, delta_monthly, upfront_cost, total_cost, affordable, rejection_reason` (no `rank`), so sort them after the ranked ones.

**From NM-12 (live API):** in the live response, rejected options are full option objects with `rank: null` (not the reduced shape above), and every item has `kind`. Sort by `rank` with `null` last.

**Acceptance criteria:**
- [ ] Shows every `considered` item, with reasons for rejected ones
- [ ] Updates with the What-if panel

---

## Sprint 4 — Polish + stretch (Sun 3:00 → 8:30 AM)

### NM-23 · Equity / payment chart `E4` `P1` · 3 pts · **Rodrigo** · 🟡 backend done, chart waits on NM-15
*As a customer, I want to see when my car is worth more than I owe.*

**Context:** Feeds the "Equity tracker" feature from our pitch. It's visual proof of why p3 should upgrade now.

**Blocked by:** NM-8 for the backend half (✅ done), and NM-15 for the chart. Rodrigo owns both halves; ask Samu to review the amortization use.

**Files:** `frontend/src/components/EquityChart.jsx` ⏳; backend: `services/equity.py` ✅ (`equity_timeline`, built on Samu's `engine.finance` functions), `routes.py` ✅ (`equity_timeline` is in the dashboard response)

**From NM-15:** the chart is unblocked. `Dashboard.jsx` passes the live `equity_timeline` from `/api/customers/<id>/dashboard` as `<EquityChart timeline={...} contractType={contract.type} />`, no other wiring needed. In sample mode (`VITE_USE_SAMPLE=true`) the timeline is an **empty array**, so render nothing (or a short note) instead of crashing.

**Spec:**
- Backend: `equity_timeline(profile, months=24) -> [{ month, value, payoff }]` (value depreciates at `DEPRECIATION_PER_YEAR`, payoff from the amortization schedule)
- Recharts `LineChart`: two lines (value, payoff), shaded area between them (green where value > payoff), a "Today" marker
- Lease customers: plot residual vs estimated value instead

**Tasks:**
- [x] Backend: `equity_timeline()` in `services/equity.py`
- [x] Add `equity_timeline` to the dashboard response
- [ ] Recharts chart in `EquityChart.jsx`
- [ ] Ask Samu to review the amortization use

**Acceptance criteria:**
- [ ] p3's chart clearly shows positive equity today
- [ ] Renders for all 3 personas without errors

**What changed / what to know (read this if you build on NM-23):**
- **Value:** `est_value × (1 − DEPRECIATION_PER_YEAR) ^ (month / 12)`, a smooth monthly drop of 12% per year.
- **Payoff:** loans use `loan_balance(today's payoff, apr, months_remaining, month)`, i.e. today's balance paid down by the remaining payments (never below 0); leases use the residual (flat).
- **Length:** stops at the contract end → p1 has **5 points** (months 0–4); p2 and p3 have **25** (months 0–24).
- **p3 check:** month 0 → value 21,000 / payoff 12,615.04; month 12 → 18,480 / 8,817.15; month 24 → 16,262.40 / 4,625.73.

### NM-24 · UI polish pass `E4` `P1` · 3 pts · **Jose**
*As judges, we should think "this could ship".*

**Tasks:**
- [ ] Consistent spacing and typography; Toyota-inspired palette (no official logos; use a text wordmark "Next Move")
- [ ] Empty, loading and error states on every screen (*NM-15 did the persona picker, the dashboard and the recommendations area: `ErrorState.jsx` with Retry, `RecommendationSkeleton.jsx`; check the remaining components, e.g. the What-if banner, comparison table and chart*)
- [ ] Favicon, page titles, a nice persona-picker header
- [ ] Check at 1280×800 and on the projector resolution (1920×1080)
- [ ] Remove console errors and warnings
- [ ] Debug badge: with `?debug=1` in the URL, show a tiny "AI" / "template" badge on each card from `explanation_source` (promised in NM-14's spec; the field is already in the API response and `RecommendationCard.jsx` doesn't render it yet). Handy for rehearsals to see which cards fell back (timeout, rate limit or a rejected number)

**Acceptance criteria:**
- [ ] No console errors on the full demo path
- [ ] A teammate who hasn't seen the UI can complete the demo path without help

### NM-25 · Live Nessie `E5` `P2` · 5 pts · **Rodrigo**
*As the Capital One track, the financial profile comes from real Nessie calls.*

**Context:** Only worth doing if Nessie is reachable. It qualifies us for Capital One's Best Use of Nessie ($250 per member), using the adapter built in NM-7.

**Blocked by:** NM-7 (✅ done), and Nessie being reachable (confirm the base URL with Capital One in the WEL hallway or on Discord)

**Files:** `backend/services/nessie.py`, `backend/scripts/seed_nessie.py`, `backend/data/nessie_ids.json`

**Spec:**
- Base URL from `.env` (`NESSIE_BASE_URL`); key from `NESSIE_KEY`, passed as `?key=`
- `seed_nessie.py`: for each persona, `POST /customers` → `POST /customers/{id}/accounts` (checking + savings) → `POST /accounts/{id}/deposits`, `/purchases`, `/bills` from the mock files; save the returned Nessie ids to `nessie_ids.json`
- `nessie.py`: `GET /customers/{id}/accounts`, `/accounts/{id}/deposits`, `/purchases`, `/bills` → the same normalization as NM-7
- Map our `customer_id` (p1) → Nessie id via `nessie_ids.json`
- 5-second timeout; on failure, fall back to mock and set `source: "mock (Nessie unavailable)"`

**From NM-7:** the math is already reusable. `nessie.py` only needs to return data in the mock file shape; then call `profile.calculate_monthly_finances(bank_data, source="nessie")` and add the `"nessie"` branch to `get_financial_profile`.

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

**From NM-13 / NM-14 (what you need to change in the explanation pipeline):**
- **Number format:** the validator (`extract_numbers` in `backend/services/llm.py`) only understands US formatting: `1,275.50`, `$294.34`, `6.9%`. It misreads European-style numbers (`1.275,00` is read as 1.275, 0 and so on), so those explanations would be rejected and fall back to templates. The simplest fix is in the prompt: tell the model to copy every number exactly as given in the JSON (`$1,275`, `294.34`), which is also standard in US Spanish. Only if you want true Spanish formatting, extend `extract_numbers` and its tests in `test_validator.py`.
- **Fallback language:** `templates.template_explanation` produces English only, so a failed or rejected Spanish explanation would show English. Add a Spanish variant keyed by `lang`.
- **Signature and route:** `explain_all(recommendations, profile, life_event)` has no language yet. Add a `lang` parameter (default `"en"`), load a Spanish prompt (a second file next to `explain.txt`), and have `routes.py` (Rodrigo) read `?lang=` and pass it through.
- **Cache:** include `lang` in NM-21's cache key, or Spanish and English entries will overwrite each other.
- **Words vs digits:** the validator ignores numbers spelled out as words ("mil doscientos"). Tell the model to write digits.

**Acceptance criteria:**
- [ ] The full demo path works in Spanish with cached explanations

### NM-27 · Recall card `E2` `P2` · 2 pts · **Rodrigo**
*As a customer, I want to know if my car has an open safety recall.*

**Files:** `backend/services/recalls.py`, `backend/data/recalls_cache.json`

**Spec:**
- NHTSA Recalls API: `https://api.nhtsa.gov/recalls/recallsByVehicle?make=TOYOTA&model={model}&modelYear={year}` (no key needed)
- Cache responses to disk (demo-safe)
- If any recalls exist, add a `recall_service` card (`action.kind: follow_up`, "Book a free recall repair") pinned above the rankings. It's safety, not a financial option.

**From NM-8:** `build_profile()` already provides `vehicle.model` and `vehicle.year` for the NHTSA query.

**Acceptance criteria:**
- [ ] Works offline from cache
- [ ] Shows the real recall title and NHTSA campaign number

### NM-28 · Engine hardening `E1` `P1` · 2 pts · **Samu**
*As a demo, the engine must never crash, whatever the slider says.*

**Tasks:**
- [ ] Edge cases: 0 months remaining, negative equity on trade-in (roll the negative equity into the new loan and say so in trade-offs), zero/negative surplus, income drop of 40%+, missing optional fields
- [ ] Fuzz test: random life-event params for all personas; assert no exceptions and that all numbers are finite
- [ ] Round money to 2 decimals at the API boundary only *(already done in `routes.py` by `round_money()`, NM-12; the engine should keep returning unrounded numbers)*

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
- [ ] **Challenges:** Nessie downtime → adapter pattern; keeping the AI from inventing numbers (NM-14: every number in an LLM sentence must appear in the engine's output for that option, or the sentence is replaced by a template; quote the `hallucinations_caught` count from NM-21's warm run)
- [ ] **What's next:** real TFS data, credit pre-qualification, push alerts when equity turns positive
- [ ] **Built with** tags; screenshots of every screen; video link; public repo
- [ ] Tracks: Toyota (+ Capital One if NM-25 is done, + Gemini MLH prize if used)

**Note:** the project already exists on Devpost from NM-16 (soft submission). This is an edit of that draft, not a new project.

**Acceptance criteria:**
- [ ] Submitted before **11:30 AM Sunday**; all 3 teammates confirm they're listed

### NM-32 · Pitch prep `E6` `P0` · 2 pts · **All**
*As presenters, each of us can deliver the demo confidently, alone if needed.*

**Tasks:**
- [ ] 5-slide deck (**Samu leads**, everyone reviews): Problem · Demo · Responsible AI (engine decides, AI explains, validator) · Business value (retention, upgrade revenue, fewer calls) · Team
- [ ] Each person rehearses the 2-minute pitch once out loud
- [ ] Prepare answers: "Where does the data come from?", "What if the LLM is wrong?", "How would TFS deploy this?", "Why these affordability thresholds?"
  - *"What if the LLM is wrong?"* (NM-14): the LLM never computes. It gets pre-calculated, pre-formatted numbers, and a validator checks every digit it writes against the engine's output. One unknown number means that card shows a deterministic template instead. Live demo: `pytest backend/tests/test_validator.py -v` shows "only $199/mo at 2.9%" being rejected. Limit to admit if asked: numbers spelled out as words aren't checked
  - *"Where does the data come from?"* (NM-6/7): synthetic Toyota contracts and a vehicle catalog we wrote, plus bank data shaped exactly like Capital One's Nessie API, generated by a seeded script. One env var (`DATA_MODE`) switches to live Nessie
- [ ] Laptop setup for judging: charger, `CACHE_ONLY=true`, browser zoom tested, tabs pre-opened

**Acceptance criteria:**
- [ ] Every teammate can give the pitch solo
- [ ] Judging starts at 2 PM in WEL; we're at our table by 1:45 PM

---

## Points per person (check balance)

| | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 | **P0/P1 total** | P2 stretch |
|---|---|---|---|---|---|---|---|
| **Samu** | NM-4, NM-5 (8) | NM-11, NM-17 (6) | NM-19, NM-18* (5) | NM-28 (2) | pitch deck lead | **21** | — |
| **Rodrigo** | ✅ NM-6, NM-7, NM-8 (8) | ✅ NM-12, ✅ NM-16 + ✅ NM-23 backend (3) | ✅ NM-18*, NM-22 (4) | NM-23 chart (3) | NM-30 (3) | **21** | NM-25, NM-27 (7) |
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
| `corolla_le_2027` | 2027 Corolla LE | 22,500 | 35 | 62% |
| `rav4_xle_2022` | 2022 RAV4 XLE | — | 30 | — |
| `highlander_xle_2027` | 2027 Highlander XLE | 45,500 | 25 | 58% |
| `camry_se_2021` | 2021 Camry SE | — | 32 | — |
| `camry_hybrid_se_2027` | 2027 Camry Hybrid SE | 32,500 | 51 | 60% |
| `corolla_le_2023` | 2023 Corolla LE | — | 35 | — |

> **Source of truth:** `backend/data/vehicle_catalog.json`, loaded by `constants.py` since NM-18. The JSON also has `year`, `model` and `trim` for every car. The 2027 Corolla MSRP was lowered from 23,500 in NM-18.

## Appendix B — Personas (exact numbers)

### p1 — Maya Lopez · "College senior · Corolla lease ending · over on miles"
- **Goals:** `["keep_a_car_after_graduation"]` · **Miles/year:** 11,700 · **Targets:** `["corolla_le_2027"]`
- **Vehicle:** 2023 Corolla LE (`corolla_le_2023`), 31,200 mi, est. value **$18,900**
- **Contract:** lease · cap cost $22,500 · residual **$14,600** · MF 0.00175 · 36 mo · **32 elapsed / 4 remaining** · payment **$284.37** · allowed 30,000 mi total
- **Projected:** 35,100 mi at lease end → **5,100 over → $1,275 fee**
- **Finances:** income **$2,100** · bills **$1,150** (incl. car; mock data: 1,149.37) · spending **$520** · surplus **$430** · savings **$2,600** · checking $640

### p2 — The Reyes family · "Expecting a baby · financed RAV4"
- **Goals:** `["keep_payments_predictable"]` · **Miles/year:** 13,000 · **Targets:** `["highlander_xle_2027"]`
- **Vehicle:** 2022 RAV4 XLE, 41,000 mi, est. value **$24,000**
- **Contract:** loan · $30,000 at **4.9%** · 60 mo · **22 paid / 38 remaining** · payment **$564.76** · payoff **≈ $19,841** → equity **≈ +$4,159**
- **Finances:** income **$6,200** · bills **$3,600** (incl. car; mock data: 3,599.76) · spending **$1,700** · surplus **$900** · savings **$9,000** · checking $2,100

### p3 — Daniel Kim · "Positive equity · high-APR Camry loan"
- **Goals:** `["newer_vehicle", "lower_fuel_cost"]` · **Miles/year:** 12,000 · **Targets:** `["camry_hybrid_se_2027"]`
- **Vehicle:** 2021 Camry SE, 48,000 mi, est. value **$21,000**
- **Contract:** loan · $22,000 at **9.9%** · 72 mo · **36 paid / 36 remaining** · payment **$406.46** · payoff **≈ $12,615** → equity **≈ +$8,385**
- **Finances:** income **$6,500** · bills **$2,800** (incl. car; mock data: 2,801.46) · spending **$1,500** · surplus **$2,200** · savings **$15,000** · checking $3,400

### Expected outcomes (NM-18 asserts these)

| Persona + event | Key numbers | Expected #1 | Notes |
|---|---|---|---|
| p1 baseline | buyout $294.34 (+$9.97) · buy-miles upfront $1,160, new lease $310.40 · return upfront $1,670 | `lease_buyout` | #2 `buy_miles_new_lease`; `return_new_lease` and `return_walk_away` rejected (rule 3: $2,600 − $1,670 < $1,150) → **2 cards** |
| p1 + longer_commute | +2,000 projected miles → 7,100 over · buy-miles upfront $1,460 | `lease_buyout` | Buy-miles now **rejected** too (rule 3: $2,600 − $1,460 < $1,150) |
| p2 baseline | keep $564.76 · Highlander ≈ $797.33 (+$233) | `keep` | Highlander affordable (#2); no refinance (4.9% < 6.4%) |
| p2 + new_baby | surplus $900 → $400 | `keep` | Highlander **rejected** (rule 2: $233 > $200) ← demo moment |
| p2 + income_drop 20% | surplus → −$340 | `talk_to_advisor` | Then `extend_term` ≈ $439.52, `payment_deferral` |
| p3 baseline | trade-in ≈ $465.09 (+$59, −$35 fuel) · refi ≈ $386.06 | `trade_in_upgrade` | Goal `newer_vehicle`; refi #2, keep #3 |
| p3 + income_drop 20% | surplus $2,200 → $900 | `trade_in_upgrade` | Still affordable; shows resilience |
| p3 + longer_commute | fuel savings grow | `trade_in_upgrade` | Hybrid advantage widens |