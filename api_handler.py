import requests
from datetime import datetime
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml

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

def fetch_eth_data(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey=AW748ZEW1BC72P2WY8REWHP1OHJV3HKR35C"
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey=AW748ZEW1BC72P2WY8REWHP1OHJV3HKR35C"
        balance_res = requests.get(url).json()
        tx_res = requests.get(tx_url).json()

        if balance_res.get("status") == "1" and tx_res.get("status") == "1":
            balance = int(balance_res["result"]) / 1e18
            txs = tx_res.get("result", [])[:5]
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
    except:
        pass
    return default_result(address, "Ethereum", "❌ API rejected")

def fetch_tron_data(address):
    try:
        url = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=5&start=0&address={address}"
        txs = requests.get(url).json().get("data", [])
        url2 = f"https://api.trongrid.io/v1/accounts/{address}"
        res = requests.get(url2).json()
        balance = int(res["data"][0].get("balance", 0)) / 1e6
        tx_list = [{
            "hash": tx["hash"],
            "time": datetime.utcfromtimestamp(int(tx["timestamp"] / 1000)).strftime('%Y-%m-%d %H:%M'),
            "from": tx["ownerAddress"],
            "to": tx["toAddress"],
            "value": str(tx["amount"] / 1e6)
        } for tx in txs if "amount" in tx]
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
    except:
        return default_result(address, "TRON", "❌ API rejected")

def fetch_btc_data(address):
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full?limit=5"
        res = requests.get(url).json()
        balance = int(res.get("final_balance", 0)) / 1e8
        txs = res.get("txs", [])[:5]
        tx_list = [{
            "hash": tx.get("hash", ""),
            "time": datetime.utcfromtimestamp(int(tx.get("received", "").split("T")[0].replace("-", ""))).strftime('%Y-%m-%d'),
            "from": tx.get("inputs", [{}])[0].get("addresses", [""])[0],
            "to": tx.get("outputs", [{}])[0].get("addresses", [""])[0],
            "value": str(tx.get("total", 0) / 1e8)
        } for tx in txs]
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
    except:
        return default_result(address, "Bitcoin", "❌ API rejected")

def fetch_xrp_data(address):
    try:
        url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?type=Payment&limit=5"
        res = requests.get(url).json()
        url2 = f"https://api.xrpscan.com/api/v1/account/{address}/balances"
        balance = float(requests.get(url2).json()[0]["value"])
        tx_list = [{
            "hash": tx.get("hash", ""),
            "time": tx.get("timestamp", ""),
            "from": tx.get("from", ""),
            "to": tx.get("to", ""),
            "value": tx.get("amount", "")
        } for tx in res]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(tx_list),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "XRP",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(tx_list),
            "last5tx": tx_list
        }
    except:
        return default_result(address, "XRP", "❌ API rejected")

def fetch_sol_data(address):
    try:
        url = f"https://public-api.solscan.io/account/transactions?address={address}&limit=5"
        txs = requests.get(url).json()
        bal_url = f"https://public-api.solscan.io/account/{address}"
        balance = float(requests.get(bal_url).json().get("lamports", 0)) / 1e9
        tx_list = [{
            "hash": tx.get("txHash", ""),
            "time": tx.get("blockTime", ""),
            "from": "",
            "to": "",
            "value": "N/A"
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(tx_list),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Solana",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(tx_list),
            "last5tx": tx_list
        }
    except:
        return default_result(address, "Solana", "❌ API rejected")

def fetch_hbar_data(address):
    try:
        url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/transactions?account.id={address}&limit=5"
        txs = requests.get(url).json().get("transactions", [])
        bal_url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        balance = int(requests.get(bal_url).json().get("balance", {}).get("balance", 0)) / 1e8
        tx_list = [{
            "hash": tx.get("transaction_hash", ""),
            "time": tx.get("consensus_timestamp", ""),
            "from": "",
            "to": "",
            "value": "N/A"
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": len(tx_list),
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "HBAR",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": len(tx_list),
            "last5tx": tx_list
        }
    except:
        return default_result(address, "HBAR", "❌ API rejected")

def fetch_base_data(address):
    try:
        url = f"https://api.basescan.org/api?module=account&action=balance&address={address}&apikey=AW748ZEW1BC72P2WY8REWHP1OHJV3HKR35C"
        balance = int(requests.get(url).json()["result"]) / 1e18
        # TX endpoint unavailable publicly
        tx_list = []
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": 0,
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "BASE",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": 0,
            "last5tx": tx_list
        }
    except:
        return default_result(address, "BASE", "❌ API rejected")
