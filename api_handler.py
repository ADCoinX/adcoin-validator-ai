import requests, os, time
from ai_risk import calculate_risk_score
from blacklist import is_blacklisted

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY")
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY")

def get_wallet_data(address):
    data = {
        "address": address,
        "network": "Unknown",
        "balance": 0,
        "ai_score": 0,
        "reason": "",
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": [],
        "blacklisted": False
    }

    if is_blacklisted(address):
        data["reason"] = "🚫 Blacklisted Wallet"
        data["blacklisted"] = True
        return data

    try:
        # === ETHEREUM ===
        if address.startswith("0x") and len(address) == 42:
            data["network"] = "Ethereum"
            bal_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"
            tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
            bal = requests.get(bal_url).json()
            tx = requests.get(tx_url).json()

            if bal.get("status") == "1":
                data["balance"] = float(bal.get("result", 0)) / 1e18
            else:
                data["reason"] += " | ETH balance failed"

            txs = tx.get("result", [])
            if tx.get("status") == "1" and txs:
                data["tx_count"] = len(txs)
                data["wallet_age"] = max(1, int((time.time() - int(txs[-1]['timeStamp'])) / 86400))
                data["last5tx"] = [{
                    "hash": t["hash"],
                    "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t["timeStamp"]))),
                    "from": t["from"],
                    "to": t["to"],
                    "value": str(int(t["value"]) / 1e18) + " ETH"
                } for t in txs[:5]]

        # === TRON ===
        elif address.startswith("T"):
            data["network"] = "TRON"
            headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY}
            bal_url = f"https://api.trongrid.io/v1/accounts/{address}"
            tx_url = f"https://api.trongrid.io/v1/accounts/{address}/transactions?limit=5&order_by=block_timestamp,desc"
            bal = requests.get(bal_url, headers=headers).json()
            tx = requests.get(tx_url, headers=headers).json()

            data["balance"] = float(bal.get('data', [{}])[0].get('balance', 0)) / 1e6
            txs = tx.get("data", [])
            data["tx_count"] = len(txs)
            data["last5tx"] = [{
                "hash": t.get("txID", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("block_timestamp", 0) / 1000))),
                "from": t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address", "-"),
                "to": t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address", "-"),
                "value": "-"
            } for t in txs]

        # === BITCOIN ===
        elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            data["network"] = "Bitcoin"
            url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}?limit=5"
            r = requests.get(url).json()
            data["balance"] = r.get("balance", 0) / 1e8
            data["tx_count"] = r.get("n_tx", 0)
            txs = r.get("txrefs", [])
            data["last5tx"] = [{
                "hash": tx.get("tx_hash", "-"),
                "time": "-",
                "from": "-",
                "to": "-",
                "value": str(tx.get("value", 0) / 1e8) + " BTC"
            } for tx in txs[:5]]

        # === SOLANA ===
        elif len(address) >= 32:
            data["network"] = "Solana"
            headers = {"Authorization": f"Bearer {HELIUS_API_KEY}"}
            bal_url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key={HELIUS_API_KEY}"
            tx_url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?limit=5&api-key={HELIUS_API_KEY}"
            bal = requests.get(bal_url, headers=headers).json()
            tx = requests.get(tx_url, headers=headers).json()

            data["balance"] = float(bal.get('nativeBalance', {}).get('lamports', 0)) / 1e9
            if isinstance(tx, list):
                data["tx_count"] = len(tx)
                for t in tx:
                    if t.get("nativeTransfers"):
                        n = t["nativeTransfers"][0]
                        data["last5tx"].append({
                            "hash": t.get("signature", "-"),
                            "time": t.get("timestamp", "-"),
                            "from": n.get("fromUserAccount", "-"),
                            "to": n.get("toUserAccount", "-"),
                            "value": str(n.get("amount", 0) / 1e9) + " SOL"
                        })

        # === XRP ===
        elif address.startswith("r"):
            data["network"] = "XRP"
            bal_url = f"https://data.ripple.com/v2/accounts/{address}"
            tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?type=Payment&limit=5"
            bal = requests.get(bal_url).json()
            tx = requests.get(tx_url).json()

            data["balance"] = float(bal.get("account_data", {}).get("Balance", 0)) / 1e6
            if isinstance(tx, list):
                data["tx_count"] = len(tx)
                data["last5tx"] = [{
                    "hash": t.get("hash", "-"),
                    "time": t.get("date", "-"),
                    "from": t.get("sender", "-"),
                    "to": t.get("recipient", "-"),
                    "value": str(t.get("amount", "0")) + " XRP"
                } for t in tx]

    except Exception as e:
        data["reason"] += f" | Error: {str(e)}"

    # === AI Risk Scoring ===
    data["ai_score"], ai_reason = calculate_risk_score(data)
    if ai_reason:
        data["reason"] += " | " + ai_reason

    return data
