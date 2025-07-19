
from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

blacklist = [
    "0x000000000000000000000000000000000000dead",
    "0x1111111111111111111111111111111111111111"
]


def ai_risk_score(address, balance_eth=0.0, tx_count=0):
    address = address.lower()
    if address in blacklist:
        return "SCAM 🚨"
    if len(address) < 10:
        return "High Risk ❗ (Suspicious address)"
    if balance_eth == 0 and tx_count == 0:
        return "High Risk ❗ (Empty wallet, no activity)"
    if balance_eth == 0:
        return "Medium Risk ⚠️ (No balance)"
    if balance_eth > 0.1 and tx_count > 5:
        return "Low Risk ✅"
    if tx_count < 2:
        return "Medium Risk ⚠️ (Inactive wallet)"
    return "Unknown"


def check_ethereum_wallet(address):
    url_balance = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
    url_txcount = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionCount&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"

    r_balance = requests.get(url_balance)
    r_tx = requests.get(url_txcount)

    eth_balance = 0.0
    tx_count = 0

    if r_balance.status_code == 200 and r_balance.json().get("status") == "1":
        eth_balance = int(r_balance.json()["result"]) / 10**18
    if r_tx.status_code == 200 and r_tx.json().get("result"):
        tx_count = int(r_tx.json()["result"], 16)

    risk = ai_risk_score(address, eth_balance, tx_count)
    return f"ETH Balance: {eth_balance:.4f} ETH\nTx Count: {tx_count}\nRisk Level: {risk}\n"

def check_tron_wallet(address):
    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    r = requests.get(url)
    data = r.json()
    if "balance" in data:
        trx_balance = data["balance"] / 1000000
        return f"TRX Balance: {trx_balance:.2f} TRX\n"
    return "TRON wallet not found or empty.\n"

def check_btc_wallet(address):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        btc_balance = data["final_balance"] / 10**8
        return f"BTC Balance: {btc_balance:.5f} BTC\n"
    return "Invalid or empty BTC wallet.\n"

def check_xrp_wallet(address):
    url = f"https://api.xrpscan.com/api/v1/account/{address}"
    r = requests.get(url)
    if r.status_code == 200 and "balance" in r.json():
        xrp = float(r.json()["balance"])
        return f"XRP Balance: {xrp:.2f} XRP\n"
    return "Invalid or empty XRP wallet.\n"

def check_solana_wallet(address):
    url = f"https://api.solana.fm/v0/accounts/{address}?cluster=mainnet"
    headers = {"accept": "application/json"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and "lamports" in r.text:
        return f"Solana wallet detected (details available on SolanaFM)\n"
    return "Invalid or empty Solana wallet.\n"

def check_bsc_wallet(address):
    return "BSC check placeholder. Add BSCScan API key to enable.\n"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        wallet = request.form["wallet"]
        result = ""
        if wallet.startswith("0x"):
            result += check_ethereum_wallet(wallet)
            result += check_bsc_wallet(wallet)
        elif wallet.startswith("T"):
            result += check_tron_wallet(wallet)
        elif wallet.startswith("1") or wallet.startswith("3") or wallet.startswith("bc1"):
            result += check_btc_wallet(wallet)
        elif wallet.startswith("r"):
            result += check_xrp_wallet(wallet)
        elif len(wallet) >= 32:
            result += check_solana_wallet(wallet)
        else:
            result = "Unsupported or unknown wallet type."
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
