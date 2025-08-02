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
        elif address.startswith("sol") or len(address) == 44:
            return fetch_sol_data(address)
        elif address.lower().startswith("0x") and "base" in address.lower():
            return fetch_base_data(address)
        elif "-" in address and len(address) >= 42:
            return fetch_hbar_data(address)
        else:
            return default_result(address, "Unknown", "Invalid wallet format")
    except Exception as e:
        return default_result(address, "Unknown", f"Error: {str(e)}")

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
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey=YourEtherscanAPIKey"
        response = requests.get(url).json()
        balance = int(response["result"]) / 1e18

        txs_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey=YourEtherscanAPIKey"
        tx_response = requests.get(txs_url).json()
        txs = tx_response.get("result", [])[:5]
        tx_list = [{
            "hash": tx["hash"],
            "time": datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M'),
            "from": tx["from"],
            "to": tx["to"],
            "value": str(int(tx["value"]) / 1e18)
        } for tx in txs]

        score = calculate_risk_score(balance, len(txs), 0)

        return {
            "address": address,
            "network": "Ethereum",
            "balance": balance,
            "ai_score": score,
            "reason": "Fetched using Etherscan",
            "wallet_age": 0,
            "tx_count": len(txs),
            "last5tx": tx_list
        }

    except Exception as e:
        return default_result(address, "Ethereum", f"ETH Error: {str(e)}")
