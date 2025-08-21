# ADC CryptoGuard Validator – Hedera Security Framework

[![Website](https://img.shields.io/badge/Website-AutoDigitalCoin.com-blue?logo=google-chrome)](https://autodigitalcoin.com)
[![Live Validator](https://img.shields.io/badge/Validator-LIVE-green?logo=vercel)](https://adcoin-validator-ai.onrender.com)
![ISO 20022](https://img.shields.io/badge/ISO%2020022-Compliant-blueviolet)
![License](https://img.shields.io/badge/License-BY--NC--ND%204.0-lightgrey)
![Repo Size](https://img.shields.io/github/repo-size/ADCoinX/adcoin-validator-ai)
![Last Commit](https://img.shields.io/github/last-commit/ADCoinX/adcoin-validator-ai)
![Issues](https://img.shields.io/github/issues/ADCoinX/adcoin-validator-ai)
![Forks](https://img.shields.io/github/forks/ADCoinX/adcoin-validator-ai?style=social)
![Stars](https://img.shields.io/github/stars/ADCoinX/adcoin-validator-ai?style=social)
[![Applying Hedera Thrive](https://img.shields.io/badge/Applying-Hedera%20Thrive-green)](https://thrivehedera.com)

---

## 📌 Project Overview
**ADC CryptoGuard Validator** is a **wallet security and compliance tool** focused on **Hedera (HBAR)**. It validates Hedera accounts, flags anomaly/scam indicators, and produces **ISO 20022-compliant** audit exports from public Mirror Node data.

👤 **Builder Note:** Built and maintained by a **solo founder (ADCX Lab)**. Program funding (e.g., Hedera Thrive / Launch) will accelerate feature depth while keeping the codebase transparent and open-source.

**Objectives**
- Protect Hedera users from high-risk or known-scam interactions
- Provide audit-ready ISO 20022 XML exports
- Keep the validator lightweight, privacy-first, and API-driven (no sensitive keys stored)

---

## 🔎 Hedera Module (✅ Active)
- Hedera account validation (`0.0.x`)
- On-chain metadata review via **Mirror Node API**
- Risk scoring (0–100) with heuristic flags (e.g., suspicious flow patterns)
- **ISO 20022 XML** export for auditors & compliance
- **Planned (Next):** deeper HTS token checks, explorer integration, richer anomaly rules

---

## 🗂️ Repository Structure
- `/core/` – AI risk scoring + ISO 20022 exporter (e.g., `ai_risk.py`, `iso_export.py`)
- `/integrations/hedera/` – Hedera-specific logic (validators, fetchers, parsers)
- `/templates/` – Web frontend (HTML/CSS)
- `/static/` – Assets (logo, styles)

> **Note:** Some folders may include placeholder `.keep` files to avoid deployment crashes. Full expansion aligns with program milestones.

---

## ⚙️ Technical Summary
- **Frontend:** HTML + CSS
- **Backend:** Python Flask
- **Risk Engine:** Local module (`ai_risk.py`) with heuristic scoring (0–100)
- **Data Sources:** **Hedera Mirror Node** public endpoints only (fallback mirrors configured)
- **Compliance:** ISO 20022 XML via `iso_export.py` (audit-ready export)

---

## 🧩 Architecture (Hedera)

User/Reviewer → Flask API (`app.py`) → Address Router (detect Hedera `0.0.x`) → Hedera Mirror Node API (accounts, transactions; public endpoints with fallback) → AI Risk Engine (`ai_risk.py`, 0–100 scoring) → ISO 20022 Export (`iso_export.py`) → Outputs: JSON (risk_score, flags), ISO 20022 XML (audit), Web UI (templates/)

- Tech: HTML/CSS (frontend), Python Flask (backend), local heuristic risk engine, Hedera Mirror Node public data only (no secrets), redundancy via multiple mirror endpoints, privacy-first execution.
- Repo paths: `/integrations/hedera/` (validators/fetchers/parsers), `/core/` (`ai_risk.py`, `iso_export.py`), `/templates/`, `/static/`.

## 🔁 Request Flow (Hedera)

1) Client calls `POST /validate` with body: `{"chain":"hedera","address":"0.0.x"}`
2) Flask API → Address Router detects Hedera pattern (`0.0.x`) and selects Hedera path.
3) Fetch snapshot from Hedera Mirror Node API (`/accounts/{id}`, `/transactions`); fallback endpoints available.
4) Pass snapshot → `ai_risk.py` → compute `risk_score` (0–100) + flags (e.g., scam history, anomalous token activity).
5) Optional compliance: call `iso_export.py` → generate ISO 20022 XML report (returns file/string path).
6) API responds with JSON: `{ "chain":"hedera", "address":"0.0.x", "risk_score": <0-100>, "flags":[...], "iso20022_xml_url": "<optional>" }`
7) Frontend (templates/) renders summary; download button exposes the ISO 20022 XML.

### Notes
- No private keys or sensitive info stored.
- Uses only public mirror endpoints (Hedera mainnet/testnet).
- Includes retries + fallback nodes for reliability.
- All processing is local; ensures compliance + privacy.

---

## 🔐 Security & Infosec
**Quality & Assurance**
- [![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)
- [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)
- [![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)

**Principles**
- No storage of secrets/private keys
- Read-only **public** endpoints with redundancy
- Local processing to preserve user privacy

---
## 🔐 Funding Disclosure & Budget (Hedera Grant)

This repository contains a modular validator with **Hedera-specific deliverables**.  
I am a **solo builder** and the requested budget is **ring-fenced for Hedera only**.  
Shared modules are maintained as open-source, but **Hedera funds the Hedera-specific portions inside them**.

---

### 🟦 Core (Hedera-funded portions only)
These components are foundational, but Hedera grant covers **only Hedera-related logic**:
- **Validator Core (Backend)** (`app.py`) → Hedera account parsing & adapter logic  
- **AI Risk Engine** (`ai_risk.py`) → Hedera heuristics & anomaly scoring (base AI is neutral)  
- **ISO 20022 Exporter** (`iso_export.py`) → Hedera export profile (base module is neutral)  
- **API Handler + Fallback** (`api_handler.py`) → Hedera Mirror Node integration  
- **Frontend (Web/Mobile)** (`index.html`, `style.css`) → Hedera account validation UI  

---

### 🟨 Hedera-Specific (Funded Scope)
1. Hedera account validation (`0.0.x` addresses)  
2. Account & transaction snapshot via Mirror Node API  
3. HTS token safety checks (policy & anomaly rules)  
4. ISO 20022 (Hedera profile) export  
5. Compliance Dashboard (Hedera-specific UI + reports)  
6. **Mobile (iOS/Android)**: lightweight Hedera account validation UI  

---

### ⚖️ Justification
- **No double funding**: XRPL-specific work is separate (`integrations/xrpl`).  
- **Core modules**: Hedera funds only Hedera-related features; neutral/cross-chain code is not billed.  
- Transparency: public repo, open issues, SonarCloud quality checks.  

---

### 📅 Timeline (per Hedera grant)
- **Week 1–2**: Parser + account validation rules  
- **Week 3–4**: Mirror Node ingestion + HTS safety checks  
- **Week 5–6**: ISO 20022 Hedera profile export  
- **Week 7–8**: Compliance dashboard + stabilization  
- **Mobile (iOS/Android)**: lightweight Hedera validation UI added in **Week 3**  

---

### 📧 Contact
For any clarification on scope or budgeting: **admin@autodigitalcoin.com**

---
## ⚠️ Disclaimer
For **educational, research, and compliance validation** purposes only. ADCX Lab does not provide financial, investment, or legal guarantees. Final responsibility for risk decisions remains with the user or institution.

---

## 📞 Contact
**Muhammad Yusri Adib** — Founder, ADCX Lab (Solo Builder)  
📩 Email: admin@autodigitalcoin.com  
💬 Telegram: [@ADCoinhelpline](https://t.me/ADCoinhelpline)  
🐦 Twitter: [@AdCoinMy](https://twitter.com/AdCoinMy)  
🔗 LinkedIn: [Muhammad Yusri Adib](https://www.linkedin.com/in/muhammad-yusri-adib)
