import requests
from datetime import datetime

def get_hedera_data(address):
    result = {
        "balance": 0,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

    try:
        # Hedera mirror node explorer API (via Kabuto)
        acc_url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        tx_url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/transactions?account.id={address}&limit=5&order=desc"

        acc_res = requests.get(acc_url, timeout=10).json()
        tx_res = requests.get(tx_url, timeout=10).json()

        result["balance"] = int(acc_res.get("balance", {}).get("balance", 0)) / 100_000_000

        result["tx_count"] = tx_res.get("links", {}).get("next", 0)
        result["last5tx"] = []

        for tx in tx_res.get("transactions", []):
            tx_data = {
                "hash": tx.get("transaction_hash", "")[:64],
                "time": tx.get("consensus_timestamp", ""),
                "from": tx.get("transaction_id", "").split("-")[0],
                "to": tx.get("transfers", [{}])[-1].get("account", "N/A"),
                "value": str(int(tx.get("transfers", [{}])[-1].get("amount", 0)) / 100_000_000) + " HBAR"
            }
            result["last5tx"].append(tx_data)

        # Wallet age
        if tx_res.get("transactions"):
            ts = tx_res["transactions"][-1].get("consensus_timestamp")
            if ts:
                dt_obj = datetime.utcfromtimestamp(float(ts))
                result["wallet_age"] = (datetime.utcnow() - dt_obj).days

        return result

    except Exception:
        return result
