from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def detect_chain(address):
    if address.startswith("0x") and len(address) == 42:
        return "ethereum"
    elif address.startswith("T") and len(address) == 34:
        return "tron"
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        return "bitcoin"
    elif address.startswith("bnb") and len(address) == 42:
        return "bsc"
    elif address.startswith("r") and len(address) >= 25:
        return "xrp"
    elif len(address) >= 32 and address[-1] != "=":
        return "solana"
    else:
        return "unknown"

@app.route("/", methods=["GET", "POST"])
def index():
    data = {}
    if request.method == "POST":
        address = request.form["wallet"]
        chain = detect_chain(address)
        data["address"] = address
        data["chain"] = chain.upper()
        data["balance"] = "Unknown"
        data["transactions"] = []
        data["risk_score"] = "Unknown"

        try:
            if chain == "tron":
                url = f"https://apilist.tronscanapi.com/api/account?address={address}"
                r = requests.get(url).json()
                data["balance"] = str(int(r.get("balance", 0)) / 1000000) + " TRX"
                tx_url = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=5&start=0&address={address}"
                tx_data = requests.get(tx_url).json()
                data["transactions"] = tx_data.get("data", [])
                data["risk_score"] = "Low" if int(r.get("balance", 0)) > 1_000_000 else "High"

            elif chain == "ethereum":
                eth_api = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey"
                r = requests.get(eth_api).json()
                data["balance"] = str(r.get("ETH", {}).get("balance", "0")) + " ETH"
                tx_url = f"https://api.ethplorer.io/getAddressTransactions/{address}?apiKey=freekey"
                tx_data = requests.get(tx_url).json()
                data["transactions"] = tx_data[:5]
                data["risk_score"] = "Low" if r.get("ETH", {}).get("balance", 0) > 1 else "High"

            elif chain == "bitcoin":
                btc_api = f"https://blockchain.info/rawaddr/{address}"
                r = requests.get(btc_api).json()
                data["balance"] = str(r.get("final_balance", 0) / 100000000) + " BTC"
                data["transactions"] = r.get("txs", [])[:5]
                data["risk_score"] = "Low" if r.get("n_tx", 0) > 3 else "High"

            elif chain == "bsc":
                bsc_api = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&apikey=YourApiKeyToken"
                res = requests.get(bsc_api).json()
                balance_wei = int(res.get("result", 0))
                data["balance"] = str(balance_wei / 1e18) + " BNB"
                data["transactions"] = []
                data["risk_score"] = "Medium"

            elif chain == "xrp":
                xrp_api = f"https://api.xrpscan.com/api/v1/account/{address}/transactions"
                tx_data = requests.get(xrp_api).json()
                balance_api = f"https://api.xrpscan.com/api/v1/account/{address}"
                bal_data = requests.get(balance_api).json()
                data["balance"] = str(bal_data.get("balance", 0)) + " XRP"
                data["transactions"] = tx_data[:5]
                data["risk_score"] = "Low" if float(data["balance"].split()[0]) > 50 else "High"

            elif chain == "solana":
                sol_api = f"https://api.mainnet-beta.solana.com"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [address]
                }
                r = requests.post(sol_api, json=payload, headers=headers).json()
                lamports = r.get("result", {}).get("value", 0)
                data["balance"] = str(lamports / 1e9) + " SOL"
                data["transactions"] = []
                data["risk_score"] = "Medium"

        except Exception as e:
            data["error"] = str(e)

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
