from flask import Flask, render_template, request
import requests
import re
import os

app = Flask(__name__)

# AI score based on simple rule
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

# Chain detector
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

# ETH balance and tx (ethplorer)
def get_eth_data(address):
    url = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey"
    r = requests.get(url).json()
    balance = r.get("ETH", {}).get("balance", 0)
    txs = r.get("transactions", [])[:10]
    return balance, txs

# TRON (tronscan)
def get_tron_data(address):
    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    r = requests.get(url).json()
    balance = r.get("balance", 0) / 1e6
    txs_url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit=10"
    txs = requests.get(txs_url).json().get("data", [])
    return balance, txs

# BTC (blockstream)
def get_btc_data(address):
    url = f"https://blockstream.info/api/address/{address}"
    r = requests.get(url).json()
    balance = r.get("chain_stats", {}).get("funded_txo_sum", 0) / 1e8
    txs_url = f"https://blockstream.info/api/address/{address}/txs"
    txs = requests.get(txs_url).json()[:10]
    return balance, txs

# XRP
def get_xrp_data(address):
    url = f"https://api.xrpscan.com/api/v1/account/{address}/summary"
    r = requests.get(url).json()
    balance = float(r.get("xrpBalance", 0))
    tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?limit=10"
    txs = requests.get(tx_url).json()
    return balance, txs

# Solana
def get_solana_data(address):
    url = f"https://public-api.solscan.io/account/{address}"
    headers = {"accept": "application/json"}
    r = requests.get(url, headers=headers).json()
    balance = r.get("lamports", 0) / 1e9
    tx_url = f"https://public-api.solscan.io/account/transactions?account={address}&limit=10"
    txs = requests.get(tx_url, headers=headers).json()
    return balance, txs

# Main UI
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Handle POST
@app.route('/validate', methods=['POST'])
def validate():
    result = None
    if request.method == 'POST':
        address = request.form['wallet']
        chain = detect_chain(address)
        balance, txs = 0, []

        try:
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
        except:
            txs = []

        ai_score = get_ai_score(balance, len(txs))
        result = {
            'address': address,
            'chain': chain,
            'balance': balance,
            'txs': txs,
            'ai_score': ai_score
        }

    return render_template('index.html', result=result)

# Render hosting port fix
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
