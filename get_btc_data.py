import requests
from datetime import datetime

def get_btc_data(address):
    result = {
        "balance": 0,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}?limit=5"
        res = requests.get(url, timeout=10).json()

        result["balance"] = float(res.get("balance", 0)) / 1e8
        result["tx_count"] = res.get("n_tx", 0)

        txs = res.get("txrefs", [])[:5]
        result["last5tx"] = [{
            "hash": tx.get("tx_hash"),
            "time": datetime.utcfromtimestamp(tx.get("confirmed", 0)).strftime('%Y-%m-%d %H:%M') if "confirmed" in tx else "N/A",
            "from": "N/A",
            "to": address,
            "value": str(tx.get("value", 0) / 1e8) + " BTC"
        } for tx in txs]

        if txs:
            first_tx = txs[-1]
            if "confirmed" in first_tx:
                result["wallet_age"] = (datetime.utcnow() - datetime.utcfromtimestamp(first_tx["confirmed"])).days

        return result

    except Exception:
        return result
