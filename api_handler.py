import requests
from datetime import datetime
from iso_export import generate_iso_xml  # Pastikan iso_export.py ada
import os

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY")
BLOCKCYPHER_API_KEY = os.environ.get("BLOCKCYPHER_API_KEY")
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY")

def default_result():
    return {
        "network": "Unknown",
        "balance": "❌",
        "transactions": [],
        "risk_score": "❌",
        "reason": "❌ API rejected",
        "iso20022": None
    }

def fetch_eth_data(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"
        bal_res = requests.get(url).json()
        balance = str(int(bal_res["result"]) / 1e18)
        print("DEBUG ETH Balance:", balance)

        tx_url = f"https://api.ethplorer.io/getAddressTransactions/{address}?apiKey=freekey"
        tx_res = requests.get(tx_url).json()
        print("DEBUG ETH Transactions:", tx_res)
        transactions = [{
            "hash": tx["hash"],
            "timestamp": datetime.utcfromtimestamp(tx["timestamp"]).strftime('%Y-%m-%d %H:%M:%S'),
            "value": str(tx["value"])
        } for tx in tx_res[:5]]

        return {
            "network": "Ethereum",
            "balance": balance,
            "transactions": transactions,
            "risk_score": "✔️",
            "reason": "✔️ Live",
            "iso20022": generate_iso_xml(address)
        }
    except Exception as e:
        print("ETH ERROR:", e)
        return default_result()

def fetch_tron_data(address):
    try:
        url = f"https://api.trongrid.io/v1/accounts/{address}"
        headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY}
        res = requests.get(url, headers=headers).json()
        print("DEBUG TRON Balance:", res)
        balance = str(res["data"][0]["balance"] / 1e6)

        tx_url = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=5&start=0&address={address}"
        txs = requests.get(tx_url).json()["data"]
        print("DEBUG TRON Transactions:", txs)
        transactions = [{
            "hash": tx["hash"],
            "timestamp": datetime.utcfromtimestamp(tx["timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            "value": str(tx["contractData"].get("amount", 0) / 1e6)
        } for tx in txs]

        return {
            "network": "TRON",
            "balance": balance,
            "transactions": transactions,
            "risk_score": "✔️",
            "reason": "✔️ Live",
            "iso20022": generate_iso_xml(address)
        }
    except Exception as e:
        print("TRON ERROR:", e)
        return default_result()

def fetch_btc_data(address):
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance?token={BLOCKCYPHER_API_KEY}"
        res = requests.get(url).json()
        print("DEBUG BTC Balance:", res)
        balance = str(res["balance"] / 1e8)

        tx_url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}?limit=5&token={BLOCKCYPHER_API_KEY}"
        tx_res = requests.get(tx_url).json()
        print("DEBUG BTC Transactions:", tx_res)
        transactions = [{
            "hash": tx["hash"],
            "timestamp": tx.get("confirmed", "N/A"),
            "value": str(tx.get("total", 0) / 1e8)
        } for tx in tx_res.get("txrefs", [])[:5]]

        return {
            "network": "Bitcoin",
            "balance": balance,
            "transactions": transactions,
            "risk_score": "✔️",
            "reason": "✔️ Live",
            "iso20022": generate_iso_xml(address)
        }
    except Exception as e:
        print("BTC ERROR:", e)
        return default_result()

def fetch_xrp_data(address):
    try:
        url = f"https://api.xrpscan.com/api/v1/account/{address}/basic"
        res = requests.get(url).json()
        print("DEBUG XRP Balance:", res)
        balance = str(float(res.get("balance", 0)) / 1e6)

        tx_url = f"https://api.xrpscan.com/api/v1/account/{address}/transactions?limit=5"
        txs = requests.get(tx_url).json()
        print("DEBUG XRP Transactions:", txs)
        transactions = [{
            "hash": tx["hash"],
            "timestamp": tx["date"],
            "value": str(tx.get("amount", "0"))
        } for tx in txs]

        return {
            "network": "XRP",
            "balance": balance,
            "transactions": transactions,
            "risk_score": "✔️",
            "reason": "✔️ Live",
            "iso20022": generate_iso_xml(address)
        }
    except Exception as e:
        print("XRP ERROR:", e)
        return default_result()

def fetch_sol_data(address):
    try:
        url = f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key={HELIUS_API_KEY}"
        res = requests.get(url).json()
        print("DEBUG SOL Balance:", res)
        sol_bal = next((item for item in res["tokens"] if item["token_symbol"] == "SOL"), None)
        balance = str(float(sol_bal["amount"]) if sol_bal else 0)

        tx_url = f"https://api.solana.fm/v0/accounts/{address}/transactions?limit=5"
        txs = requests.get(tx_url).json().get("transactions", [])
        print("DEBUG SOL Transactions:", txs)
        transactions = [{
            "hash": tx["signature"],
            "timestamp": tx["blockTime"],
            "value": "N/A"
        } for tx in txs[:5]]

        return {
            "network": "Solana",
            "balance": balance,
            "transactions": transactions,
            "risk_score": "✔️",
            "reason": "✔️ Live",
            "iso20022": generate_iso_xml(address)
        }
    except Exception as e:
        print("SOL ERROR:", e)
        return default_result()

def get_wallet_data(address):
    if address.startswith("0x") and len(address) == 42:
        return fetch_eth_data(address)
    elif address.startswith("T") and len(address) == 34:
        return fetch_tron_data(address)
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        return fetch_btc_data(address)
    elif address.startswith("r") and len(address) > 20:
        return fetch_xrp_data(address)
    elif len(address) >= 32 and address.isalnum():
        return fetch_sol_data(address)
    else:
        return default_result()
