
import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ETHERSCAN_API = os.getenv("ETHERSCAN_API")
BSCSCAN_API = os.getenv("BSCSCAN_API")

def get_eth_balance(wallet):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={wallet}&tag=latest&apikey={ETHERSCAN_API}"
        res = requests.get(url).json()
        return int(res["result"]) / 1e18
    except:
        return None

def get_eth_txs(wallet):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&startblock=0&endblock=99999999&sort=desc&apikey={ETHERSCAN_API}"
        res = requests.get(url).json()
        return res["result"][:10]
    except:
        return []

def get_bsc_balance(wallet):
    try:
        url = f"https://api.bscscan.com/api?module=account&action=balance&address={wallet}&apikey={BSCSCAN_API}"
        res = requests.get(url).json()
        return int(res["result"]) / 1e18
    except:
        return None

def ai_risk_score(balance, tx_count):
    if balance == 0 or tx_count == 0:
        return "⚠️ High Risk"
    elif tx_count < 5:
        return "🟡 Medium Risk"
    else:
        return "🟢 Low Risk"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    wallet = request.form['wallet']
    wallet = wallet.strip()

    eth_balance = get_eth_balance(wallet)
    eth_txs = get_eth_txs(wallet)
    eth_score = ai_risk_score(eth_balance, len(eth_txs))

    bsc_balance = get_bsc_balance(wallet)
    bsc_score = ai_risk_score(bsc_balance, 0)

    return render_template('index.html', wallet=wallet,
                           eth_balance=eth_balance,
                           eth_score=eth_score,
                           eth_txs=eth_txs,
                           bsc_balance=bsc_balance,
                           bsc_score=bsc_score)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
