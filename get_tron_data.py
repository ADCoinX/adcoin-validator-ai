import requests
from datetime import datetime

def get_tron_data(address):
    result = {
        "balance": 0,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

    try:
        # Primary API: TRONSCAN
        url = f"https://apilist.tronscanapi.com/api/accountv2?address={address}"
        res = requests.get(url, timeout=10).json()

        # Balance
        balances = res.get("balances", [])
        for b in balances:
            if b.get("tokenName") == "TRX":
                result["balance"] = float(b.get("amount", 0))

        # Transactions
        tx_url = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=5&start=0&address={address}"
        tx_res = requests.get(tx_url, timeout=10).json()
        txs = tx_res.get("data", [])
        result["tx_count"] = tx_res.get("total", 0)

        result["last5tx"] = [{
            "hash": tx["hash"],
            "time": datetime.utcfromtimestamp(int(tx["timestamp"] / 1000)).strftime('%Y-%m-%d %H:%M'),
            "from": tx.get("ownerAddress", "N/A"),
            "to": tx.get("toAddress", "N/A"),
            "value": str(int(tx.get("amount", 0)) / 1e6) + " TRX"
        } for tx in txs[:5]]

        if txs:
            first_tx_time = txs[-1]["timestamp"] / 1000
            result["wallet_age"] = (datetime.utcnow() - datetime.utcfromtimestamp(first_tx_time)).days

        return result

    except Exception:
        return result
