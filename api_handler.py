import requests, os, time
from ai_risk import calculate_risk_score

ETHERSCAN_API_KEY  = os.environ.get("ETHERSCAN_API_KEY")
TRONGRID_API_KEY   = os.environ.get("TRONGRID_API_KEY")
HELIUS_API_KEY     = os.environ.get("HELIUS_API_KEY")
BASESCAN_API_KEY   = os.environ.get("BASESCAN_API_KEY")

def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {}

# =============== ETH (Etherscan V2, fallback Blockchair public) ===============
def fetch_eth(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        bal_url = f"https://api.etherscan.io/v2/account/balance?address={address}&apiKey={ETHERSCAN_API_KEY}"
        tx_url = f"https://api.etherscan.io/v2/account/transactions?address={address}&apiKey={ETHERSCAN_API_KEY}"
        bal    = safe_json(requests.get(bal_url, timeout=8))
        tx     = safe_json(requests.get(tx_url, timeout=8))
        if bal.get("result", {}).get("balance", None):
            result["balance"] = float(bal["result"]["balance"]) / 1e18
        txs = tx.get("result", [])
        result["tx_count"] = len(txs)
        if txs:
            result["wallet_age"] = max(1, int((time.time() - int(txs[-1].get('timestamp', time.time()))) / 86400))
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timestamp", 0)))),
                "from": t.get("from", "-"),
                "to": t.get("to", "-"),
                "value": str(int(t.get("value", 0)) / 1e18) + " ETH"
            } for t in txs[:5]]
        # Aggressive fallback Blockchair
        if (result["balance"] == 0 and result["tx_count"] == 0):
            print("Fallback to Blockchair for ETH!")
            url = f"https://api.blockchair.com/ethereum/dashboards/address/{address}"
            r = safe_json(requests.get(url, timeout=8))
            data = r.get("data", {}).get(address, {})
            result["balance"] = float(data.get("address", {}).get("balance", 0)) / 1e18
            txs = data.get("transactions", [])[:5]
            result["tx_count"] = len(txs)
            result["last5tx"] = [{"hash": h, "time": "-", "from": "-", "to": "-", "value": "-"} for h in txs]
    except Exception as e:
        print(f"ETH error: {e}")
    return result

# =============== BASE (BaseScan, fallback Blockscout) ===============
def fetch_base(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        bal_url = f"https://api.basescan.org/api?module=account&action=balance&address={address}&apikey={BASESCAN_API_KEY}"
        tx_url  = f"https://api.basescan.org/api?module=account&action=txlist&address={address}&sort=desc&apikey={BASESCAN_API_KEY}"
        bal = safe_json(requests.get(bal_url, timeout=6))
        tx  = safe_json(requests.get(tx_url, timeout=8))
        if bal.get("status") == "1" and bal.get("result"):
            result["balance"] = float(bal["result"]) / 1e18
        txs = tx.get("result", [])
        if tx.get("status") == "1" and isinstance(txs, list) and txs:
            result["tx_count"] = len(txs)
            result["wallet_age"] = max(1, int((time.time() - int(txs[-1].get('timeStamp', time.time()))) / 86400))
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timeStamp", 0)))),
                "from": t.get("from", "-"),
                "to": t.get("to", "-"),
                "value": str(int(t.get("value", 0)) / 1e18) + " ETH"
            } for t in txs[:5]]
        # Aggressive fallback: Blockscout
        if (result["balance"] == 0 and result["tx_count"] == 0):
            print("Fallback to Blockscout for BASE!")
            url = f"https://base.blockscout.com/api/v2/addresses/{address}"
            r = safe_json(requests.get(url, timeout=8))
            result["balance"] = float(r.get("eth_balance", 0)) / 1e18
            tx_url = f"https://base.blockscout.com/api/v2/addresses/{address}/transactions"
            txs = safe_json(requests.get(tx_url, timeout=8))
            if isinstance(txs, list):
                result["tx_count"] = len(txs)
                result["last5tx"] = [{"hash": t.get("hash", "-"), "time": "-", "from": t.get("from", "-"), "to": t.get("to", "-"), "value": "-"} for t in txs[:5]]
    except Exception as e:
        print(f"BASE error: {e}")
    return result

# =============== BTC (Blockstream, fallback Blockchair) ===============
def fetch_btc(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        url    = f"https://blockstream.info/api/address/{address}"
        tx_url = f"https://blockstream.info/api/address/{address}/txs"
        r  = safe_json(requests.get(url, timeout=6))
        txs = safe_json(requests.get(tx_url, timeout=8))
        funded = r.get("chain_stats", {}).get("funded_txo_sum", 0)
        spent  = r.get("chain_stats", {}).get("spent_txo_sum", 0)
        result["balance"] = (funded - spent) / 1e8
        result["tx_count"] = r.get("chain_stats", {}).get("tx_count", 0)
        result["last5tx"] = [{
            "hash": tx.get("txid", "-"),
            "time": "-",
            "from": "-",
            "to": "-",
            "value": "-"
        } for tx in txs[:5]] if isinstance(txs, list) else []
        # Aggressive fallback Blockchair
        if (result["balance"] == 0 and result["tx_count"] == 0):
            print("Fallback to Blockchair for BTC!")
            url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"
            r = safe_json(requests.get(url, timeout=8))
            data = r.get("data", {}).get(address, {})
            result["balance"] = float(data.get("address", {}).get("balance", 0)) / 1e8
            txs = data.get("transactions", [])[:5]
            result["tx_count"] = len(txs)
            result["last5tx"] = [{"hash": h, "time": "-", "from": "-", "to": "-", "value": "-"} for h in txs]
    except Exception as e:
        print(f"BTC error: {e}")
    return result

# =============== TRON (Trongrid, fallback Tronscan public) ===============
def fetch_tron(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY}
        bal_url = f"https://api.trongrid.io/v1/accounts/{address}"
        bal = safe_json(requests.get(bal_url, headers=headers, timeout=6))
        result["balance"] = float(bal.get('data', [{}])[0].get('balance', 0)) / 1e6
        tx_url = f"https://api.trongrid.io/v1/accounts/{address}/transactions?limit=5&order_by=block_timestamp,desc"
        tx = safe_json(requests.get(tx_url, headers=headers, timeout=8))
        txs = tx.get("data", [])
        result["tx_count"] = len(txs)
        if txs:
            result["last5tx"] = [{
                "hash": t.get("txID", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("block_timestamp", 0) / 1000))),
                "from": t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address", "-"),
                "to": t.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address", "-"),
                "value": "-"
            } for t in txs[:5]]
        # Aggressive fallback TRONSCAN public
        if (result["balance"] == 0 and result["tx_count"] == 0):
            print("Fallback to TRONSCAN public for TRON!")
            ts_url = f"https://apilist.tronscanapi.com/api/account?address={address}"
            ts_bal = safe_json(requests.get(ts_url, timeout=6))
            result["balance"] = float(ts_bal.get('balance', 0)) / 1e6
            result["tx_count"] = ts_bal.get('transactionCount', 0)
            ts_tx_url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit=5&sort=-timestamp"
            tx = safe_json(requests.get(ts_tx_url, timeout=8))
            txs = tx.get('data', [])
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timestamp", 0)) / 1000)),
                "from": t.get("ownerAddress", "-"),
                "to": t.get("toAddress", "-"),
                "value": str(t.get("amount", 0) / 1e6) + " TRX"
            } for t in txs[:5]]
    except Exception as e:
        print(f"TRON error: {e}")
    return result

# =============== XRP (XRPSCAN, fallback ripple data public) ===============
def fetch_xrp(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        bal_url = f"https://data.ripple.com/v2/accounts/{address}"
        tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?type=Payment&limit=5"
        bal = safe_json(requests.get(bal_url, timeout=6))
        tx = safe_json(requests.get(tx_url, timeout=8))
        result["balance"] = float(bal.get("account_data", {}).get("Balance", 0)) / 1e6
        if isinstance(tx, list):
            result["tx_count"] = len(tx)
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": t.get("date", "-"),
                "from": t.get("sender", "-"),
                "to": t.get("recipient", "-"),
                "value": str(t.get("amount", "0")) + " XRP"
            } for t in tx]
        # Aggressive fallback public
        if result["balance"] == 0:
            print("Fallback to xrpldata public for XRP!")
            bal_url = f"https://api.xrpldata.com/api/v1/accounts/{address}"
            bal = safe_json(requests.get(bal_url, timeout=6))
            result["balance"] = float(bal.get("account_data", {}).get("Balance", 0)) / 1e6
    except Exception as e:
        print(f"XRP error: {e}")
    return result

# =============== SOL (Helius, fallback Solscan public) ===============
def fetch_solana(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
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
        # Aggressive fallback solscan public
        if result["balance"] == 0:
            print("Fallback to solscan public for SOL!")
            url = f"https://public-api.solscan.io/account/tokens?account={address}"
            bal = safe_json(requests.get(url, timeout=6))
            if isinstance(bal, list) and bal:
                result["balance"] = float(bal[0].get("tokenAmount", {}).get("uiAmount", 0))
    except Exception as e:
        print(f"SOL error: {e}")
    return result

# =============== HEDERA (MirrorNode only, public) ===============
def fetch_hedera(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        r = safe_json(requests.get(url, timeout=8))
        account_data = r.get("account", {})
        balance = account_data.get("balance", {}).get("balance", 0)
        result["balance"] = float(balance) / 1e8
    except Exception as e:
        print(f"Hedera error: {e}")
    return result

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
    try:
        # --- chain detect ---
        if address.startswith("0x") and len(address) == 42:
            eth_data = fetch_eth(address)
            if eth_data["balance"] > 0 or eth_data["tx_count"] > 0:
                data.update(eth_data)
                data["network"] = "Ethereum"
            else:
                base_data = fetch_base(address)
                data.update(base_data)
                data["network"] = "BASE"
        elif address.startswith("T"):
            data["network"] = "TRON"
            data.update(fetch_tron(address))
        elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            data["network"] = "Bitcoin"
            data.update(fetch_btc(address))
        elif address.startswith("r"):
            data["network"] = "XRP"
            data.update(fetch_xrp(address))
        elif len(address) >= 32 and not address.startswith("0.0."):
            data["network"] = "Solana"
            data.update(fetch_solana(address))
        elif address.startswith("0.0."):
            data["network"] = "Hedera"
            data.update(fetch_hedera(address))
        else:
            data["reason"] = " | Unsupported address type"
    except Exception as e:
        data["reason"] += f" | Error: {str(e)}"
    try:
        data["ai_score"], ai_reason = calculate_risk_score(data)
        if ai_reason:
            data["reason"] += " | " + ai_reason
    except Exception as e:
        data["reason"] += f" | AI Error: {str(e)}"
    if "last5tx" not in data or not isinstance(data["last5tx"], list):
        data["last5tx"] = []
    if "balance" not in data or not isinstance(data["balance"], (int, float)):
        data["balance"] = 0
    if "tx_count" not in data or not isinstance(data["tx_count"], int):
        data["tx_count"] = 0
    return data
