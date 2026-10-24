# 🚗 Next Move

> **HackTX 2026 · Toyota Financial Services "What's Your Next Move?" Challenge**

**Next Move** helps Toyota customers answer one question:

> *"Given my situation today, what's the smartest next move for me and my Toyota?"*

---

## 📌 The Idea in 30 Seconds

1. A customer logs in and sees **their vehicle** and **their loan or lease**.
2. We combine that with **their real cash flow** (from Capital One's Nessie API).
3. The app shows **2–3 ranked recommendation cards**.
4. Each card has:
   - 💵 **The numbers** (payment, total cost, savings)
   - 💬 **A plain-English explanation**
   - 👉 **An action button**: self-service, schedule a follow-up, or claim an eligible offer

---

## ✨ Core Features

| Feature | What it does | Example |
|---|---|---|
| **🔄 End-of-Lease/Loan Advisor** | Compares return, buyout, new lease, refinance, and trade-in side by side. Shows the monthly payment, total cost, and trade-offs for each option. | *"Buying out your Corolla costs $14,200. A new lease is $289/mo."* |
| **🔮 "What If?" Simulator** | The user picks a life event (new baby, job change, move, income drop, longer commute). The app recalculates and recommends a next step. | *"Baby on the way? A Highlander fits your budget for +$90/mo."* |
| **📈 Equity Tracker** | Tracks car value vs. loan payoff and alerts the customer when they have positive equity and an upgrade makes sense. | *"Your RAV4 is worth $3,200 more than you owe."* |

---

## 🏦 How We Use Capital One's Nessie API

[Nessie](http://api.nessieisreal.com/) is Capital One's hackathon API (USE THE ORIGINAL API CAPITALONE). It provides **mock customer banking data** (customers, accounts, deposits, bills, purchases, loans) and uses a simple API key for authentication.

**What we pull from Nessie:**

- **Accounts & deposits** → the customer's income
- **Bills & purchases** → the customer's spending
- **Result** → their **monthly surplus**, which drives every recommendation

**Why it matters:**

- ✅ **Personalized:** recommendations are based on real cash flow, not generic advice.
- ✅ **Affordability guardrails:** we never recommend something the customer can't afford.
- ✅ **Synthetic data:** Nessie data is already mock data, which meets the challenge requirement.

**What Nessie *doesn't* have:** Toyota vehicle and loan/lease details (model, mileage, residual value, APR, months remaining).
➡️ We create our own **synthetic Toyota JSON dataset** and link each profile to a Nessie `customer_id`.

---

## 🧠 Responsible AI (Big Judging Point)

| Rule | Why |
|---|---|
| 🔢 **All math is done in Python code, never by the LLM** | Payments, interest, equity, and affordability are always accurate and reproducible. |
| 💬 **The LLM only *explains* results** | It turns numbers into plain language. It doesn't make decisions. |
| 🔍 **Assumptions are always visible** | APR, miles per year, and vehicle value are shown on every card. |
| ❓ **"Why this recommendation?" button** | Users can see exactly what drove each suggestion. |
| 🚫 **No invented rates or offers** | The LLM only sees numbers our engine calculated. |
| 🙋 **Human handoff, always available** | Every card offers "Talk to a specialist." |

---

## 🏗️ How It Works

```
┌──────────────────────┐
│   React Frontend     │  Dashboard · Recommendation cards · What-if simulator
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│    Flask Backend     │
│                      │
│  1. Data layer       │ ← Nessie API (banking) + Toyota JSON (vehicle/loan)
│  2. Calc engine      │ ← Payments, equity, affordability (pure Python)
│  3. Recommender      │ ← Ranks the 2–3 best options
│  4. LLM explainer    │ ← Turns results into plain English
└──────────────────────┘
```

**Flow:** Load customer → calculate options → filter by affordability → rank → explain → display.

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| **Frontend** | React, Recharts |
| **Backend** | Flask (Python) |
| **Banking data** | Capital One Nessie API |
| **Vehicle data** | Our synthetic Toyota JSON |
| **AI** | LLM for plain-language explanations only |

---

## 🎬 Demo Plan: 3 exampe accounts

| Persona | Situation | Expected "Next Move" |
|---|---|---|
| 🎓 **The Student** | Corolla lease, going over her miles | Buy extra miles now (cheaper than paying the overage at lease end) |
| 👶 **The Growing Family** | Financed RAV4, baby on the way | Upgrade to a Highlander or Sienna within budget |
| 💰 **The Upgrader** | Positive equity on their current Toyota | Trade in and upgrade for about the same monthly payment |

---

## 💼 Business Value for Toyota

- 🔁 **Retention:** keeps customers with Toyota at end of lease, when they're most likely to leave.
- 📈 **Revenue:** upgrade offers timed to real equity and affordability.
- 📉 **Less service effort:** customers self-serve on payment questions instead of calling.

---

## 👥 Team & Tasks

| Member | Responsibilities |
|---|---|
| **Rodrigo** | _TBD_ |
| **Sam** | _TBD_ |
| **Jose** | _TBD_ |

> 📝 Sam is finalizing the task split. This section will be updated.

