import requests
import os
import time
from datetime import datetime

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

def get_wallet_data(address):
    if address.startswith("0x") and len(address) == 42:
        return "Ethereum", fetch_eth_data(address)
    elif address.startswith("T") and len(address) == 34:
        return "TRON", fetch_tron_data(address)
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        return "Bitcoin", fetch_btc_data(address)
    elif address.startswith("B") or address.startswith("bnb"):
        return "Binance Smart Chain", fetch_bsc_data(address)
    elif address.startswith("S") or len(address) in [43, 44]:
        return "Solana", fetch_solana_data(address)
    elif address.startswith("r") and len(address) >= 25:
        return "XRP", fetch_xrp_data(address)
    else:
        return "Unknown", {}

# ----------- Ethereum ----------
def fetch_eth_data(address):
    tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    balance_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"

    tx = requests.get(tx_url).json()
    tx_list = tx.get("result", [])[:5]

    balance_wei = int(requests.get(balance_url).json().get("result", 0))
    balance_eth = balance_wei / 1e18

    last5tx = []
    created_at = None
    if tx_list:
        created_at = int(tx_list[-1]['timeStamp'])
        for tx in tx_list:
            value_eth = int(tx['value']) / 1e18
            last5tx.append({
                "hash": tx["hash"],
                "time": datetime.fromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S'),
                "from": tx["from"],
                "to": tx["to"],
                "value": f"{value_eth:.5f} ETH"
            })

    age_days = int((time.time() - created_at) / 86400) if created_at else 0
    return {"balance": balance_eth, "tx_count": len(tx_list), "wallet_age": age_days, "last5tx": last5tx}

# ----------- TRON ----------
def fetch_tron_data(address):
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
    return {"balance": balance, "tx_count": len(tx_list), "wallet_age": age_days, "last5tx": last5tx}

# ----------- Bitcoin ----------
def fetch_btc_data(address):
    url = f"https://blockstream.info/api/address/{address}"
    res = requests.get(url).json()
    balance = int(res.get("chain_stats", {}).get("funded_txo_sum", 0)) / 1e8
    tx_count = res.get("chain_stats", {}).get("tx_count", 0)
    return {"balance": balance, "tx_count": tx_count, "wallet_age": 0, "last5tx": []}

# ----------- BSC ----------
def fetch_bsc_data(address):
    return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

# ----------- Solana ----------
def fetch_solana_data(address):
    return {"balance": 0, "tx_count": 0, "wallet_age": 0, "last5tx": []}

# ----------- XRP ----------
def fetch_xrp_data(address):
    url = f"https://api.xrpscan.com/api/v1/account/{address}"
    res = requests.get(url).json()
    balance = float(res.get("xrpBalance", 0))
    tx_count = res.get("transactionCount", 0)
    return {"balance": balance, "tx_count": tx_count, "wallet_age": 0, "last5tx": []}
