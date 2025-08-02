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
        elif address.startswith("0.0.") and address.count(".") == 2:
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
        # Primary API: Etherscan
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={ETHERSCAN_API_KEY}"
        
        balance_response = requests.get(url, timeout=10).json()
        tx_response = requests.get(tx_url, timeout=10).json()

        if balance_response.get("status") == "1" and tx_response.get("status") == "1":
            balance = int(balance_response["result"]) / 1e18
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
        print(f"[Etherscan Failed] {e}")

    # Fallback API: Ethplorer
    try:
        url = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey"
        response = requests.get(url, timeout=10).json()

        balance = response.get("ETH", {}).get("balance", 0)
        tx_count = response.get("countTxs", 0)
        txs = response.get("operations", [])[:5]
        tx_list = [{
            "hash": tx.get("transactionHash", ""),
            "time": datetime.utcfromtimestamp(tx.get("timestamp", 0)).strftime('%Y-%m-%d %H:%M'),
            "from": tx.get("from", ""),
            "to": tx.get("to", ""),
            "value": str(tx.get("value", 0))
        } for tx in txs]
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": tx_count,
            "wallet_age": 0
        })

        return {
            "address": address,
            "network": "Ethereum",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": tx_count,
            "last5tx": tx_list
        }

    except Exception as e:
        print(f"[Ethplorer Failed] {e}")
        return default_result(address, "Ethereum", "❌ API rejected")

# 🔻 Yang bawah ni dari kod asal kau, tak diubah langsung

def fetch_tron_data(address):
    try:
        url = f"https://api.trongrid.io/v1/accounts/{address}"
        response = requests.get(url).json()
        balance = int(response["data"][0].get("balance", 0)) / 1e6
    except:
        try:
            url = f"https://apilist.tronscanapi.com/api/account?address={address}"
            response = requests.get(url).json()
            balance = int(response.get("balance", 0)) / 1e6
        except:
            return default_result(address, "TRON", "❌ API rejected")

    tx_list = []
    score, reason = calculate_risk_score({
        "balance": balance,
        "tx_count": 0,
        "wallet_age": 0
    })

    return {
        "address": address,
        "network": "TRON",
        "balance": balance,
        "ai_score": score,
        "reason": reason,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": tx_list
    }

def fetch_btc_data(address):
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        response = requests.get(url).json()
        balance = int(response["final_balance"]) / 1e8
    except:
        try:
            url = f"https://blockstream.info/api/address/{address}"
            response = requests.get(url).json()
            balance = response.get("chain_stats", {}).get("funded_txo_sum", 0) / 1e8
        except:
            return default_result(address, "Bitcoin", "❌ API rejected")

    score, reason = calculate_risk_score({
        "balance": balance,
        "tx_count": 0,
        "wallet_age": 0
    })

    return {
        "address": address,
        "network": "Bitcoin",
        "balance": balance,
        "ai_score": score,
        "reason": reason,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

def fetch_xrp_data(address):
    try:
        url = f"https://api.xrpscan.com/api/v1/account/{address}/balances"
        response = requests.get(url).json()
        balance = float(response[0]["value"])
    except:
        try:
            url = f"https://data.ripple.com/v2/accounts/{address}/balances"
            response = requests.get(url).json()
            balance = float(response["balances"][0]["value"])
        except:
            return default_result(address, "XRP", "❌ API rejected")

    score, reason = calculate_risk_score({
        "balance": balance,
        "tx_count": 0,
        "wallet_age": 0
    })

    return {
        "address": address,
        "network": "XRP",
        "balance": balance,
        "ai_score": score,
        "reason": reason,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

def fetch_sol_data(address):
    try:
        url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key=90048cfc-009e-4e79-a4ae-3070d2fc5a5c"
        response = requests.get(url).json()
        balance = float(response["nativeBalance"]["sol"])
    except:
        try:
            url = f"https://public-api.solscan.io/account/{address}"
            response = requests.get(url).json()
            balance = float(response.get("lamports", 0)) / 1e9
        except:
            return default_result(address, "Solana", "❌ API rejected")

    score, reason = calculate_risk_score({
        "balance": balance,
        "tx_count": 0,
        "wallet_age": 0
    })

    return {
        "address": address,
        "network": "Solana",
        "balance": balance,
        "ai_score": score,
        "reason": reason,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

def fetch_hbar_data(address):
    try:
        url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        response = requests.get(url).json()
        balance = int(response["balance"]) / 1e8
    except:
        try:
            url = f"https://hashscan.io/api/mainnet/account/{address}"
            response = requests.get(url).json()
            balance = int(response["balance"]) / 1e8
        except:
            return default_result(address, "HBAR", "❌ API rejected")

    score, reason = calculate_risk_score({
        "balance": balance,
        "tx_count": 0,
        "wallet_age": 0
    })

    return {
        "address": address,
        "network": "HBAR",
        "balance": balance,
        "ai_score": score,
        "reason": reason,
        "wallet_age": 0,
        "tx_count": 0,
        "last5tx": []
    }

def fetch_base_data(address):
    try:
        url = f"https://api.basescan.org/api?module=account&action=balance&address={address}&apikey=AW748ZEW1BC72P2WY8REWHP1OHJV3HKR35C"
        response = requests.get(url).json()
        balance = int(response["result"]) / 1e18
    except:
        try:
            url = f"https://api.blockscout.com/base/mainnet/api?module=account&action=balance&address={address}"
            response = requests.get(url).json()
            balance = int(response["result"]) / 1e18
        except:
            return default_result(address, "BASE", "❌ API rejected")

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
        "last5tx": []
    }
