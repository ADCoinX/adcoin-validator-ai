import requests
import os
import time
from datetime import datetime

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

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
    elif address.startswith("5") or len(address) in [43, 44]:
        result = ("Solana", fetch_solana_data(address))
    elif address.startswith("r") and len(address) >= 25:
        result = ("XRP", fetch_xrp_data(address))
    else:
        result = ("Unknown", {})

    # -------------------------
    # ✅ AI + ISO + Google Sheet
    data = result[1]

    risk_score = calculate_risk_score(
        data.get("balance", 0),
        data.get("tx_count", 0),
        data.get("wallet_age", 0)
    )

    send_to_google_sheet(
        address,
        "Valid" if data else "Invalid",
        risk_score,
        result[0]
    )

    generate_iso_xml(
        address,
        "Valid" if data else "Invalid",
        risk_score,
        result[0]
    )
    # -------------------------

    return result

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
    try:
        url = f"https://s1.ripple.com:51234"
        headers = {"Content-Type": "application/json"}
        payload = {
            "method": "account_info",
            "params": [
                {
                    "account": address,
                    "ledger_index": "validated",
                    "strict": True
                }
            ]
        }

        res = requests.post(url, headers=headers, json=payload)

        if res.status_code != 200:
            print("❌ XRP Ledger API Error", res.status_code)
            return {}

        data = res.json()
        account_data = data["result"].get("account_data", {})
        balance = float(account_data.get("Balance", 0)) / 1_000_000  # XRP in drops

        return {
            "balance": balance,
            "tx_count": 0,  # XRP Ledger REST doesn't give tx count directly
            "wallet_age": 0,  # Wallet age logic requires extra calls
            "last5tx": []
        }

    except Exception as e:
        print("❌ XRP Ledger API Exception", str(e))
        return {}

def send_to_google_sheet(wallet, result, risk_score, network, ip=None, ai_comment="", blacklisted=""):
    url = "https://script.google.com/macros/s/AKfycbzqcQZEzS_RrnC0pwx5ifNof6mhncnHO-TyqJuHd47fpG0u0-_C08fh1m9f4Yicxq79Gg/exec"

    payload = {
        "wallet": wallet,
        "result": result,
        "risk_score": risk_score,
        "network": network,
        "ip": ip or "Unknown",
        "ai_comment": ai_comment,
        "blacklisted": blacklisted
    }

    try:
        response = requests.post(url, json=payload)
        print("✅ Sheet Log:", response.text)
    except Exception as e:
        print("❌ Sheet Log Error:", str(e))

# ----------- XRP ----------
def fetch_xrp_data(address):
    ...
    return {...}

# ✅ TAMBAH SEMUA YANG INI KAT BAWAH SEKALI
# 🔐 Semak blacklist
def is_blacklisted(wallet):
    ...

# 🤖 AI Risk Score Calculator
def calculate_risk_score(balance, tx_count, wallet_age):
    ...

# 🧾 ISO 20022 Export
def generate_iso_xml(wallet, result, risk_score, network):
    ...
