import requests
from datetime import datetime, timezone
from urllib.parse import quote
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml

# Constants
API_REJECTED_MSG = "❌ API rejected"

def sanitize_address(address):
    return quote(address.lower())  # Encode URL untuk elak injection

def get_wallet_data(address):
    try:
        safe_address = sanitize_address(address)
        if not safe_address:
            raise ValueError("Invalid wallet format")

        if safe_address.startswith("0x") and len(safe_address) == 42:
            return fetch_eth_data(safe_address)
        elif safe_address.startswith("T") and len(safe_address) == 34:
            return fetch_tron_data(safe_address)
        elif safe_address.startswith("1") or safe_address.startswith("3") or safe_address.startswith("bc1"):
            return fetch_btc_data(safe_address)
        elif safe_address.startswith("r") and len(safe_address) >= 25:
            return fetch_xrp_data(safe_address)
        elif len(safe_address) == 44:
            return fetch_sol_data(safe_address)
        elif safe_address.startswith("0.0.") and safe_address.count(".") == 2:
            return fetch_hbar_data(safe_address)
        elif safe_address.lower().startswith("0x") and "base" in safe_address.lower():
            return fetch_base_data(safe_address)
        else:
            raise ValueError("Invalid wallet format")
    except ValueError as ve:
        return {"status": "0", "message": "NOTOK", "result": str(ve)}
    except requests.exceptions.RequestException as re:
        return default_result(address, "Unknown", f"❌ Error: {str(re)}")
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
        # API 1: Ethplorer (public free tier)
        url = f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey"
        response = requests.get(url, timeout=10).json()
        balance = response.get("ETH", {}).get("balance", 0)
        tx_count = response.get("countTxs", 0)
        txs = response.get("operations", [])[:5]
        tx_list = [{
            "hash": tx.get("transactionHash", ""),
            "time": datetime.fromtimestamp(tx.get("timestamp", 0), tz=timezone.utc).strftime('%Y-%m-%d %H:%M'),
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
    except requests.exceptions.RequestException as e:
        print(f"[Ethplorer Failed] {e}")
        try:
            # API 2: Blockscout (public)
            url = f"https://eth.blockscout.com/api/v2/addresses/{address}"
            response = requests.get(url, timeout=10).json()
            balance = int(response.get("coin_balance", 0)) / 1e18
            tx_count = response.get("transactions_count", 0)
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
                "last5tx": []
            }
        except requests.exceptions.RequestException as e:
            print(f"[Blockscout Failed] {e}")
            try:
                # API 3: DeFiLlama (public)
                url = f"https://coins.llama.fi/prices/current/ethereum:{address}"
                response = requests.get(url, timeout=10).json()
                balance = response.get("coins", {}).get(f"ethereum:{address}", {}).get("price", 0)
                tx_count = 0
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
                    "last5tx": []
                }
            except requests.exceptions.RequestException as e:
                print(f"[DeFiLlama Failed] {e}")
                return default_result(address, "Ethereum", API_REJECTED_MSG)

# (Kod untuk fetch_tron_data, fetch_btc_data, fetch_xrp_data, fetch_sol_data, fetch_hbar_data, fetch_base_data serupa seperti sebelum ini, dengan public API je—aku tak ubah sebab dah ok, tapi kalau nak full, copy dari versi lama)
