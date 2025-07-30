import requests
import os
import time
from datetime import datetime
from blacklist import is_blacklisted
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY")
BLOCKCYPHER_API_KEY = os.environ.get("BLOCKCYPHER_API_KEY")
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY")

def get_wallet_data(address):
    if is_blacklisted(address):
        result = ("Scam Wallet", {})
    elif address.startswith("0x") and len(address) == 42:
        result = ("Ethereum", fetch_eth_data(address))
    elif address.startswith("T") and len(address) == 34:
        result = ("TRON", fetch_tron_data(address))
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        result = ("Bitcoin", fetch_btc_data(address))
    elif address.startswith("bnb"):
        result = ("Binance Smart Chain", fetch_bsc_data(address))
    elif len(address) in [43, 44] or address.startswith("5"):
        result = ("Solana", fetch_solana_data(address))
    elif address.startswith("r") and len(address) >= 25:
        result = ("XRP", fetch_xrp_data(address))
    else:
        result = ("Unknown", {})

    data = result[1]
    risk_score, reason = calculate_risk_score(data)
    generate_iso_xml(address, "Valid" if data else "Invalid", risk_score, result[0])
    return result

# Ethereum
def fetch_eth_data(address):
    try:
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
        balance_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"

        tx_resp = requests.get(tx_url).json()
        tx_list = tx_resp.get("result", [])[:5]

        balance_resp = requests.get(balance_url).json()
        if balance_resp.get("status") != "1":
            print("ETH API Error:", balance_resp)
            return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

        balance_wei = int(balance_resp.get("result", "0"))
        balance_eth = balance_wei / 1e18

        last5tx = []
        created_at = None
        if tx_list:
            created_at = int(tx_list[-1]["timeStamp"])
            for tx in tx_list:
                value_eth = int(tx["value"]) / 1e18
                last5tx.append({
                    "hash": tx["hash"],
                    "time": datetime.fromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S'),
                    "from": tx["from"],
                    "to": tx["to"],
                    "value": f"{value_eth:.5f} ETH"
                })

        age_days = int((time.time() - created_at) / 86400) if created_at else 0
        return {
            "balance": balance_eth,
            "tx_count": len(tx_list),
            "wallet_age": age_days,
            "last5tx": last5tx
        }
    except Exception as e:
        print("ETH API error:", str(e))
        return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

# TRON
def fetch_tron_data(address):
    try:
        headers = {"Authorization": f"Bearer {TRONGRID_API_KEY}"}
        info_url = f"https://api.trongrid.io/v1/accounts/{address}"
        tx_url = f"https://api.trongrid.io/v1/accounts/{address}/transactions?limit=5&order_by=block_timestamp,desc"

        res = requests.get(info_url, headers=headers).json()
        balance = int(res.get("data", [{}])[0].get("balance", 0)) / 1e6
        created_at = res.get("data", [{}])[0].get("create_time", 0)

        tx_data = requests.get(tx_url, headers=headers).json()
        tx_list = tx_data.get("data", [])

        last5tx = []
        for tx in tx_list:
            amount = int(tx.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("amount", 0)) / 1e6
            last5tx.append({
                "hash": tx["txID"],
                "time": datetime.fromtimestamp(tx["block_timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "from": tx["raw_data"]["contract"][0]["parameter"]["value"].get("owner_address", ""),
                "to": tx["raw_data"]["contract"][0]["parameter"]["value"].get("to_address", ""),
                "value": f"{amount:.2f} TRX"
            })

        age_days = int((time.time() - created_at / 1000) / 86400) if created_at else 0
        return {
            "balance": balance,
            "tx_count": len(tx_list),
            "wallet_age": age_days,
            "last5tx": last5tx
        }
    except Exception as e:
        print("TRON API error:", str(e))
        return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

# Bitcoin
def fetch_btc_data(address):
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance?token={BLOCKCYPHER_API_KEY}"
        res = requests.get(url).json()
        balance = int(res.get("balance", 0)) / 1e8
        tx_count = res.get("n_tx", 0)
        return {"balance": balance, "tx_count": tx_count, "wallet_age": 0, "last5tx": []}
    except Exception as e:
        print("BTC API error:", str(e))
        return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

# BSC (placeholder)
def fetch_bsc_data(address):
    return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

# Solana
def fetch_solana_data(address):
    try:
        url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key={HELIUS_API_KEY}"
        res = requests.get(url).json()
        lamports = res.get("nativeBalance", {}).get("lamports", 0)
        balance = lamports / 1e9
        return {"balance": balance, "tx_count": 0, "wallet_age": 0, "last5tx": []}
    except Exception as e:
        print("Solana API error:", str(e))
        return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

# XRP
def fetch_xrp_data(address):
    try:
        url = f"https://api.xrpscan.com/api/v1/account/{address}"
        response = requests.get(url)
        data = response.json()
        balance = float(data.get("balance", 0)) / 1_000_000
        tx_count = data.get("transaction_count", 0)
        return {"balance": balance, "tx_count": tx_count, "wallet_age": 0, "last5tx": []}
    except Exception as e:
        print("XRP API error:", str(e))
        return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}
