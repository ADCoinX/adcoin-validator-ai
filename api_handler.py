import requests, os, time
from ai_risk import calculate_risk_score
from blacklist import is_blacklisted

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY")
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY")  # For Solana

def get_wallet_data(address):
    data = {
        "address": address,
        "network": "Unknown",
        "balance": 0,
        "ai_score": 0,
        "reason": "",
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

    if is_blacklisted(address):
        data["reason"] = "🚫 Blacklisted Wallet"
        return data

    # Ethereum
    if address.startswith("0x") and len(address) == 42:
        data["network"] = "Ethereum"
        from_wallet = address.lower()
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={from_wallet}&apikey={ETHERSCAN_API_KEY}"
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={from_wallet}&sort=desc&apikey={ETHERSCAN_API_KEY}"

        try:
            bal = requests.get(url).json()
            data["balance"] = float(bal['result']) / 1e18

            tx = requests.get(tx_url).json()
            if tx["result"]:
                data["tx_count"] = len(tx["result"])
                data["wallet_age"] = max(1, int((time.time() - int(tx['result'][-1]['timeStamp'])) / 86400))
                data["last5tx"] = [{
                    "hash": t["hash"],
                    "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t["timeStamp"]))),
                    "from": t["from"],
                    "to": t["to"],
                    "value": str(int(t["value"]) / 1e18) + " ETH"
                } for t in tx["result"][:5]]
        except:
            data["reason"] = "Error fetching Ethereum data"

    # TRON
    elif address.startswith("T"):
        data["network"] = "TRON"
        url = f"https://api.trongrid.io/v1/accounts/{address}"
        tx_url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?limit=5&order_by=block_timestamp,desc"
        headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY}

        try:
            r = requests.get(url, headers=headers).json()
            data["balance"] = float(r['data'][0].get('balance', 0)) / 1e6

            tx = requests.get(tx_url, headers=headers).json()
            if tx['data']:
                data["tx_count"] = len(tx['data'])
                data["last5tx"] = [{
                    "hash": t["transaction_id"],
                    "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t["block_timestamp"] / 1000))),
                    "from": t.get("from", "-"),
                    "to": t.get("to", "-"),
                    "value": str(float(t.get("value", 0)) / 1e6) + " TRX"
                } for t in tx['data']]
        except:
            data["reason"] = "Error fetching TRON data"

    # Bitcoin
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        data["network"] = "Bitcoin"
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}?limit=5"
        try:
            r = requests.get(url).json()
            data["balance"] = r["balance"] / 1e8
            data["tx_count"] = r.get("n_tx", 0)

            if "txrefs" in r:
                data["last5tx"] = [{
                    "hash": tx["tx_hash"],
                    "time": "-",  # BlockCypher free API tak bagi timestamp txrefs
                    "from": "-",
                    "to": "-",
                    "value": str(tx["value"] / 1e8) + " BTC"
                } for tx in r["txrefs"][:5]]
        except:
            data["reason"] = "Error fetching Bitcoin data"

    # Solana
    elif len(address) >= 32:
        data["network"] = "Solana"
        headers = {"Authorization": f"Bearer {HELIUS_API_KEY}"}
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?limit=5&api-key={HELIUS_API_KEY}"
            r = requests.get(url, headers=headers).json()
            balance_url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key={HELIUS_API_KEY}"
            b = requests.get(balance_url, headers=headers).json()
            data["balance"] = float(b['nativeBalance']['lamports']) / 1e9

            if isinstance(r, list):
                data["tx_count"] = len(r)
                data["last5tx"] = [{
                    "hash": tx.get("signature", ""),
                    "time": tx.get("timestamp", "-"),
                    "from": tx.get("nativeTransfers", [{}])[0].get("fromUserAccount", "-"),
                    "to": tx.get("nativeTransfers", [{}])[0].get("toUserAccount", "-"),
                    "value": str(tx.get("nativeTransfers", [{}])[0].get("amount", 0) / 1e9) + " SOL"
                } for tx in r]
        except:
            data["reason"] = "Error fetching Solana data"

    # XRP
    elif address.startswith("r"):
        data["network"] = "XRP"
        try:
            url = f"https://api.xrpscan.com/api/v1/account/{address}/basic"
            r = requests.get(url).json()
            data["balance"] = float(r.get("balance", 0))

            tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?type=Payment&limit=5"
            tx = requests.get(tx_url).json()
            if isinstance(tx, list):
                data["tx_count"] = len(tx)
                data["last5tx"] = [{
                    "hash": t.get("hash", "-"),
                    "time": t.get("date", "-"),
                    "from": t.get("sender", "-"),
                    "to": t.get("recipient", "-"),
                    "value": t.get("amount", "-") + " XRP"
                } for t in tx]
        except:
            data["reason"] = "Error fetching XRP data"

    # AI Score
    data["ai_score"], data["reason"] = calculate_risk_score(data)
    return data
