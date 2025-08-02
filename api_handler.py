import requests, os, time
from ai_risk import calculate_risk_score

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY")
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY")
BASESCAN_API_KEY = os.environ.get("BASESCAN_API_KEY")

def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {}

# ETH
def fetch_eth(address):
    result = {"balance": None, "tx_count": None, "wallet_age": None, "last5tx": [], "error": "", "explorer": f"https://etherscan.io/address/{address}"}
    try:
        bal_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"
        bal = safe_json(requests.get(bal_url, timeout=8))
        if bal.get("status") == "1":
            result["balance"] = float(bal["result"]) / 1e18
        else:
            result["error"] = "ETH API error."
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
        tx = safe_json(requests.get(tx_url, timeout=8))
        txs = tx.get("result", [])
        if tx.get("status") == "1" and isinstance(txs, list) and len(txs) > 0:
            result["tx_count"] = len(txs)
            result["wallet_age"] = max(1, int((time.time() - int(txs[-1].get('timeStamp', time.time()))) / 86400))
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timeStamp", 0)))),
                "from": t.get("from", "-"),
                "to": t.get("to", "-"),
                "value": str(int(t.get("value", 0)) / 1e18) + " ETH"
            } for t in txs[:5]]
        else:
            result["error"] += " | ETH TX API fail."
    except Exception as e:
        result["error"] = f"ETH API BLOCKED: {e}"
    return result

# BASE
def fetch_base(address):
    result = {"balance": None, "tx_count": None, "wallet_age": None, "last5tx": [], "error": "", "explorer": f"https://basescan.org/address/{address}"}
    try:
        bal_url = f"https://api.basescan.org/api?module=account&action=balance&address={address}&apikey={BASESCAN_API_KEY}"
        tx_url = f"https://api.basescan.org/api?module=account&action=txlist&address={address}&sort=desc&apikey={BASESCAN_API_KEY}"
        bal = safe_json(requests.get(bal_url, timeout=6))
        tx = safe_json(requests.get(tx_url, timeout=8))
        if bal.get("status") == "1":
            result["balance"] = float(bal["result"]) / 1e18
        else:
            result["error"] = "BASE API error."
        txs = tx.get("result", [])
        if tx.get("status") == "1" and isinstance(txs, list) and len(txs) > 0:
            result["tx_count"] = len(txs)
            result["wallet_age"] = max(1, int((time.time() - int(txs[-1].get('timeStamp', time.time()))) / 86400))
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timeStamp", 0)))),
                "from": t.get("from", "-"),
                "to": t.get("to", "-"),
                "value": str(int(t.get("value", 0)) / 1e18) + " ETH"
            } for t in txs[:5]]
        else:
            result["error"] += " | BASE TX API fail."
    except Exception as e:
        result["error"] = f"BASE API BLOCKED: {e}"
    return result

# TRON
def fetch_tron(address):
    result = {"balance": None, "tx_count": None, "wallet_age": None, "last5tx": [], "error": "", "explorer": f"https://tronscan.io/#/address/{address}"}
    try:
        headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY}
        bal_url = f"https://api.trongrid.io/v1/accounts/{address}"
        tx_url = f"https://api.trongrid.io/v1/accounts/{address}/transactions?limit=5&order_by=block_timestamp,desc"
        bal = safe_json(requests.get(bal_url, headers=headers, timeout=6))
        tx = safe_json(requests.get(tx_url, headers=headers, timeout=8))
        if bal.get('data') and len(bal['data']) > 0:
            result["balance"] = float(bal['data'][0].get('balance', 0)) / 1e6
        else:
            result["error"] = "TRON API error."
        txs = tx.get("data", [])
        if txs:
            result["tx_count"] = len(txs)
            result["last5tx"] = [{
                "hash": t.get("txID", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("block_timestamp", 0) / 1000))),
                "from": t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address", "-"),
                "to": t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address", "-"),
                "value": "-"
            } for t in txs[:5]]
        else:
            result["error"] += " | TRON TX API fail."
    except Exception as e:
        result["error"] = f"TRON API BLOCKED: {e}"
    return result

# BTC
def fetch_btc(address):
    result = {"balance": None, "tx_count": None, "wallet_age": None, "last5tx": [], "error": "", "explorer": f"https://blockstream.info/address/{address}"}
    try:
        url = f"https://blockstream.info/api/address/{address}"
        tx_url = f"https://blockstream.info/api/address/{address}/txs"
        r = safe_json(requests.get(url, timeout=6))
        txs = safe_json(requests.get(tx_url, timeout=8))
        funded = r.get("chain_stats", {}).get("funded_txo_sum", 0)
        spent = r.get("chain_stats", {}).get("spent_txo_sum", 0)
        result["balance"] = (funded - spent) / 1e8
        result["tx_count"] = r.get("chain_stats", {}).get("tx_count", 0)
        result["last5tx"] = [{
            "hash": tx.get("txid", "-"),
            "time": "-",
            "from": "-",
            "to": "-",
            "value": "-"
        } for tx in txs[:5]] if isinstance(txs, list) else []
        if result["balance"] is None:
            result["error"] = "BTC API fail."
    except Exception as e:
        result["error"] = f"BTC API BLOCKED: {e}"
    return result

# XRP
def fetch_xrp(address):
    result = {"balance": None, "tx_count": None, "wallet_age": None, "last5tx": [], "error": "", "explorer": f"https://xrpscan.com/account/{address}"}
    try:
        bal_url = f"https://data.ripple.com/v2/accounts/{address}"
        tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?type=Payment&limit=5"
        bal = safe_json(requests.get(bal_url, timeout=6))
        tx = safe_json(requests.get(tx_url, timeout=8))
        if bal.get("account_data", {}).get("Balance"):
            result["balance"] = float(bal["account_data"]["Balance"]) / 1e6
        else:
            result["error"] = "XRP API error."
        if isinstance(tx, list) and len(tx) > 0:
            result["tx_count"] = len(tx)
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": t.get("date", "-"),
                "from": t.get("sender", "-"),
                "to": t.get("recipient", "-"),
                "value": str(t.get("amount", "0")) + " XRP"
            } for t in tx]
        else:
            result["error"] += " | XRP TX API fail."
    except Exception as e:
        result["error"] = f"XRP API BLOCKED: {e}"
    return result

# SOL
def fetch_solana(address):
    result = {"balance": None, "tx_count": None, "wallet_age": None, "last5tx": [], "error": "", "explorer": f"https://solscan.io/account/{address}"}
    try:
        headers = {"Authorization": f"Bearer {HELIUS_API_KEY}"}
        bal_url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key={HELIUS_API_KEY}"
        tx_url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?limit=5&api-key={HELIUS_API_KEY}"
        bal = safe_json(requests.get(bal_url, headers=headers, timeout=6))
        tx = safe_json(requests.get(tx_url, headers=headers, timeout=8))
        result["balance"] = float(bal.get('nativeBalance', {}).get('lamports', 0)) / 1e9
        if isinstance(tx, list) and len(tx) > 0:
            for t in tx[:5]:
                if t.get("nativeTransfers"):
                    n = t["nativeTransfers"][0]
                    result["last5tx"].append({
                        "hash": t.get("signature", "-"),
                        "time": str(t.get("timestamp", "-")),
                        "from": n.get("fromUserAccount", "-"),
                        "to": n.get("toUserAccount", "-"),
                        "value": str(n.get("amount", 0) / 1e9) + " SOL"
                    })
            result["tx_count"] = len(tx)
        else:
            result["error"] = "SOL TX API fail."
    except Exception as e:
        result["error"] = f"SOL API BLOCKED: {e}"
    return result

# HEDERA
def fetch_hedera(address):
    result = {"balance": None, "tx_count": None, "wallet_age": None, "last5tx": [], "error": "", "explorer": f"https://hashscan.io/mainnet/account/{address}"}
    try:
        url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        r = safe_json(requests.get(url, timeout=8))
        account_data = r.get("account", {})
        balance = account_data.get("balance", {}).get("balance", 0)
        result["balance"] = float(balance) / 1e8
        # Optional: fetch transactions (/transactions?account.id=0.0.xxxx)
    except Exception as e:
        result["error"] = f"HEDERA API BLOCKED: {e}"
    return result

# MAIN ENTRY
def get_wallet_data(address):
    data = {
        "address": address,
        "network": "Unknown",
        "balance": None,
        "ai_score": 0,
        "reason": "",
        "wallet_age": None,
        "tx_count": None,
        "last5tx": [],
        "error": "",
        "explorer": ""
    }

    try:
        if address.startswith("0x") and len(address) == 42:
            eth_data = fetch_eth(address)
            data.update(eth_data)
            data["network"] = "Ethereum"
        elif address.startswith("T"):
            data.update(fetch_tron(address))
            data["network"] = "TRON"
        elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            data.update(fetch_btc(address))
            data["network"] = "Bitcoin"
        elif address.startswith("r"):
            data.update(fetch_xrp(address))
            data["network"] = "XRP"
        elif len(address) >= 32:
            data.update(fetch_solana(address))
            data["network"] = "Solana"
        elif address.startswith("0.0."):
            data.update(fetch_hedera(address))
            data["network"] = "Hedera"
        else:
            data["reason"] = "Unsupported address type"
    except Exception as e:
        data["error"] = f"Critical system error: {str(e)}"

    try:
        data["ai_score"], ai_reason = calculate_risk_score(data)
        if ai_reason:
            data["reason"] += " | " + ai_reason
    except Exception as e:
        data["reason"] += f" | AI Error: {str(e)}"

    # Explorer fallback if error
    if data.get("error"):
        data["reason"] += f" | {data['error']} - <a href='{data['explorer']}' target='_blank'>View on Explorer</a>"

    # Guarantee field
    for k in ["last5tx", "balance", "tx_count", "wallet_age"]:
        if k not in data or data[k] is None:
            data[k] = "N/A"

    return data
