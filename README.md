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
- **XRPL** (XRP Ledger)  
- **Hedera** (HBAR)  
- Ethereum, Bitcoin, TRON, Solana (extended support modules)  

Primary Objective:  
✔️ Strengthen trust in blockchain transactions through transparent wallet validation.  
✔️ Support **audit-ready data exports** for compliance teams.  
✔️ Deliver a **lightweight, API-driven validator** without storing sensitive user information.  

---

## 📈 Funding & Ecosystem Alignment

ADC CryptoGuard is seeking support to scale multi-chain features:  
- Applying for XRPL Grants: To enhance XRPL validation and add XRP balance checks.  
- Applying for Hedera Launch Program (via Thrive Protocol): To integrate Hedera Mirror Node API and HTS token security.  

Check grant-specific branches: `xrpl-grant` for XRPL prototypes, `hedera-grant` for Hedera developments.  

---

## 🔎 Chain-Specific Modules

### XRPL Module
- Address validation (`r...`)  
- Scam & fraudulent interaction detection  
- Dynamic wallet risk scoring  
- ISO 20022 XML export  
- Planned (Post-Funding): XRP balance check & validator integration  

### Hedera Module
- Account validation (`0.0.x`)  
- On-chain metadata parsing  
- Risk & anomaly detection  
- ISO 20022 XML export  
- Planned (Post-Funding): HBAR explorer API integration  

---

## 🗂️ Repository Structure

- `/core/`: Shared AI and export modules (e.g., ai_risk.py, iso_export.py).  
- `/integrations/xrpl/`: XRPL-specific code.  
- `/integrations/hedera/`: Hedera prototype code.  
- `/templates/`: Frontend HTML/CSS.  
- `/static/`: Assets like logo.png.  

---

## ⚙️ Technical Architecture

- **Frontend**: HTML + CSS (lightweight web interface)  
- **Backend**: Python Flask  
- **AI Risk Engine**: Local scoring module (`ai_risk.py`) with 0–100 scale  
- **Blockchain Data**: Fetched from **public fallback APIs** only (no private key usage)  
- **ISO 20022 Compliance**: Structured XML export (`iso_export.py`)  

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
