import requests
from datetime import datetime

def get_xrp_data(address):
    result = {
        "balance": 0,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

    try:
        # XRPSCAN API
        tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?limit=5"
        bal_url = f"https://api.xrpscan.com/api/v1/account/{address}"

        bal_res = requests.get(bal_url, timeout=10).json()
        result["balance"] = float(bal_res.get("xrpBalance", 0))

        tx_res = requests.get(tx_url, timeout=10).json()
        txs = tx_res[:5]

        result["tx_count"] = len(tx_res)
        result["last5tx"] = []

        for tx in txs:
            tx_data = {
                "hash": tx.get("hash", "")[:64],
                "time": tx.get("timestamp", "N/A"),
                "from": tx.get("from", "N/A"),
                "to": tx.get("to", "N/A"),
                "value": f'{tx.get("amount", 0)} XRP'
            }
            result["last5tx"].append(tx_data)

        # Wallet age from first transaction
        if txs:
            first_time = txs[-1].get("timestamp", "")
            if first_time:
                dt_obj = datetime.strptime(first_time, "%Y-%m-%dT%H:%M:%SZ")
                result["wallet_age"] = (datetime.utcnow() - dt_obj).days

        return result

    except Exception:
        return result
