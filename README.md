# 🚗 NexMove

> **HackTX 2026 · Toyota Financial Services Challenge**

A dashboard that tells a Toyota customer their **smartest next move** (buyout, upgrade, refinance, or keep) with real numbers and one clear action.

---

## ✨ Features

- **Lease/Loan Advisor:** compares every option and ranks the top 3.
- **"What If?" Simulator:** new baby, income drop, or longer commute → the best move updates.
- **Equity Tracker:** shows when your car is worth more than you owe.
- **Human Handoff:** "Talk to a specialist" button on every screen.

---

## 🧠 Responsible AI

- **The engine decides, the AI explains.** All math and ranking is tested Python code.
- **The AI can't make up numbers.** A validator rejects any number the engine didn't compute.
- **Only affordable options are recommended**, and rejected ones show why.

---

## 🗂️ Data

- **Synthetic Toyota data:** vehicles, leases, loans.
- **Bank data:** mock, shaped like Capital One's Nessie API (live Nessie is a stretch goal).

**Stack:** React + Recharts · Flask · Gemini

---

## 🎬 Demo Personas

| Persona | Situation | Best Move |
|---|---|---|
| 🎓 **Maya** | Lease ending, over on miles | Buy out the lease |
| 👶 **Reyes family** | Baby on the way | Keep the RAV4 (the Highlander becomes unaffordable) |
| 💰 **Daniel** | High-APR loan, positive equity | Trade in for a Camry Hybrid |

---

## 👥 Team

| Member | Role |
|---|---|
| **Samu** | Finance engine + What-if panel + pitch deck |
| **Rodrigo** | Data + Flask API + charts + demo video |
| **Jose** | AI explanations + frontend + Devpost |

Full task breakdown: `BACKLOG.md`

---

## ⏱️ Key Deadlines

- **Sat 11:30 PM:** soft submission
- **Sun 10:30 AM:** code freeze
- **Sun 11:30 AM:** final submission