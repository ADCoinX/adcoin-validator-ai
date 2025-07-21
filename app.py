from flask import Flask, render_template, request
import requests
import re
import os

app = Flask(__name__)

# Etherscan API Key (Real)
ETHERSCAN_API_KEY = "ABUE4N8J7TVP6P2K7BXUTSC2AZWXJ9MIJD"

# AI Score logic
def get_ai_score(balance, tx_count):
    score = 100
    if balance == 0:
        score -= 40
    if tx_count == 0:
        score -= 40
    if balance < 0.01:
        score -= 10
    if tx_count < 3:
        score -= 10
    return max(score, 0)

# Chain detection
def detect_chain(address):
    if address.startswith("0x") and len(address) == 42:
        return "ethereum"
    elif address.startswith("T") and len(address) == 34:
        return "tron"
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        return "bitcoin"
    elif address.startswith("r") and len(address) > 24:
        return "xrp"
    elif re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", address):
        return "solana"
    else:
        return "unknown"

# Ethereum (Etherscan API)
def get_eth_data(address):
    try:
        balance_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
        balance_res = requests.get(balance_url, timeout=10).json()
        tx_res = requests.get(tx_url, timeout=10).json()
        balance = int(balance_res.get("result", 0)) / 1e18
        txs = tx_res.get("result", [])[:10]
        return balance, txs
    except Exception as e:
        print("ETHERSCAN ERROR:", e)
        return 0, []

# TRON (public)
def get_tron_data(address):
    try:
        url = f"https://apilist.tronscanapi.com/api/account?address={address}"
        r = requests.get(url, timeout=8).json()
        balance = r.get("balance", 0) / 1e6
        tx_url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit=10"
        txs = requests.get(tx_url, timeout=8).json().get("data", [])
        return balance, txs
    except Exception as e:
        print("TRON ERROR:", e)
        return 0, []

# Bitcoin (public)
def get_btc_data(address):
    try:
        url = f"https://blockstream.info/api/address/{address}"
        r = requests.get(url, timeout=8).json()
        balance = r.get("chain_stats", {}).get("funded_txo_sum", 0) / 1e8
        tx_url = f"https://blockstream.info/api/address/{address}/txs"
        txs = requests.get(tx_url, timeout=8).json()[:10]
        return balance, txs
    except Exception as e:
        print("BTC ERROR:", e)
        return 0, []

# XRP (public)
def get_xrp_data(address):
    try:
        url = f"https://api.xrpscan.com/api/v1/account/{address}/summary"
        r = requests.get(url, timeout=8).json()
        balance = float(r.get("xrpBalance", 0))
        tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?limit=10"
        txs = requests.get(tx_url, timeout=8).json()
        return balance, txs
    except Exception as e:
        print("XRP ERROR:", e)
        return 0, []

# Solana (public)
def get_solana_data(address):
    try:
        url = f"https://public-api.solscan.io/account/{address}"
        headers = {"accept": "application/json"}
        r = requests.get(url, headers=headers, timeout=8).json()
        balance = r.get("lamports", 0) / 1e9
        tx_url = f"https://public-api.solscan.io/account/transactions?account={address}&limit=10"
        txs = requests.get(tx_url, headers=headers, timeout=8).json()
        return balance, txs
    except Exception as e:
        print("SOLANA ERROR:", e)
        return 0, []

# Home route
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Validate route
@app.route('/validate', methods=['POST'])
def validate():
    result = None
    if request.method == 'POST':
        address = request.form['wallet']
        chain = detect_chain(address)
        balance, txs = 0, []

        if chain == "ethereum":
            balance, txs = get_eth_data(address)
        elif chain == "tron":
            balance, txs = get_tron_data(address)
        elif chain == "bitcoin":
            balance, txs = get_btc_data(address)
        elif chain == "xrp":
            balance, txs = get_xrp_data(address)
        elif chain == "solana":
            balance, txs = get_solana_data(address)

        ai_score = get_ai_score(balance, len(txs))
        result = {
            'address': address,
            'chain': chain,
            'balance': balance,
            'txs': txs,
            'ai_score': ai_score
        }

    return render_template('index.html', result=result)

# Render hosting port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
