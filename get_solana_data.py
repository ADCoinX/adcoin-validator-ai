import requests
from datetime import datetime

def get_solana_data(address):
    result = {
        "balance": 0,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

    try:
        # Gunakan Helius public API
        tx_url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key=helius&limit=5"
        bal_url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key=helius"

        tx_res = requests.get(tx_url, timeout=10).json()
        bal_res = requests.get(bal_url, timeout=10).json()

        result["balance"] = float(bal_res.get("SOL", {}).get("amount", 0)) / 1_000_000_000
        result["tx_count"] = len(tx_res)
        result["last5tx"] = []

        for tx in tx_res[:5]:
            tx_data = {
                "hash": tx.get("signature", ""),
                "time": tx.get("timestamp", ""),
                "from": tx.get("source", "N/A"),
                "to": tx.get("destination", "N/A"),
                "value": f'{tx.get("amount", 0)} SOL'
            }
            result["last5tx"].append(tx_data)

        if tx_res:
            first_time = tx_res[-1].get("timestamp", "")
            if first_time:
                dt_obj = datetime.strptime(first_time, "%Y-%m-%dT%H:%M:%SZ")
                result["wallet_age"] = (datetime.utcnow() - dt_obj).days

        return result

    except Exception:
        return result
