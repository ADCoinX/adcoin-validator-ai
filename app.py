from flask import Flask, render_template, request
import requests
import re

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

def get_balance_tron(wallet):
    url = f"https://apilist.tronscan.org/api/account?address={wallet}"
    try:
        res = requests.get(url).json()
        balance = res.get("balance", 0) / 1e6
        return f"{balance:.2f} TRX"
    except:
        return "N/A"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/validate", methods=["POST"])
def validate():
    wallet = request.form.get("wallet")
    network = detect_network(wallet)

    if network == "Ethereum":
        balance = get_balance_eth(wallet)
    elif network == "TRON":
        balance = get_balance_tron(wallet)
    else:
        balance = "N/A"

    # Dummy safety score
    score = "Low Risk ✅" if balance != "N/A" else "Unknown ⚠️"

    return render_template("index.html", wallet=wallet, network=network, balance=balance, score=score)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
