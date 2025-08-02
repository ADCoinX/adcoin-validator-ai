import requests
from datetime import datetime
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml

ETHERSCAN_API_KEY = "AW748ZEW1BC72P2WY8REWHP1OHJV3HKR35C"
TRONGRID_API_KEY = "510c999b-d0d7-4342-b0a8-d610cab9ae4d"
BLOCKCYPHER_API_KEY = "b58628B2045040A9b4872A13DA62A34B"
HELIUS_API_KEY = "90048cfc-009e-4e79-a4ae-3070d2fc5a5c"

def get_wallet_data(address):
    try:
        if address.startswith("0x") and len(address) == 42:
            return fetch_eth_data(address)
        elif address.startswith("T") and len(address) == 34:
            return fetch_tron_data(address)
        elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            return fetch_btc_data(address)
        elif address.startswith("r") and len(address) >= 25:
            return fetch_xrp_data(address)
        elif len(address) == 44:
            return fetch_sol_data(address)
        elif "-" in address and len(address) >= 42:
            return fetch_hbar_data(address)
        elif address.lower().startswith("0x") and "base" in address.lower():
            return fetch_base_data(address)
        else:
            return default_result(address, "Unknown", "❌ Invalid wallet format")
    except Exception as e:
        return default_result(address, "Unknown", f"❌ Error: {str(e)}")

def default_result(address, network, reason):
    return {
        "address": address,
        "network": network,
        "balance": 0,
        "ai_score": 0,
        "reason": reason,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

# =============== ETH (Etherscan + fallback Ethplorer) ===============
def fetch_eth_data(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={ETHERSCAN_API_KEY}"

        balance_response = requests.get(url, timeout=10).json()
        tx_response = requests.get(tx_url, timeout=10).json()
        balance = int(balance_response.get("result", 0)) / 1e18
        txs = tx_response.get("result", [])[:5]
        tx_list = [{
            "hash": tx["hash"],
            "time": datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M'),
            "from": tx["from"],
            "to": tx["to"],
            "value": str(int(tx["value"]) / 1e18)
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Ethereum",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[ETHERSCAN FAIL] {e}")

    # Fallback Ethplorer
    try:
        url = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey"
        r = requests.get(url, timeout=10).json()
        balance = r.get("ETH", {}).get("balance", 0)
        txs = r.get("operations", [])[:5]
        tx_list = [{
            "hash": tx.get("transactionHash", ""),
            "time": datetime.utcfromtimestamp(tx.get("timestamp", 0)).strftime('%Y-%m-%d %H:%M'),
            "from": tx.get("from", ""),
            "to": tx.get("to", ""),
            "value": str(tx.get("value", 0))
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Ethereum",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[Ethplorer FAIL] {e}")
        return default_result(address, "Ethereum", "❌ API rejected")

# =============== TRON (TronGrid + fallback Tronscan) ===============
def fetch_tron_data(address):
    try:
        url = f"https://api.trongrid.io/v1/accounts/{address}?include=transactions"
        response = requests.get(url, headers={"TRON-PRO-API-KEY": TRONGRID_API_KEY}).json()
        balance = int(response["data"][0].get("balance", 0)) / 1e6
        txs = response["data"][0].get("transactions", {}).get("data", [])[:5]
        tx_list = [{
            "hash": tx.get("txID", ""),
            "time": datetime.utcfromtimestamp(tx.get("block_timestamp", 0) / 1000).strftime('%Y-%m-%d %H:%M'),
            "from": tx.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address", ""),
            "to": tx.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address", ""),
            "value": str(tx.get("ret", [{}])[0].get("amount", 0) / 1e6)
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "TRON",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[TronGrid FAIL] {e}")

    # Fallback: Tronscan transactions (last 5)
    try:
        url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&sort=-timestamp&limit=5"
        resp = requests.get(url).json()
        txs = resp.get("data", [])
        balance_url = f"https://apilist.tronscanapi.com/api/account?address={address}"
        balance_resp = requests.get(balance_url).json()
        balance = int(balance_resp.get("balance", 0)) / 1e6
        tx_list = [{
            "hash": tx.get("hash", ""),
            "time": datetime.utcfromtimestamp(tx.get("timestamp", 0) / 1000).strftime('%Y-%m-%d %H:%M'),
            "from": tx.get("ownerAddress", ""),
            "to": tx.get("toAddress", ""),
            "value": str(tx.get("amount", 0) / 1e6)
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "TRON",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[Tronscan FAIL] {e}")
        return default_result(address, "TRON", "❌ API rejected")

# =============== BTC (Blockcypher) ===============
def fetch_btc_data(address):
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"
        response = requests.get(url).json()
        balance = int(response.get("final_balance", 0)) / 1e8
        txs = response.get("txs", [])[:5]
        tx_list = []
        for tx in txs:
            from_addr = tx.get("inputs", [{}])[0].get("addresses", [""])[0]
            to_addr = tx.get("outputs", [{}])[0].get("addresses", [""])[0]
            value = tx.get("total", 0) / 1e8
            tx_list.append({
                "hash": tx.get("hash", ""),
                "time": tx.get("confirmed", "")[:16],
                "from": from_addr,
                "to": to_addr,
                "value": str(value)
            })
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Bitcoin",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[Blockcypher FAIL] {e}")
        return default_result(address, "Bitcoin", "❌ API rejected")

# =============== XRP (xrpscan, fallback rippledata) ===============
def fetch_xrp_data(address):
    try:
        url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions"
        response = requests.get(url).json()
        txs = response[:5] if isinstance(response, list) else []
        # Get balance
        bal_url = f"https://api.xrpscan.com/api/v1/account/{address}/balances"
        bal_resp = requests.get(bal_url).json()
        balance = float(bal_resp[0]["value"]) if bal_resp else 0
        tx_list = [{
            "hash": tx.get("hash", ""),
            "time": tx.get("date", "")[:16],
            "from": tx.get("Account", ""),
            "to": tx.get("Destination", ""),
            "value": str(tx.get("Amount", ""))
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "XRP",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[XRPSCAN FAIL] {e}")

    # Fallback: ripple.com
    try:
        url = f"https://data.ripple.com/v2/accounts/{address}/transactions?limit=5"
        resp = requests.get(url).json()
        txs = resp.get("transactions", [])
        bal_url = f"https://data.ripple.com/v2/accounts/{address}/balances"
        bal_resp = requests.get(bal_url).json()
        balance = float(bal_resp["balances"][0]["value"]) if "balances" in bal_resp else 0
        tx_list = [{
            "hash": tx.get("hash", ""),
            "time": tx.get("date", "")[:16],
            "from": tx.get("Account", ""),
            "to": tx.get("Destination", ""),
            "value": str(tx.get("Amount", ""))
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "XRP",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[Rippledata FAIL] {e}")
        return default_result(address, "XRP", "❌ API rejected")

# =============== SOL (Helius, fallback Solscan) ===============
def fetch_sol_data(address):
    try:
        url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_API_KEY}&limit=5"
        response = requests.get(url).json()
        txs = response if isinstance(response, list) else []
        bal_url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key={HELIUS_API_KEY}"
        bal_resp = requests.get(bal_url).json()
        balance = float(bal_resp.get("nativeBalance", {}).get("sol", 0))
        tx_list = [{
            "hash": tx.get("signature", ""),
            "time": datetime.utcfromtimestamp(tx.get("timestamp", 0)).strftime('%Y-%m-%d %H:%M') if tx.get("timestamp") else "",
            "from": tx.get("account", ""),
            "to": "",
            "value": ""
        } for tx in txs[:5]]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Solana",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[Helius FAIL] {e}")

    # Fallback: Solscan
    try:
        url = f"https://public-api.solscan.io/account/transactions?account={address}&limit=5"
        txs = requests.get(url).json()
        bal_url = f"https://public-api.solscan.io/account/{address}"
        bal_resp = requests.get(bal_url).json()
        balance = float(bal_resp.get("lamports", 0)) / 1e9
        tx_list = [{
            "hash": tx.get("signature", ""),
            "time": tx.get("blockTime", ""),
            "from": "",
            "to": "",
            "value": ""
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Solana",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[Solscan FAIL] {e}")
        return default_result(address, "Solana", "❌ API rejected")

# =============== HBAR (Mirrornode + fallback hashscan) ===============
def fetch_hbar_data(address):
    try:
        url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}/transactions?limit=5"
        resp = requests.get(url).json()
        txs = resp.get("transactions", [])
        bal_url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        bal_resp = requests.get(bal_url).json()
        balance = int(bal_resp.get("balance", {}).get("balance", 0)) / 1e8
        tx_list = [{
            "hash": tx.get("transaction_id", ""),
            "time": tx.get("consensus_timestamp", ""),
            "from": "",
            "to": "",
            "value": ""
        } for tx in txs[:5]]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "HBAR",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[HBAR MIRRORNODE FAIL] {e}")

    # Fallback: Hashscan
    try:
        url = f"https://hashscan.io/api/mainnet/account/{address}/transactions?limit=5"
        resp = requests.get(url).json()
        txs = resp.get("transactions", [])
        bal_url = f"https://hashscan.io/api/mainnet/account/{address}"
        bal_resp = requests.get(bal_url).json()
        balance = int(bal_resp.get("balance", 0)) / 1e8
        tx_list = [{
            "hash": tx.get("transactionId", ""),
            "time": tx.get("consensusTimestamp", ""),
            "from": "",
            "to": "",
            "value": ""
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(txs),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "HBAR",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }
    except Exception as e:
        print(f"[Hashscan FAIL] {e}")
        return default_result(address, "HBAR
