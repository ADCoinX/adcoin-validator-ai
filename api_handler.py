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

# ETH aggressive fallback
def fetch_eth(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    # 1. Etherscan V2
    try:
        bal_url = f"https://api.etherscan.io/v2/account/balance?address={address}&apiKey={ETHERSCAN_API_KEY}"
        tx_url = f"https://api.etherscan.io/v2/account/transactions?address={address}&apiKey={ETHERSCAN_API_KEY}"
        bal = safe_json(requests.get(bal_url, timeout=8))
        tx = safe_json(requests.get(tx_url, timeout=8))
        txs = tx.get("result", [])
        if bal.get("result", {}).get("balance") is not None:
            result["balance"] = float(bal["result"]["balance"]) / 1e18
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
            return result
    except Exception as e:
        print(f"ETH v2 error: {e}")

    # 2. Etherscan V1 (public)
    try:
        bal_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}"
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc"
        bal = safe_json(requests.get(bal_url, timeout=8))
        tx = safe_json(requests.get(tx_url, timeout=8))
        if bal.get("status") == "1" and bal.get("result"):
            result["balance"] = float(bal["result"]) / 1e18
        txs = tx.get("result", [])
        if tx.get("status") == "1" and isinstance(txs, list):
            result["tx_count"] = len(txs)
            if txs:
                result["wallet_age"] = max(1, int((time.time() - int(txs[-1].get('timeStamp', time.time()))) / 86400))
                result["last5tx"] = [{
                    "hash": t.get("hash", "-"),
                    "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timeStamp", 0)))),
                    "from": t.get("from", "-"),
                    "to": t.get("to", "-"),
                    "value": str(int(t.get("value", 0)) / 1e18) + " ETH"
                } for t in txs[:5]]
            return result
    except Exception as e:
        print(f"ETH V1 error: {e}")

    # 3. Blockchair (public, last fallback)
    try:
        url = f"https://api.blockchair.com/ethereum/dashboards/address/{address}"
        r = safe_json(requests.get(url, timeout=8))
        data = r.get("data", {}).get(address.lower(), {})
        if data:
            result["balance"] = float(data.get("address", {}).get("balance", 0)) / 1e18
            txs = data.get("transactions", [])
            result["tx_count"] = len(txs)
            result["last5tx"] = [{
                "hash": t,
                "time": "-",
                "from": "-",
                "to": "-",
                "value": "-"
            } for t in txs[:5]]
        return result
    except Exception as e:
        print(f"ETH Blockchair error: {e}")

    return result

# BASE aggressive fallback
def fetch_base(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        bal_url = f"https://api.basescan.org/api?module=account&action=balance&address={address}&apikey={BASESCAN_API_KEY}"
        tx_url = f"https://api.basescan.org/api?module=account&action=txlist&address={address}&sort=desc&apikey={BASESCAN_API_KEY}"
        bal = safe_json(requests.get(bal_url, timeout=6))
        tx = safe_json(requests.get(tx_url, timeout=8))
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
            return result
    except Exception as e:
        print(f"BASEscan error: {e}")

    try:
        url = f"https://base.blockscout.com/api?module=account&action=balance&address={address}"
        bal = safe_json(requests.get(url, timeout=8))
        if bal.get("result"):
            result["balance"] = float(bal.get("result")) / 1e18
        url2 = f"https://base.blockscout.com/api?module=account&action=txlist&address={address}&sort=desc"
        tx = safe_json(requests.get(url2, timeout=8))
        txs = tx.get("result", [])
        if txs:
            result["tx_count"] = len(txs)
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timeStamp", 0)))),
                "from": t.get("from", "-"),
                "to": t.get("to", "-"),
                "value": str(int(t.get("value", 0)) / 1e18) + " ETH"
            } for t in txs[:5]]
        return result
    except Exception as e:
        print(f"BASE Blockscout error: {e}")

    return result

# TRON aggressive fallback
def fetch_tron(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY}
        bal_url = f"https://api.trongrid.io/v1/accounts/{address}"
        tx_url = f"https://api.trongrid.io/v1/accounts/{address}/transactions?limit=5&order_by=block_timestamp,desc"
        bal = safe_json(requests.get(bal_url, headers=headers, timeout=6))
        tx = safe_json(requests.get(tx_url, headers=headers, timeout=8))
        result["balance"] = float(bal.get('data', [{}])[0].get('balance', 0)) / 1e6
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
            return result
    except Exception as e:
        print(f"TRON Trongrid error: {e}")

    try:
        url = f"https://apilist.tronscanapi.com/api/account?address={address}"
        bal = safe_json(requests.get(url, timeout=8))
        result["balance"] = float(bal.get('balance', 0)) / 1e6
        tx_url = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=5&address={address}"
        tx = safe_json(requests.get(tx_url, timeout=8))
        txs = tx.get("data", [])
        result["tx_count"] = len(txs)
        if txs:
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(t.get("timestamp", 0) / 1000))),
                "from": t.get("ownerAddress", "-"),
                "to": t.get("toAddress", "-"),
                "value": "-"
            } for t in txs[:5]]
        return result
    except Exception as e:
        print(f"TRON Tronscan error: {e}")

    return result

# BTC aggressive fallback
def fetch_btc(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
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
        return result
    except Exception as e:
        print(f"BTC blockstream error: {e}")

    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}"
        r = safe_json(requests.get(url, timeout=8))
        result["balance"] = float(r.get("balance", 0)) / 1e8
        txs = r.get("txrefs", []) if "txrefs" in r else []
        result["tx_count"] = len(txs)
        result["last5tx"] = [{
            "hash": t.get("tx_hash", "-"),
            "time": "-",
            "from": "-",
            "to": "-",
            "value": "-"
        } for t in txs[:5]]
        return result
    except Exception as e:
        print(f"BTC blockcypher error: {e}")

    return result

# XRP aggressive fallback
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
        return result
    except Exception as e:
        print(f"XRP error: {e}")

    try:
        url = f"https://xrpscan.com/api/v1/account/{address}/transactions?limit=5"
        tx = safe_json(requests.get(url, timeout=8))
        if isinstance(tx, list):
            result["tx_count"] = len(tx)
            result["last5tx"] = [{
                "hash": t.get("hash", "-"),
                "time": t.get("date", "-"),
                "from": t.get("sender", "-"),
                "to": t.get("recipient", "-"),
                "value": str(t.get("amount", "0")) + " XRP"
            } for t in tx]
        return result
    except Exception as e:
        print(f"XRP fallback error: {e}")

    return result

# SOLANA aggressive fallback
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
        return result
    except Exception as e:
        print(f"SOL error: {e}")

    try:
        # public Solscan
        url = f"https://public-api.solscan.io/account/{address}"
        bal = safe_json(requests.get(url, timeout=8))
        result["balance"] = float(bal.get('lamports', 0)) / 1e9
        # Solscan tx not open API, so skip tx here (minimum is balance shown)
        return result
    except Exception as e:
        print(f"SOL fallback error: {e}")

    return result

# HEDERA aggressive fallback
def fetch_hedera(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        r = safe_json(requests.get(url, timeout=8))
        account_data = r.get("account", {})
        balance = account_data.get("balance", {}).get("balance", 0)
        result["balance"] = float(balance) / 1e8
        # Add transaction fetch if needed
    except Exception as e:
        print(f"Hedera error: {e}")

    # fallback: no open public fallback for HBAR, just return above
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
    }
    try:
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
        elif len(address) >= 32
