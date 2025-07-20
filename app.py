from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# === [1] NETWORK DETECTION ===
def detect_network(wallet):
    if wallet.startswith("0x"):
        return "Ethereum"
    elif wallet.startswith("T"):
        return "TRON"
    elif wallet.startswith("1") or wallet.startswith("3") or wallet.startswith("bc1"):
        return "Bitcoin"
    elif wallet.startswith("bnb"):
        return "BSC"
    elif wallet.startswith("r"):
        return "XRP"
    elif len(wallet) == 44:
        return "Solana"
    return "Unknown"

# === [2] BALANCE CHECK ===
def get_balance(wallet, network):
    try:
        if network == "Ethereum":
            res = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={wallet}&tag=latest&apikey=YourApiKey").json()
            return str(int(res['result']) / 10**18) + " ETH"
        elif network == "TRON":
            res = requests.get(f"https://api.trongrid.io/v1/accounts/{wallet}").json()
            return str(res['data'][0].get('balance', 0) / 10**6) + " TRX"
        elif network == "Bitcoin":
            res = requests.get(f"https://blockchain.info/rawaddr/{wallet}").json()
            return str(res['final_balance'] / 10**8) + " BTC"
        elif network == "BSC":
            res = requests.get(f"https://api.bscscan.com/api?module=account&action=balance&address={wallet}&apikey=YourApiKey").json()
            return str(int(res['result']) / 10**18) + " BNB"
        elif network == "XRP":
            res = requests.get(f"https://api.xrpscan.com/api/v1/account/{wallet}").json()
            return str(res['account_data']['Balance']) + " XRP"
        elif network == "Solana":
            res = requests.get(f"https://public-api.solscan.io/account/{wallet}").json()
            return str(res.get('lamports', 0) / 10**9) + " SOL"
    except:
        return "Unavailable"
    return "Unavailable"

# === [3] AI SAFETY CHECK ===
def ai_safety_check(wallet, balance, network):
    try:
        if balance == "Unavailable" or network == "Unknown":
            return "Unknown Risk"
        value = float(balance.split(" ")[0])
        if value == 0:
            return "High Risk"
        elif value < 0.01:
            return "Medium Risk"
        elif value >= 0.01:
            return "Low Risk"
        if wallet.startswith("0x000") or wallet.endswith("0000"):
            return "High Risk"
    except:
        return "Unknown Risk"
    return "Low Risk"

# === [4] TRANSACTIONS FETCH ===
def get_transactions(wallet, network):
    try:
        if network == "Ethereum":
            url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&sort=desc&apikey=YourApiKey"
            res = requests.get(url).json()
            txs = res.get("result", [])[:10]
            return [{
                "hash": tx["hash"],
                "from": tx["from"],
                "to": tx["to"],
                "value": str(int(tx["value"]) / 10**18) + " ETH",
                "time": tx["timeStamp"]
            } for tx in txs]

        elif network == "Bitcoin":
            url = f"https://blockchain.info/rawaddr/{wallet}"
            res = requests.get(url).json()
            txs = res.get("txs", [])[:10]
            return [{
                "hash": tx["hash"],
                "value": str(sum([o["value"] for o in tx["out"]]) / 10**8) + " BTC"
            } for tx in txs]

        elif network == "TRON":
            url = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=10&start=0&address={wallet}"
            res = requests.get(url).json()
            txs = res.get("data", [])
            return [{
                "hash": tx["hash"],
                "type": tx.get("contractType", "TRX TX"),
                "amount": tx.get("amount", 0)
            } for tx in txs]

        # Can extend to BSC, XRP, SOL later
    except:
        return []

# === [5] MAIN ROUTE ===
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        wallet = request.form['wallet']
        network = detect_network(wallet)
        balance = get_balance(wallet, network)
        risk_score = ai_safety_check(wallet, balance, network)
        transactions = get_transactions(wallet, network)
        result = {
            'wallet': wallet,
            'network': network,
            'balance': balance,
            'risk': risk_score,
            'transactions': transactions
        }
    return render_template('index.html', result=result)

# === [6] RUN ===
if __name__ == "__main__":
    app.run(debug=True)
