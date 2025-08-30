# ADC CryptoGuard Validator – XRPL Security Framework  

[![Website](https://img.shields.io/badge/Website-AutoDigitalCoin.com-blue?logo=google-chrome)](https://autodigitalcoin.com)  
[![Live Validator](https://img.shields.io/badge/Validator-LIVE-green?logo=vercel)](https://adcoin-validator-ai.onrender.com)  
![ISO 20022](https://img.shields.io/badge/ISO%2020022-Compliant-blueviolet)  
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Repo Size](https://img.shields.io/github/repo-size/ADCoinX/adcoin-validator-ai)  
![Last Commit](https://img.shields.io/github/last-commit/ADCoinX/adcoin-validator-ai)  
![Issues](https://img.shields.io/github/issues/ADCoinX/adcoin-validator-ai)  
![Forks](https://img.shields.io/github/forks/ADCoinX/adcoin-validator-ai?style=social)  
![Stars](https://img.shields.io/github/stars/ADCoinX/adcoin-validator-ai?style=social)  
[![Applying XRPL Grants](https://img.shields.io/badge/Applying-XRPL%20Grants-blue)](https://xrpl.org/grants)  
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)  
![Tests](https://img.shields.io/badge/Tests-Covered-blue)  

---

## 📌 Project Overview  

**ADC CryptoGuard Validator** is a **wallet security and compliance tool** built for the **XRP Ledger (XRPL)**.  
It validates XRPL addresses, detects anomalies or scam activity, and generates **ISO 20022-compliant audit exports**.  

👤 **Development Model:**  
Built and maintained by ADCX Lab with lean execution, fast iteration, and open transparency. Funding will enable expansion into a small dedicated team (blockchain dev + frontend/mobile + AI/security).  

**Objectives:**  
- Protect XRPL users from scam & high-risk wallets  
- Provide audit-ready compliance reports (ISO 20022 XML)  
- Deliver AI-powered wallet risk scoring with zero user data stored  

---

## 🔎 XRPL Module (✅ Active)  

- XRPL address validation (`r...`)  
- AI-driven anomaly detection (suspicious flows, scam tags)  
- Dynamic wallet **risk score (0–100)**  
- **ISO 20022 XML export** for auditors  
- Planned: XRP balance snapshot + RPC validator integration  

---

## 🗂️ Repository Structure  

```
core/            → AI risk engine, ISO exporter  
integrations/    → XRPL-specific logic (validators, parsers)  
templates/       → Web frontend (HTML/CSS)  
static/          → Assets (logo, styles)  
```

---

## ⚙️ Technical Summary  

- **Frontend:** HTML + CSS  
- **Backend:** Python Flask  
- **AI Risk Engine:** Local scoring (0–100, heuristics + anomaly rules)  
- **Data Sources:** XRPL Public API + fallback endpoints  
- **Compliance:** ISO 20022 XML via `iso_export.py`  

---

## 🧩 System Design  

```
User (UI / API)
   ↓
Flask API (app.py)
   ↓
XRPL Public API (snapshot)
   ↓
AI Risk Engine (ai_risk.py)
   ↓
ISO Export (iso_export.py)
   ↓
JSON / ISO XML → Reviewer Dashboard
```  
---
## 🧩 System Architecture (Visual)

```
+------------------+        +--------------------+        +------------------+
|   User / Client  | -----> |  Flask API Router  | -----> |  XRPL Public API |
| (Web UI / cURL)  |        |  (app.py)          |        |  (snapshot data) |
+------------------+        +--------------------+        +------------------+
                                      |
                                      v
                            +---------------------+
                            |   AI Risk Engine    |
                            |   (ai_risk.py)      |
                            |  Score: 0 – 100     |
                            +---------------------+
                                      |
                                      v
                            +---------------------+
                            |   ISO Exporter      |
                            |   (iso_export.py)   |
                            |  ISO 20022 XML Out  |
                            +---------------------+
                                      |
                                      v
                        +-------------------------------+
                        |  JSON API Response + XML File |
                        |  Shown in Reviewer Dashboard  |
                        +-------------------------------+
```
---

## 🚀 Upgrade Plan (Grant-Funded Enhancements)  

If funded through **XRPL Grants**, ADC CryptoGuard will accelerate the following:  

### 🔥 AI Risk Engine (Upgrade)  
- ML anomaly detection (unsupervised clustering for scam patterns).  
- Wallet-to-wallet graph analysis.  
- Multi-metric scoring (age, tx diversity, liquidity anomalies, blacklist).  
- Reviewer dashboard → **explainable AI**.  

### 🔥 ISO 20022 Export (Upgrade)  
- XRPL-specific ISO 20022 profiles (wallet + tx metadata).  
- Multi-standard compliance (GDPR/PDPA).  
- Enterprise-ready integration (SAP, Oracle).  
- Automated XML download in dashboard.  

---

## 🛠️ API Endpoints (Sample)  

### Health Check
```bash
curl -X GET https://<backend-url>/healthz
```

### XRPL Validation
```bash
curl -X POST https://<backend-url>/validate \
  -H "Content-Type: application/json" \
  -d '{"chain":"xrpl","address":"rEXAMPLE"}'
```

### ISO 20022 Export
```bash
curl -X POST https://<backend-url>/iso/export \
  -H "Content-Type: application/json" \
  -d '{"address":"rEXAMPLE"}'
```

---
## 🔐 Security & Threat Model

At ADCX Lab, safety isn’t an afterthought — it’s built in from day one.  
Even in the demo stage, we evaluate potential risks and mitigation paths.

### 📊 Threat Matrix – CryptoGuard (XRPL)

| Threat / Attack Vector        | Likelihood | Impact | Notes & Mitigation |
|-------------------------------|------------|--------|---------------------|
| **DDoS / API Spam**           | High       | Medium | Rate limiting, Cloudflare, fallback nodes |
| **API Dependency Abuse**      | High       | Medium | Multiple API keys, caching, fallback APIs |
| **Phishing / Clone Website**  | Medium     | High   | Official domain, SSL cert, verified links |
| **XSS / Input Injection**     | Medium     | Medium | Strict input validation & sanitization |
| **AI Risk Engine Bypass**     | Low/Med    | Medium | Hybrid rules + AI, manual blacklist |
| **Blacklist Poisoning**       | Low/Med    | Low/Med| Moderated entries, hash verification |
| **ISO 20022 Export Injection**| Low        | Medium | XML schema validation, sanitize input |
| **Google Sheets Log Abuse**   | Medium     | Low/Med| Env-secured keys, migrate to DB w/ auth |

### ⚖️ Summary
- Highest risk (short-term): **DDoS / API spam** and **Phishing clones**  
- Medium risk: **XSS, API dependency abuse, AI bypass**  
- Lower risk: **ISO export injection, log poisoning**  
- **Mitigation plan**: Rate limiting, SSL cert, schema validation, multi-API redundancy, DB migration

---
## 🚀 Project Status – CryptoGuard (XRPL)

**Live Demo:** https://adcoin-validator-ai.onrender.com  
**Repository:** https://github.com/ADCoinX/adcoin-validator-ai  

### ✅ Completed
- Wallet validation via public APIs (XRPL Explorer, Etherscan, BlockCypher)
- AI risk scoring engine (hybrid rule-based + scoring weights)
- ISO 20022 XML export module
- Google Sheets logging for traction tracking
- Public demo deployment (Render.com)

### 🚧 In Progress
- Improve input sanitization for XML export
- API fallback & caching to handle rate-limit issues
- Basic monitoring for uptime / error logging

### 🔜 Planned
- Rate limiting & DDoS protection (Cloudflare / API Gateway)
- Domain verification + anti-phishing (official ADCX domain)
- Migration from Google Sheets → secure DB (with authentication)
- More chain integrations (multi-chain support beyond XRPL)

---

## 💡 Use Cases  

- **Compliance teams**: Generate ISO 20022 XML reports for audits.  
- **Wallet providers**: Integrate scam wallet checks before transactions.  
- **Exchanges**: Run anomaly detection to reduce fraud risk.  
- **Developers**: Access validator via lightweight API.  

---

## 📈 Roadmap (XRPL-Focused)  

- **M1** → Enhanced heuristics for scam wallet detection  
- **M2** → XRP balance + validator integration  
- **M3** → ISO 20022 export finalized for XRPL  
- **M4** → Reviewer dashboard (risk visualization + ISO download)  
- **M5** → Mobile wallet checker (iOS/Android, XRPL only)  

---

## 🤝 Contributor Guide  

We welcome contributions from the community to strengthen **wallet safety on XRPL**.  

**How to Contribute:**  
1. Fork this repo & create a new branch (`feature/your-feature`).  
2. Commit your changes with clear messages.  
3. Open a Pull Request – describe what and why.  
4. All contributions will be reviewed openly and transparently.  

**Areas where help is valuable:**  
- Improving AI heuristics & ML scoring  
- Expanding ISO 20022 profiles  
- Frontend/mobile UI contributions  
- Documentation & testing  

---

## Team & Governance

**Core Team**
- **Muhammad Yusri Adib — Founder / CTO**  
  Focus: architecture, AI risk engine, XRPL integrations, ISO 20022 exporter.  
  Commitment: Full-time.  
  [LinkedIn](http://linkedin.com/in/yusri-adib-455aa8b7)

- **Muhammad Mustafa, CPA, CFE, CMA, CIA — Co-Founder / Finance & Compliance Lead**  
  Focus: governance, audit & reporting, budget control, regulatory alignment.  
  Commitment: Full-time.  
  [LinkedIn](http://linkedin.com/in/muhammad-mustafa-abdulmanaf)

**Governance & Quality**
- `main` branch is protected: peer reviews + CI checks required before merge.  
- Secrets managed via GitHub Encrypted Secrets.  
- No user data stored; validator is privacy-first.  
- Vulnerability reporting per `SECURITY.md` — 72-hour SLA for high-severity issues.

**Grant Use (XRPL-specific)**
XRPL Grant funds will be applied **only to XRPL deliverables**, including:  
1. Wallet validation heuristics for XRPL.  
2. XRPL balance & transaction anomaly detection.  
3. ISO 20022 schema tailored for XRPL.  
4. QA, testing, and documentation for XRPL module.

---

## 🔐 Security & Infosec  

**Quality & Assurance**  
- [![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  
- [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  
- [![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  

**Principles:**  
- No storage of keys or PII  
- Public API calls only, with redundancy  
- Local, privacy-first execution  

---

## ⚠️ Disclaimer  

This tool is for **educational, research, and compliance validation** only.  
ADCX Lab does not provide financial, investment, or legal guarantees.  
Code is open-sourced under MIT License; provided as-is with no warranties.

---

## 📞 Contact  

👤 **Muhammad Yusri Adib**  
Founder – ADCX Lab

📩 Email: admin@autodigitalcoin.com  
💬 Telegram: [@ADCoinhelpline](https://t.me/ADCoinhelpline)  
🐦 Twitter: [@AdCoinMy](https://twitter.com/AdCoinMy)  
🔗 LinkedIn: [Muhammad Yusri Adib](https://www.linkedin.com/in/muhammad-yusri-adib)  
