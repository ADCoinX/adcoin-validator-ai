# ADC CryptoGuard Validator – Multi-Chain Security Framework

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
[![Applying Hedera Thrive](https://img.shields.io/badge/Applying-Hedera%20Thrive-green)](https://thrivehedera.com)  

---

## 📌 Project Overview

**ADC CryptoGuard Validator** is a **multi-chain wallet security and compliance tool** developed by **ADCX Lab**.  
It provides validation, anomaly detection, and risk scoring across leading blockchain ecosystems.  

The framework is designed to support **regulatory compliance (ISO 20022)** while enabling scalable risk monitoring for:  
- **XRPL** (XRP Ledger) — ✅ Active  
- **Hedera** (HBAR) — ✅ Active  
- Ethereum, Bitcoin, TRON, Solana (extended support modules – roadmap)  

**Primary Objective**:  
✔️ Strengthen trust in blockchain transactions through transparent wallet validation.  
✔️ Support **audit-ready data exports** for compliance teams.  
✔️ Deliver a **lightweight, API-driven validator** without storing sensitive user information.  

---

## 📈 Funding & Ecosystem Alignment  

ADC CryptoGuard is seeking support to scale multi-chain features:  
- Applying for **XRPL Grants**: To enhance XRPL validation and add XRP balance checks.  
- Applying for **Hedera Launch Program (via Thrive Protocol)**: To integrate Hedera HTS token security.  

**Reasons for Dual Grants (For Reviewers):**  
1. **Scalable Security for Emerging Ecosystems**: By integrating XRPL and Hedera, ADC CryptoGuard addresses scam risks in high-growth networks like Southeast Asia, where crypto fraud exceeds $20B annually (per Chainalysis reports), enabling broader user protection through AI-driven validation.  
2. **Compliance-Ready Innovation**: The tool's ISO 20022 XML exports facilitate regulatory audits, aligning with enterprise needs on Hedera and XRPL, while funding will accelerate certifications like GDPR/PDPA for global adoption.  
3. **Multi-Chain Utility Without Compromise**: Seeking dual grants ensures focused enhancements (e.g., XRPL balance checks, Hedera HTS integrations) while maintaining a unified, open-source framework, maximizing impact on Web3 safety without ecosystem silos.  

---

### 🔎 Note for Reviewers  

This repository is developed by a **solo builder** under ADCX Lab.  
Separate README versions are prepared for **XRPL Grants** and **Hedera Thrive/Launch Program** to reflect each ecosystem’s priorities.  

While the **core engine** is shared, the focus and deliverables differ:  
- **XRPL** → wallet validation, XRP balance, community fraud protection.  
- **Hedera** → HTS token security, enterprise compliance, ISO 20022 integration.  

This ensures alignment without duplicating efforts across ecosystems.  


---
## Funding Disclosures
- [XRPL Scope & Budget](docs/README.XRPL.md)
- [Hedera Scope & Budget](docs/README.HEDERA.md)
---

## 🔎 Chain-Specific Modules

### XRPL Module (✅ Active)
- Address validation (`r...`)  
- Scam & fraudulent interaction detection  
- Dynamic wallet risk scoring  
- ISO 20022 XML export  
- Planned (Next): XRP balance check & validator integration via XRPL RPC  

### Hedera Module (✅ Active)
- Account validation (`0.0.x`)  
- On-chain metadata parsing via Mirror Node API  
- Risk & anomaly detection  
- ISO 20022 XML export  
- Planned (Next): deeper HTS token security & explorer API integration  

### Extended Roadmap
- Ethereum (`0x...`) – wallet + token/NFT validator  
- Bitcoin (`bc1...`, `1...`, `3...`) – scam flagging & anomaly checks  
- TRON (`T...`) – scam wallet blacklist + balance scan  
- Solana (`44-char address`) – scam detection + token audit  

---

## 🗂️ Repository Structure

- `/core/`: Shared AI and export modules (e.g., ai_risk.py, iso_export.py).  
- `/integrations/`: Chain-specific code (e.g., xrpl/, hedera/, future ETH/BTC/TRON/SOL).  
- `/templates/`: Frontend HTML/CSS.  
- `/static/`: Assets like logo.png.  

> **Note (Grant-Dependent Expansion):**  
> Some directories (e.g., `/core.keep`, `/integrations/xrpl`, `/integrations/hedera`) are currently placeholders to prevent project crash during deployment.  
> Full modules will be populated once funding is secured, ensuring smooth integration without breaking the live validator.  

---

## 👤 Development Model

ADC CryptoGuard Validator is currently built and maintained by a **solo builder** under ADCX Lab.  
- Ensures **fast iteration** and **lean development**.  
- Transparent, open-source contributions welcome.  
- Funding support (via XRPL / Hedera grants) will allow expansion into a **small dedicated security team** for scaling multi-chain modules.  

---

## ⚙️ Technical Architecture

- **Frontend**: HTML + CSS (lightweight web interface)  
- **Backend**: Python Flask  
- **AI Risk Engine**: Local scoring module (`ai_risk.py`) with 0–100 scale  
- **Blockchain Data**: Fetched from **public fallback APIs** only (no private key usage)  
- **ISO 20022 Compliance**: Structured XML export (`iso_export.py`)

---

## 🧩 System Design (High-Level + Flow)

**High-Level Architecture (Compressed)**  
User/Reviewer (Web UI or cURL) → Flask API (app.py) → Address Router (detect chain) →  
• XRPL Public API / Explorer  
• Hedera Mirror Node API  
• Roadmap: ETH / BTC / TRON / SOL  
→ AI Risk Engine (ai_risk.py) → ISO 20022 Export (iso_export.py) →  
Outputs: JSON (risk_score, findings) + ISO 20022 XML + Frontend Templates (HTML/CSS)  
Security Layer: SonarCloud (Quality Gate) + Dependabot (Dependencies)  

**Request Flow (Sequence – Simplified)**  
1. User submits POST /validate {"chain":"xrpl","address":"r..."} or {"chain":"hedera","address":"0.0.x"}  
2. Flask API routes to Address Router → detect chain type  
3. Router fetches snapshot:  
   • XRPL → Public API  
   • Hedera → Mirror Node  
   • Other chains → Roadmap endpoints  
4. Router sends snapshot → AI Risk Engine → calculate risk_score (0–100)  
5. API optionally calls ISO 20022 Export → build XML  
6. API returns response → JSON + (optional) ISO XML link  

---

## 🔐 Security & Infosec Alignment

ADCX Lab applies industry best practices in software assurance and compliance.  

### Quality & Assurance
- Continuous analysis via **SonarQube / SonarCloud**  
- Dependency management via **Dependabot**  
- Transparent repository metrics (see badges above)  

### Security Principles
- No storage of sensitive keys or credentials  
- Public blockchain API calls only  
- Redundancy via multi-backup public endpoints  
- Local execution ensures data privacy  

---

## 📊 Compliance Readiness

- **ISO 20022**: Structured XML export available for audit teams (self-compliant; certification in progress)  
- **Transparency**: Open-source validation, code scans publicly visible  
- **Infosec Evidence**:  
  - [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  
  - [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  
  - [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  

---
## 🔐 Funding Disclosure & Non-Overlap (Important for Reviewers)

This repository contains a unified, modular validator with chain-specific deliverables. I am a **solo builder**, and I am applying to **two ecosystem programs** with **clearly separated scopes** to avoid any double funding.

### What each grant funds (non-overlapping)
- **XRPL Grant — Scope**
  1) XRPL wallet validation enhancements (address `r...`, quality checks)
  2) XRP balance & activity snapshot via public XRPL endpoints
  3) XRPL-specific anomaly rules & scam heuristics
  4) Export to ISO 20022 (XRPL profile) + lightweight reviewer dashboard
  5) Mobile (iOS/Android) — XRPL wallet checker (balances + scam heuristics)  
  **Milestones**: M1 Parser & heuristics · M2 Balance snapshot · M3 ISO export (XRPL) · M4 Reviewer dashboard (XRPL) · M5 Mobile XRPL app

- **Hedera Thrive/Launch — Scope**
  1) Hedera account validation (account `0.0.x`)
  2) Mirror Node integration (accounts/transactions)
  3) HTS token safety checks (selected tokens, basic policy rules)
  4) Export to ISO 20022 (Hedera profile)
  5) Mobile (iOS/Android) — Hedera wallet checker (HTS token safety + account lookup)  
  **Milestones**: H1 Mirror Node ingestion · H2 HTS checks · H3 ISO export (Hedera) · H4 Compliance report (Hedera) · H5 Mobile Hedera app

> **No shared deliverable is billed twice.** Shared core utilities (e.g., `ai_risk.py`, `iso_export.py`) are funded by **neither grant**; they are open-source foundation work maintained at my own cost unless a program explicitly requests enhancements unique to that chain.

### If both grants are approved
- I will **ring-fence budgets and branches**:
  - `integrations/xrpl` ← XRPL-funded tasks only  
  - `integrations/hedera` ← Hedera-funded tasks only
- Separate progress tracking (issues, PR labels, milestone boards) per ecosystem.
- Shared work (refactors, infra, docs) remains **unfunded** or will be **explicitly attributed** to a single program if requested.

### If only one grant is approved
- I will **deliver that chain’s milestones in full**.
- The other chain remains active but limited to unfunded, best-effort maintenance until separate funding is confirmed.

### Capacity & resourcing (solo builder)
- Current status: solo builder with open-source transparency (SonarCloud, Dependabot).
- Hiring plan (grant-dependent): 1) Blockchain dev (validator/API) → 2) Frontend or Mobile (UI) → 3) AI/Security.
- Risk controls: public API only (no keys), local processing, fallback endpoints, ISO 20022 export profiles per chain.

### Timeline (high-level, per approved grant)
- Week 1–2: finalize chain adapters + endpoint fallbacks
- Week 3–4: implement chain-specific heuristics + tests
- Week 3–5: develop Mobile (iOS/Android) app tailored per chain
- Week 5–6: ISO 20022 export profile + reviewer view
- Week 7–8: stabilization, docs, and compliance evidence

### Contact
For any clarification on scope separation or budgeting, please reach out: **admin@autodigitalcoin.com**
---

## ⚠️ Disclaimer

This system is intended for **educational, research, and compliance validation purposes** only.  
ADCX Lab does not provide financial, investment, or legal guarantees.  
Final responsibility for risk assessment remains with the user or institution.  

---

## 📞 Contact Information

👤 **Muhammad Yusri Adib**  
Founder – ADCX Lab  

📩 Email: admin@autodigitalcoin.com  
💬 Telegram: [@ADCoinhelpline](https://t.me/ADCoinhelpline)  
🐦 Twitter: [@AdCoinMy](https://twitter.com/AdCoinMy)  
🔗 LinkedIn: [Muhammad Yusri Adib](https://www.linkedin.com/in/muhammad-yusri-adib)  
