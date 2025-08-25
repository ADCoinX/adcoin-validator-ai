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
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)  
![Tests](https://img.shields.io/badge/Tests-Covered-blue)  

---

## 📌 Project Overview  

**ADC CryptoGuard Validator** is a **wallet security and compliance tool** built for the **XRP Ledger (XRPL)**.  
It validates XRPL addresses, detects anomalies or scam activity, and generates **ISO 20022-compliant audit exports**.  

👤 **Development Model:**  
Built and maintained by a **solo builder (ADCX Lab)** with lean execution, fast iteration, and open transparency. Funding will enable expansion into a small dedicated team (blockchain dev + frontend/mobile + AI/security).  

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

## 💬 Founder’s Note  

This project is built by me as a **solo builder** from Malaysia under **ADCX Lab**.  
I started ADC CryptoGuard because I saw too many people around me – especially in Southeast Asia – losing money to scams.  

I am applying for this grant because **without support, it will be very hard for me to continue scaling this work alone**.  
I don’t have a team or large funding – just commitment, faith, and the hope that this tool can make Web3 safer for everyone.  

🙏 Any support means the world to me, and I will dedicate myself fully to delivering impact for the XRPL community.  

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

---

## 📞 Contact  

👤 **Muhammad Yusri Adib**  
Founder – ADCX Lab (Solo Builder)  

📩 Email: admin@autodigitalcoin.com  
💬 Telegram: [@ADCoinhelpline](https://t.me/ADCoinhelpline)  
🐦 Twitter: [@AdCoinMy](https://twitter.com/AdCoinMy)  
🔗 LinkedIn: [Muhammad Yusri Adib](https://www.linkedin.com/in/muhammad-yusri-adib)  
