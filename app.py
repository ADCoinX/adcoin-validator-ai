
from flask import Flask, request, render_template, redirect, url_for
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "ADCoin Validator is Live"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
LOG_FILE = 'validation_log.json'

BLACKLISTED = {
    "0x000000000000000000000000000000000000dead",
    "0x1111111111111111111111111111111111111111"
}

def log_validation(entry):
    log_data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                log_data = json.load(f)
            except:
                log_data = []
    log_data.append(entry)
    with open(LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        tx_hash = request.form.get('txhash')
        result = {
            "input": tx_hash,
            "blacklisted": tx_hash.lower() in BLACKLISTED,
            "timestamp": datetime.utcnow().isoformat()
        }

        if tx_hash.startswith("0x") and len(tx_hash) == 66:
            url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={ETHERSCAN_API_KEY}"
            response = requests.get(url)
            try:
                tx_data = response.json()
                result.update({"etherscan": tx_data})
                if tx_data.get("result"):
                    to_address = tx_data["result"].get("to")
                    contract_check = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={to_address}&apikey={ETHERSCAN_API_KEY}"
                    contract_response = requests.get(contract_check)
                    contract_data = contract_response.json()
                    result["smart_contract"] = contract_data
            except:
                result.update({"etherscan": "Invalid response"})

        log_validation(result)
    return render_template('index.html', result=result)

@app.route('/admin')
def admin():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                log_data = json.load(f)
            except:
                log_data = []
    else:
        log_data = []
    return render_template('admin.html', logs=log_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
