from flask import Flask, render_template, request
import requests

app = Flask(__name__)

ETHERSCAN_API_KEY = "QZ2IEY7FFB5DVPMCYA5FCH2BQIYG4QSTHH"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

def is_suspicious_wallet(address):
    # Call Etherscan API to get token tx
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY
    }
    try:
        response = requests.get(ETHERSCAN_API_URL, params=params).json()
        txs = response.get("result", [])
        unique_tokens = set(tx["contractAddress"] for tx in txs)
        if len(unique_tokens) > 50:
            return True, len(unique_tokens)
        return False, len(unique_tokens)
    except Exception:
        return False, 0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    address = request.form['address']
    if not address.lower().startswith("0x") or len(address) != 42:
        return render_template('index.html', result="❌ Invalid address format")

    suspicious, token_count = is_suspicious_wallet(address)
    if suspicious:
        result = f"⚠️ Suspicious wallet detected! ({token_count} tokens found)"
    else:
        result = f"✅ Wallet is clean. ({token_count} tokens found)"
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run()