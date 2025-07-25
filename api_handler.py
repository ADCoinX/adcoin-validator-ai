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

# ---------------- Ethereum / BSC ----------------
def fetch_eth_data(address):
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY
    }
    tx = requests.get(url, params=params).json()
    tx_list = tx.get("result", [])
    tx_count = len(tx_list)
    balance_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"
    balance_wei = int(requests.get(balance_url).json().get("result", 0))
    balance_eth = balance_wei / 1e18
    created_at = None
    if tx_list:
        created_at = int(tx_list[0]['timeStamp'])
    age_days = int((time.time() - created_at) / 86400) if created_at else 0
    return {"balance": balance_eth, "tx_count": tx_count, "wallet_age": age_days}

# ---------------- TRON ----------------
def fetch_tron_data(address):
    headers = {"Authorization": f"Bearer {TRONGRID_API_KEY}"}
    url = f"https://api.trongrid.io/v1/accounts/{address}"
    res = requests.get(url, headers=headers).json()
    balance = int(res.get("data", [{}])[0].get("balance", 0)) / 1e6
    tx_url = f"https://api.trongrid.io/v1/accounts/{address}/transactions"
    tx_data = requests.get(tx_url, headers=headers).json()
    tx_count = len(tx_data.get("data", []))
    created_at = res.get("data", [{}])[0].get("create_time", 0)
    age_days = int((time.time() - created_at / 1000) / 86400) if created_at else 0
    return {"balance": balance, "tx_count": tx_count, "wallet_age": age_days}

# ---------------- Bitcoin ----------------
def fetch_btc_data(address):
    url = f"https://blockstream.info/api/address/{address}"
    res = requests.get(url).json()
    balance = int(res.get("chain_stats", {}).get("funded_txo_sum", 0)) / 1e8
    tx_count = res.get("chain_stats", {}).get("tx_count", 0)
    age_days = 0  # BTC API doesn't give wallet age
    return {"balance": balance, "tx_count": tx_count, "wallet_age": age_days}

# ---------------- Solana ----------------
def fetch_solana_data(address):
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [address, {"encoding": "jsonParsed"}]
    }
    res = requests.post(url, json=payload).json()
    balance = 0
    if res.get("result") and res["result"].get("value"):
        lamports = res["result"]["value"].get("lamports", 0)
        balance = lamports / 1e9
    tx_count = 0  # Need extra RPC calls for tx count
    return {"balance": balance, "tx_count": tx_count, "wallet_age": 0}

# ---------------- XRP ----------------
def fetch_xrp_data(address):
    url = f"https://api.xrpscan.com/api/v1/account/{address}"
    res = requests.get(url).json()
    balance = float(res.get("xrpBalance", 0))
    tx_count = res.get("transactionCount", 0)
    return {"balance": balance, "tx_count": tx_count, "wallet_age": 0}
