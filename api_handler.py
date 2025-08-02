import requests, os, time
from ai_risk import calculate_risk_score

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY")
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY")
BASESCAN_API_KEY = os.environ.get("BASESCAN_API_KEY")

def safe_json(response):
    try:
        print("URL:", response.url)
        print("Status:", response.status_code)
        print("Resp:", response.text[:200])
        return response.json()
    except Exception as e:
        print("JSON Error:", str(e))
        return {}

def fetch_eth(address):
    result = {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    try:
        bal_url = f"https://api.etherscan.io/v2/account/balance?address={address}&apiKey={ETHERSCAN_API_KEY}"
        bal = safe_json(requests.get(bal_url, timeout=8))
        result["balance"] = float(bal.get("result", {}).get("balance", 0)) / 1e18

        tx_url = f"https://api.etherscan.io/v2/account/transactions?address={address}&apiKey={ETHERSCAN_API_KEY}"
        tx = safe_json(requests.get(tx_url, timeout=8))
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
    except Exception as e:
        print(f"ETH error: {e}")
    return result

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
    except Exception as e:
        print(f"BASE error: {e}")
    return result

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
    except Exception as e:
        print(f"TRON error: {e}")
    return result

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
    except Exception as e:
        print(f"BTC error: {e}")
    return result

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
    except Exception as e:
        print(f"XRP error: {e}")
    return result

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
    except Exception as e:
        print(f"SOL error: {e}")
    return result

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
        "last5tx": []
    }

    try:
        if address.startswith("0x") and len(address) == 42:
            print("=== ETH & BASE ===")
            eth_data = fetch_eth(address)
            print("ETH:", eth_data)
            base_data = fetch_base(address)
            print("BASE:", base_data)
            eth_valid = (eth_data["balance"] is not None and eth_data["tx_count"] is not None and (eth_data["balance"] > 0 or eth_data["tx_count"] > 0))
            base_valid = (base_data["balance"] is not None and base_data["tx_count"] is not None and (base_data["balance"] > 0 or base_data["tx_count"] > 0))
            if eth_valid and not base_valid:
                data.update(eth_data)
                data["network"] = "Ethereum"
            elif base_valid and not eth_valid:
                data.update(base_data)
                data["network"] = "BASE"
            elif eth_valid and base_valid:
                data.update(eth_data)
                data["network"] = "Ethereum"
                data["reason"] = "Wallet aktif di ETH & BASE (default: ETH)"
            else:
                data.update(eth_data)
                data["reason"] = "ETH & BASE kosong/tiada data atau API error"
        elif address.startswith("T"):
            print("=== TRON ===")
            tron_data = fetch_tron(address)
            print("TRON:", tron_data)
            data["network"] = "TRON"
            data.update(tron_data)
        elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            print("=== BTC ===")
            btc_data = fetch_btc(address)
            print("BTC:", btc_data)
            data["network"] = "Bitcoin"
            data.update(btc_data)
        elif address.startswith("r"):
            print("=== XRP ===")
            xrp_data = fetch_xrp(address)
            print("XRP:", xrp_data)
            data["network"] = "XRP"
            data.update(xrp_data)
        elif len(address) >= 32:
            print("=== SOLANA ===")
            sol_data = fetch_solana(address)
            print("SOL:", sol_data)
            data["network"] = "Solana"
            data.update(sol_data)
        elif address.startswith("0.0."):
            print("=== HEDERA ===")
            hedera_data = fetch_hedera(address)
            print("HEDERA:", hedera_data)
            data["network"] = "Hedera"
            data.update(hedera_data)
        else:
            data["reason"] = "| Unsupported address type"
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

    print("FINAL RETURN:", data)
    return data
