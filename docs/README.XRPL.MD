# ADC CryptoGuard Validator – XRPL Security Framework

[![Website](https://img.shields.io/badge/Website-AutoDigitalCoin.com-blue?logo=google-chrome)](https://autodigitalcoin.com)
[![Live Validator](https://img.shields.io/badge/Validator-LIVE-green?logo=vercel)](https://adcoin-validator-ai.onrender.com)
![ISO 20022](https://img.shields.io/badge/ISO%2020022-Compliant-blueviolet)
![License](https://img.shields.io/badge/License-BY--NC--ND%204.0-lightgrey)
![Repo Size](https://img.shields.io/github/repo-size/ADCoinX/adcoin-validator-ai)
![Last Commit](https://img.shields.io/github/last-commit/ADCoinX/adcoin-validator-ai)
![Issues](https://img.shields.io/github/issues/ADCoinX/adcoin-validator-ai)
![Forks](https://img.shields.io/github/forks/ADCoinX/adcoin-validator-ai?style=social)
![Stars](https://img.shields.io/github/stars/ADCoinX/adcoin-validator-ai?style=social)
[![Applying XRPL Grants](https://img.shields.io/badge/Applying-XRPL%20Grants-blue)](https://xrpl.org/grants)

---

## 📌 Project Overview
**ADC CryptoGuard Validator** is a **wallet security and compliance tool** focused on the **XRP Ledger (XRPL)**. It validates XRPL addresses, detects anomalies/scam patterns, and produces **ISO 20022-compliant** audit exports.

👤 **Builder Note:** Built and maintained by a **solo founder (ADCX Lab)**. Grant support will fund scaling while keeping the project transparent and open-source.

**Objectives**
- Protect XRPL users from high-risk/scam wallets
- Provide audit-ready ISO 20022 XML exports
- Keep everything lightweight, privacy-first, and API-driven (no sensitive data stored)

---

## 🔎 XRPL Module (✅ Active)
- XRPL address validation (`r...`)
- Scam & fraudulent interaction detection
- Dynamic wallet **risk score (0–100)**
- **ISO 20022 XML** export for auditors
- **Planned (Next):** XRP balance check + validator/RPC integration

---

## 🗂️ Repository Structure
- `/core/` – AI risk scoring + ISO 20022 exporter (e.g., `ai_risk.py`, `iso_export.py`)
- `/integrations/xrpl/` – XRPL-specific logic (validators, fetchers, parsers)
- `/templates/` – Web frontend (HTML/CSS)
- `/static/` – Assets (logo, styles)

> **Note:** Some folders may include placeholder `.keep` files to avoid deployment crashes. Full expansion follows XRPL grant milestones.

---

## ⚙️ Technical Summary
- **Frontend:** HTML + CSS
- **Backend:** Python Flask
- **Risk Engine:** Local module (`ai_risk.py`) with heuristic scoring (0–100)
- **Data Sources:** **Public XRPL APIs** only (with fallback endpoints)
- **Compliance:** ISO 20022 XML via `iso_export.py`

---
## 🧩 Architecture (XRPL)

User/Reviewer → Flask API (`app.py`) → Address Router (detect XRPL `r...`) → XRPL Public API (public endpoints, with fallback) → AI Risk Engine (`ai_risk.py`, 0–100 scoring) → ISO 20022 Export (`iso_export.py`) → Outputs: JSON (risk_score, flags), ISO 20022 XML (audit), Web UI (templates/)

- Tech: HTML/CSS (frontend), Python Flask (backend), local risk heuristics, public XRPL data only (no secrets), redundancy via multi-backup endpoints, privacy-first (local processing).
- Repo paths: `/integrations/xrpl/` (validators/fetchers/parsers), `/core/` (`ai_risk.py`, `iso_export.py`), `/templates/`, `/static/`.

## 🔁 Request Flow (XRPL)

1) Client calls `POST /validate` with body: `{"chain":"xrpl","address":"r..."}`
2) Flask API → Address Router detects XRPL pattern (`r...`) and selects XRPL path.
3) Fetch snapshot from XRPL Public API (account/tx metadata; read-only; fallback if primary fails).
4) Pass snapshot → `ai_risk.py` → compute `risk_score` (0–100) + flags (e.g., scam interactions, anomalous activity).
5) Optional compliance: call `iso_export.py` → generate ISO 20022 XML report (returns file/string path).
6) API responds with JSON: `{ "chain":"xrpl", "address":"r...", "risk_score": <0-100>, "flags":[...], "iso20022_xml_url": "<optional>" }`
7) Frontend (templates/) renders summary; download button exposes the ISO 20022 XML.

### Notes
- No private keys or secrets stored; public API only.
- Timeouts + retries on upstream calls; fallbacks enabled.
- All processing local to preserve user privacy.

---

## 🔐 Security & Infosec
**Quality & Assurance**
- [![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)
- [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)
- [![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)

**Principles**
- No storage of secrets/private keys
- Public API calls only, with redundancy
- Local processing for user privacy

---
## 🔐 Funding Disclosure & Budget (XRPL Grant)

This repository contains a modular validator with XRPL-specific deliverables.  
I am a **solo builder** and the requested budget is **ring-fenced for XRPL only**.  
Shared modules are maintained as open-source, but **XRPL funds the XRPL-specific portions inside them**.

---

### 🟦 Core (XRPL-funded portions only)
These components are foundational, but XRPL grant covers **only XRPL-related logic**:
- **Validator Core (Backend)** (`app.py`) → XRPL wallet parsing & adapter logic  
- **AI Risk Engine** (`ai_risk.py`) → XRPL heuristics & anomaly scoring (base AI is neutral)  
- **ISO 20022 Exporter** (`iso_export.py`) → XRPL export profile (base module is neutral)  
- **API Handler + Fallback** (`api_handler.py`) → XRPL public API integration  
- **Frontend (Web/Mobile)** (`index.html`, `style.css`) → XRPL wallet validation UI  

---

### 🟨 XRPL-Specific (Funded Scope)
1. XRPL Wallet validation (addresses `r...`)  
2. Balance & activity snapshot via XRPL API  
3. XRPL anomaly rules & scam heuristics  
4. ISO 20022 (XRPL profile) export  
5. Reviewer Dashboard (XRPL-specific UI + reports)  
6. **Mobile (iOS/Android)**: lightweight XRPL wallet validation UI  

---

### ⚖️ Justification
- **No double funding**: Hedera-specific work is separate (`integrations/hedera`).  
- **Core modules**: XRPL funds only XRPL-related features; neutral/cross-chain code is not billed.  
- Transparency: public repo, open issues, SonarCloud quality checks.  

---

### 📅 Timeline (per XRPL grant)
- **Week 1–2**: Parser + wallet validation rules  
- **Week 3–4**: Balance snapshot + anomaly heuristics  
- **Week 5–6**: ISO 20022 XRPL profile export  
- **Week 7–8**: Reviewer dashboard + stabilization  
- **Mobile (iOS/Android)**: lightweight wallet validation UI added in **Week 3**  

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
