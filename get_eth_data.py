import requests
from datetime import datetime

def get_eth_data(address):
    result = {
        "balance": 0,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

    try:
        # Primary API: Etherscan
        etherscan_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey=YourAPIKey"
        balance_res = requests.get(etherscan_url, timeout=10).json()
        if balance_res.get("status") == "1":
            result["balance"] = int(balance_res["result"]) / 1e18

        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey=YourAPIKey"
        tx_res = requests.get(tx_url, timeout=10).json()
        if tx_res.get("status") == "1":
            txs = tx_res["result"]
            result["tx_count"] = len(txs)
            result["last5tx"] = [{
                "hash": tx["hash"],
                "time": datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M'),
                "from": tx["from"],
                "to": tx["to"],
                "value": str(int(tx["value"]) / 1e18) + " ETH"
            } for tx in txs[:5]]

            if txs:
                first_tx_time = int(txs[-1]["timeStamp"])
                wallet_age_days = (datetime.utcnow() - datetime.utcfromtimestamp(first_tx_time)).days
                result["wallet_age"] = wallet_age_days

        return result

    except Exception:
        # Fallback: public explorer API (e.g., Blockchair or Covalent, if added later)
        return result
