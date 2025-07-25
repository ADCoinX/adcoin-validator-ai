from flask import Flask, render_template, request
import requests
import re
from datetime import datetime

app = Flask(__name__)

def detect_network(wallet):
    if wallet.startswith("0x") and len(wallet) == 42:
        return "Ethereum"
    elif wallet.startswith("T") and len(wallet) == 34:
        return "TRON"
    elif wallet.startswith("1") or wallet.startswith("3") or wallet.startswith("bc1"):
        return "Bitcoin"
    elif wallet.startswith("bnb") and len(wallet) > 30:
        return "BSC"
    elif wallet.startswith("r") and len(wallet) > 20:
        return "XRP"
    elif len(wallet) == 44 and re.match(r"^[1-9A-HJ-NP-Za-km-z]+$", wallet):
        return "Solana"
    else:
        return "Unknown"

def get_balance_eth(wallet):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={wallet}&tag=latest&apikey=JTY578RMBIUHX448ICPB9JD5UERHWKA2PE"
    try:
        res = requests.get(url).json()
        balance = int(res['result']) / 1e18
        return f"{balance:.5f} ETH"
    except:
        return "N/A"

def get_last5_tx_eth(wallet):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&sort=desc&apikey=JTY578RMBIUHX448ICPB9JD5UERHWKA2PE"
    try:
        res = requests.get(url).json()
        txs = res.get('result', [])[:5]
        result = []
        for tx in txs:
            value_eth = int(tx['value']) / 1e18
            result.append({
                "hash": tx["hash"],
                "time": datetime.fromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S'),
                "from": tx["from"],
                "to": tx["to"],
                "value": f"{value_eth:.5f} ETH"
            })
        return result
    except:
        return []

def get_balance_tron(wallet):
    url = f"https://apilist.tronscan.org/api/account?address={wallet}"
    try:
        res = requests.get(url).json()
        balance = res.get("balance", 0) / 1e6
        return f"{balance:.2f} TRX"
    except:
        return "N/A"

def get_last5_tx_tron(wallet):
    url = f"https://apilist.tronscan.org/api/transaction?sort=-timestamp&count=true&limit=5&start=0&address={wallet}"
    try:
        res = requests.get(url).json()
        txs = res.get('data', [])
        result = []
        for tx in txs:
            value = tx.get('amount', 0) / 1e6 if 'amount' in tx else 0
            result.append({
                "hash": tx["hash"],
                "time": datetime.fromtimestamp(tx["timestamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'),
                "from": tx["ownerAddress"] if "ownerAddress" in tx else "",
                "to": tx["toAddress"] if "toAddress" in tx else "",
                "value": f"{value:.2f} TRX"
            })
        return result
    except:
        return []

def get_unique_user_count():
    try:
        with open("user_log.txt", "r") as f:
            lines = f.readlines()
        unique_ips = set([line.split('|')[1].strip() for line in lines])
        return len(unique_ips)
    except:
        return 0

@app.route("/")
def home():
    user_count = get_unique_user_count()
    return render_template("index.html", user_count=user_count)

@app.route("/validate", methods=["POST"])
def validate():
    wallet = request.form.get("wallet")
    network = detect_network(wallet)

    # Log user IP & wallet
    user_ip = request.remote_addr
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("user_log.txt", "a") as f:
        f.write(f"{timestamp} | {user_ip} | {wallet}\n")
    user_count = get_unique_user_count()

    balance = "N/A"
    last5tx = []

    if network == "Ethereum":
        balance = get_balance_eth(wallet)
        last5tx = get_last5_tx_eth(wallet)
    elif network == "TRON":
        balance = get_balance_tron(wallet)
        last5tx = get_last5_tx_tron(wallet)

    score = "Low Risk ✅" if balance != "N/A" else "Unknown ⚠️"

    return render_template(
        "index.html",
        wallet=wallet,
        network=network,
        balance=balance,
        score=score,
        last5tx=last5tx,
        user_count=user_count
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
