
from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")  # kau kena isi ini nanti

blacklist = ["0x000000000000000000000000000000000000dead", "0x1111111111111111111111111111111111111111"]

def ai_risk_score(address, balance=0.0, tx_count=0):
    address = address.lower()
    if address in blacklist:
        return "SCAM 🚨"
    if len(address) < 10:
        return "High Risk ❗ (Suspicious address)"
    if balance == 0 and tx_count == 0:
        return "High Risk ❗ (Empty wallet, no activity)"
    if balance == 0:
        return "Medium Risk ⚠️ (No balance)"
    if balance > 0.1 and tx_count > 5:
        return "Low Risk ✅"
    if tx_count < 2:
        return "Medium Risk ⚠️ (Inactive wallet)"
    return "Unknown"

def check_ethereum_wallet(address):
    balance_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"
    tx_url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionCount&address={address}&apikey={ETHERSCAN_API_KEY}"

    balance_eth = int(requests.get(balance_url).json()["result"]) / 10**18
    tx_count = int(requests.get(tx_url).json()["result"], 16)

    risk = ai_risk_score(address, balance_eth, tx_count)
    return f"ETH Balance: {balance_eth:.4f} ETH\nTx Count: {tx_count}\nRisk Level: {risk}\n"

def check_tron_wallet(address):
    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    data = requests.get(url).json()
    balance = data.get("balance", 0) / 1e6
    tx_count = data.get("transactions", 0)
    risk = ai_risk_score(address, balance, tx_count)
    return f"TRX Balance: {balance:.2f} TRX\nRisk Level: {risk}\n"

def check_btc_wallet(address):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
    data = requests.get(url).json()
    balance = data.get("final_balance", 0) / 1e8
    tx_count = data.get("n_tx", 0)
    risk = ai_risk_score(address, balance, tx_count)
    return f"BTC Balance: {balance:.5f} BTC\nRisk Level: {risk}\n"

def check_xrp_wallet(address):
    url = f"https://api.xrpscan.com/api/v1/account/{address}"
    data = requests.get(url).json()
    balance = float(data.get("balance", 0))
    tx_count = data.get("sequence", 0)
    risk = ai_risk_score(address, balance, tx_count)
    return f"XRP Balance: {balance:.2f} XRP\nRisk Level: {risk}\n"

def check_solana_wallet(address):
    url = f"https://api.solana.fm/v0/accounts/{address}?cluster=mainnet"
    data = requests.get(url).json()
    lamports = data.get("lamports", 0)
    balance = lamports / 1e9
    risk = ai_risk_score(address, balance, 0)
    return f"SOL Balance: {balance:.4f} SOL\nRisk Level: {risk}\n"

def check_bsc_wallet(address):
    url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&apikey={BSCSCAN_API_KEY}"
    data = requests.get(url).json()
    balance = int(data["result"]) / 1e18
    risk = ai_risk_score(address, balance, 0)
    return f"BSC Balance: {balance:.4f} BNB\nRisk Level: {risk}\n"

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        wallet = request.form["wallet"]
        if wallet.startswith("0x"):
            result += check_ethereum_wallet(wallet)
            result += check_bsc_wallet(wallet)
        elif wallet.startswith("T"):
            result += check_tron_wallet(wallet)
        elif wallet.startswith(("1", "3", "bc1")):
            result += check_btc_wallet(wallet)
        elif wallet.startswith("r"):
            result += check_xrp_wallet(wallet)
        elif len(wallet) > 30:
            result += check_solana_wallet(wallet)
        else:
            result = "Unsupported wallet type."
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
