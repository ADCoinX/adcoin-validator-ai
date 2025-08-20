# ADC CryptoGuard Validator

[![Website](https://img.shields.io/badge/Website-AutoDigitalCoin.com-blue?logo=google-chrome)](https://autodigitalcoin.com)  
[![Live Validator](https://img.shields.io/badge/Validator-LIVE-green?logo=vercel)](https://adcoin-validator-ai.onrender.com)  
![ISO 20022](https://img.shields.io/badge/ISO%2020022-Compliant-blueviolet)  
![License](https://img.shields.io/badge/License-BY--NC--ND%204.0-lightgrey)  
![Repo Size](https://img.shields.io/github/repo-size/ADCoinX/adcoin-validator-ai)  
![Last Commit](https://img.shields.io/github/last-commit/ADCoinX/adcoin-validator-ai)  
![Issues](https://img.shields.io/github/issues/ADCoinX/adcoin-validator-ai)  
![Forks](https://img.shields.io/github/forks/ADCoinX/adcoin-validator-ai?style=social)  
![Stars](https://img.shields.io/github/stars/ADCoinX/adcoin-validator-ai?style=social)  

---

## ✅ Developed by

**Muhammad Yusri Adib**  
*Founder of ADCoin & ADCX Lab 🇲🇾*

🔗 Live Validator: [https://adcoin-validator-ai.onrender.com](https://adcoin-validator-ai.onrender.com)  
📩 Contact: admin@autodigitalcoin.com  

---

## 🛡️ XRPL Integration

ADC CryptoGuard integrates with the XRPL Mainnet and Sidechain to provide:  

- Validation of XRPL wallet addresses (`r…`)  
- Scam interaction detection  
- AI-powered risk scoring for XRPL wallets  
- ISO 20022 XML export of validated results  
- Planned: XRP balance check & validator lookup via XRPSCAN API  

---

## 🔧 Tech Stack

- **Frontend**: HTML + CSS (`templates/index.html`)  
- **Backend**: Python (Flask)  
- **AI Module**: `ai_risk.py` → calculates dynamic wallet risk scores  
- **Blockchain Integration**:
  - Ethereum → Etherscan API  
  - TRON → TronGrid API  
  - Bitcoin → BlockCypher API  
  - Solana → Helius API  
  - XRP → XRPSCAN / XRP Explorer  
- **ISO 20022**: XML export via `iso_export.py`  

---

## 🧠 AI Risk Module

The **AI Risk Engine** (`ai_risk.py`) is a lightweight module that:  

- Analyzes wallet transaction history  
- Flags suspicious or scam-related activity  
- Generates a **dynamic risk score** (0–100)  
- Runs locally (no sensitive API keys stored)  
- Uses fallback public APIs for redundancy  

---

## 🔐 Security & Infosec Compliance

We prioritize security, transparency, and code quality across all ADCX Lab projects.  

### 📊 Code Quality & Security Scans
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_adcoin-validator-ai&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=ADCoinX_adcoin-validator-ai)  

### 🛡️ Security Practices
- No sensitive API keys or credentials stored in this repo  
- All blockchain data fetched from **public APIs only**  
- Regular scans via **SonarQube / SonarCloud**  
- Dependencies monitored via **Dependabot**  
- Public transparency for Infosec reviewers  

### 📂 Compliance Evidence
- ISO 20022 XML Export (`iso_export.py`)  
- Continuous scanning results (see badges above ✅)  

---

> ⚠️ *Disclaimer*: This project is for **educational and security research purposes**.  
> Final decisions and risk assessments remain the responsibility of the user.  

---

## 🎯 Branding & Logo Usage

This project uses the official **ADCoin Validator** logo located at:  
📁 `static/logo.png`  

⚠️ **Do not remove, replace, or reuse this logo.**  
All branding is under ADCX Lab’s copyright.  

📩 Contact: admin@autodigitalcoin.com  

---

## 📄 License

This project is licensed under:  

**Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International**  
🔗 [https://creativecommons.org/licenses/by-nc-nd/4.0](https://creativecommons.org/licenses/by-nc-nd/4.0)
