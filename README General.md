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
