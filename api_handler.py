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
        # API 1: Ethplorer (public free tier, no private key)
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
            # API 2: Blockscout (public, no key)
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
                # API 3: DeFiLlama (public, no key, for balance query)
                url = f"https://coins.llama.fi/prices/current/ethereum:{address}"
                response = requests.get(url, timeout=10).json()
                balance = response.get("coins", {}).get(f"ethereum:{address}", {}).get("price", 0)
                # tx_count not available, set to 0
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

def fetch_tron_data(address):
    try:
        # API 1: Tronscan (correct public endpoint, no key)
        url = f"https://api.tronscan.org/api/account?address={address}"
        response = requests.get(url, timeout=10).json()
        balance = int(response.get("balance", 0)) / 1e6
        tx_count = response.get("totalTransactionCount", 0)
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": tx_count,
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "TRON",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": tx_count,
            "last5tx": []
        }
    except requests.exceptions.RequestException as e:
        print(f"[Tronscan Failed] {e}")
        try:
            # API 2: Trongrid (public, no key)
            url = f"https://api.trongrid.io/v1/accounts/{address}"
            response = requests.get(url, timeout=10).json()
            balance = int(response["data"][0].get("balance", 0)) / 1e6
            tx_count = len(response.get("data", []))
            score, reason = calculate_risk_score({
                "balance": balance,
                "tx_count": tx_count,
                "wallet_age": 0
            })
            return {
                "address": address,
                "network": "TRON",
                "balance": balance,
                "ai_score": score,
                "reason": reason,
                "wallet_age": 0,
                "tx_count": tx_count,
                "last5tx": []
            }
        except requests.exceptions.RequestException as e:
            print(f"[Trongrid Failed] {e}")
            try:
                # API 3: Tron Explorer (public, no key)
                url = f"https://api.tronex.io/v1/account/{address}"
                response = requests.get(url, timeout=10).json()
                balance = int(response.get("balance", 0)) / 1e6
                tx_count = response.get("tx_count", 0)
                score, reason = calculate_risk_score({
                    "balance": balance,
                    "tx_count": tx_count,
                    "wallet_age": 0
                })
                return {
                    "address": address,
                    "network": "TRON",
                    "balance": balance,
                    "ai_score": score,
                    "reason": reason,
                    "wallet_age": 0,
                    "tx_count": tx_count,
                    "last5tx": []
                }
            except requests.exceptions.RequestException as e:
                print(f"[Tron Explorer Failed] {e}")
                return default_result(address, "TRON", API_REJECTED_MSG)

def fetch_btc_data(address):
    try:
        # API 1: Blockcypher (public, no key)
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        response = requests.get(url, timeout=10).json()
        balance = int(response.get("final_balance", 0)) / 1e8
        tx_count = response.get("n_tx", 0)
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": tx_count,
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Bitcoin",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": tx_count,
            "last5tx": []
        }
    except requests.exceptions.RequestException as e:
        print(f"[Blockcypher Failed] {e}")
        try:
            # API 2: Blockstream (public, no key)
            url = f"https://blockstream.info/api/address/{address}"
            response = requests.get(url, timeout=10).json()
            balance = response.get("chain_stats", {}).get("funded_txo_sum", 0) / 1e8
            tx_count = response.get("chain_stats", {}).get("tx_count", 0)
            score, reason = calculate_risk_score({
                "balance": balance,
                "tx_count": tx_count,
                "wallet_age": 0
            })
            return {
                "address": address,
                "network": "Bitcoin",
                "balance": balance,
                "ai_score": score,
                "reason": reason,
                "wallet_age": 0,
                "tx_count": tx_count,
                "last5tx": []
            }
        except requests.exceptions.RequestException as e:
            print(f"[Blockstream Failed] {e}")
            try:
                # API 3: Chain.so (public, no key)
                url = f"https://chain.so/api/v2/get_address_balance/BTC/{address}"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("data", {}).get("confirmed_balance", 0))
                tx_count = response.get("data", {}).get("txs", 0)
                score, reason = calculate_risk_score({
                    "balance": balance,
                    "tx_count": tx_count,
                    "wallet_age": 0
                })
                return {
                    "address": address,
                    "network": "Bitcoin",
                    "balance": balance,
                    "ai_score": score,
                    "reason": reason,
                    "wallet_age": 0,
                    "tx_count": tx_count,
                    "last5tx": []
                }
            except requests.exceptions.RequestException as e:
                print(f"[Chain.so Failed] {e}")
                return default_result(address, "Bitcoin", API_REJECTED_MSG)

def fetch_xrp_data(address):
    try:
        # API 1: XRPL RPC (public, no key, POST request)
        url = "https://s1.ripple.com:51234/"
        payload = {
            "method": "account_info",
            "params": [{
                "account": address,
                "ledger_index": "current"
            }]
        }
        response = requests.post(url, json=payload, timeout=10).json()
        if 'result' in response and 'account_data' in response['result']:
            balance = int(response['result']['account_data']['Balance']) / 1e6
            tx_count = response['result'].get('transaction_count', 0)
            score, reason = calculate_risk_score({
                "balance": balance,
                "tx_count": tx_count,
                "wallet_age": 0
            })
            return {
                "address": address,
                "network": "XRP",
                "balance": balance,
                "ai_score": score,
                "reason": reason,
                "wallet_age": 0,
                "tx_count": tx_count,
                "last5tx": []
            }
        else:
            print("Invalid response from XRPL RPC")
    except requests.exceptions.RequestException as e:
        print(f"[XRPL RPC Failed] {e}")
        try:
            # API 2: Ripple Data API (public, no key)
            url = f"https://data.ripple.com/v2/accounts/{address}/balances"
            response = requests.get(url, timeout=10).json()
            balance = float(response["balances"][0].get("value", 0))
            tx_count = response.get("transaction_count", 0)
            score, reason = calculate_risk_score({
                "balance": balance,
                "tx_count": tx_count,
                "wallet_age": 0
            })
            return {
                "address": address,
                "network": "XRP",
                "balance": balance,
                "ai_score": score,
                "reason": reason,
                "wallet_age": 0,
                "tx_count": tx_count,
                "last5tx": []
            }
        except requests.exceptions.RequestException as e:
            print(f"[Ripple Failed] {e}")
            try:
                # API 3: Bithomp (public, no key)
                url = f"https://bithomp.com/api/v2/address/{address}"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("xrpBalance", 0))
                tx_count = response.get("transactionCount", 0)
                score, reason = calculate_risk_score({
                    "balance": balance,
                    "tx_count": tx_count,
                    "wallet_age": 0
                })
                return {
                    "address": address,
                    "network": "XRP",
                    "balance": balance,
                    "ai_score": score,
                    "reason": reason,
                    "wallet_age": 0,
                    "tx_count": tx_count,
                    "last5tx": []
                }
            except requests.exceptions.RequestException as e:
                print(f"[Bithomp Failed] {e}")
                return default_result(address, "XRP", API_REJECTED_MSG)

def fetch_sol_data(address):
    try:
        # API 1: Solscan (public, no key)
        url = f"https://public-api.solscan.io/account/{address}"
        response = requests.get(url, timeout=10).json()
        balance = float(response.get("lamports", 0)) / 1e9
        tx_count = response.get("transactionCount", 0)
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": tx_count,
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "Solana",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": tx_count,
            "last5tx": []
        }
    except requests.exceptions.RequestException as e:
        print(f"[Solscan Failed] {e}")
        try:
            # API 2: Solana Explorer (public, no key)
            url = f"https://explorer.solana.com/address/{address}?cluster=mainnet-beta"
            # Note: Solana Explorer doesn't have direct JSON API, so use RPC
            url = "https://api.mainnet-beta.solana.com"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [address]
            }
            response = requests.post(url, json=payload, timeout=10).json()
            balance = response.get("result", {}).get("value", 0) / 1e9
            # For tx_count, use separate call
            payload_tx = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [address, {"limit": 1}]
            }
            response_tx = requests.post(url, json=payload_tx, timeout=10).json()
            tx_count = len(response_tx.get("result", []))
            score, reason = calculate_risk_score({
                "balance": balance,
                "tx_count": tx_count,
                "wallet_age": 0
            })
            return {
                "address": address,
                "network": "Solana",
                "balance": balance,
                "ai_score": score,
                "reason": reason,
                "wallet_age": 0,
                "tx_count": tx_count,
                "last5tx": []
            }
        except requests.exceptions.RequestException as e:
            print(f"[Solana RPC Failed] {e}")
            try:
                # API 3: Solana Beach (public, no key)
                url = f"https://api.solana.beach/v1/account/{address}"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("data", {}).get("lamports", 0)) / 1e9
                tx_count = response.get("transaction_count", 0)
                score, reason = calculate_risk_score({
                    "balance": balance,
                    "tx_count": tx_count,
                    "wallet_age": 0
                })
                return {
                    "address": address,
                    "network": "Solana",
                    "balance": balance,
                    "ai_score": score,
                    "reason": reason,
                    "wallet_age": 0,
                    "tx_count": tx_count,
                    "last5tx": []
                }
            except requests.exceptions.RequestException as e:
                print(f"[Solana Beach Failed] {e}")
                return default_result(address, "Solana", API_REJECTED_MSG)

def fetch_hbar_data(address):
    try:
        # API 1: Hedera Mirror Node (public, no key)
        url = f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{address}"
        response = requests.get(url, timeout=10).json()
        balance_data = response.get("balance", {}).get("balance", 0)
        balance = int(balance_data) / 1e8
        tokens = response.get("balance", {}).get("tokens", [])
        tx_count = len(tokens) if tokens else 0
        score, reason = calculate_risk_score({
            "balance": balance,
            "tx_count": tx_count,
            "wallet_age": 0
        })
        return {
            "address": address,
            "network": "HBAR",
            "balance": balance,
            "ai_score": score,
            "reason": reason,
            "wallet_age": 0,
            "tx_count": tx_count,
            "last5tx": []
        }
    except requests.exceptions.RequestException as e:
        print(f"[Hedera Mirror Failed] {e}")
        try:
            # API 2: Hashscan (public, no key)
            url = f"https://hashscan.io/mainnet/api/account/{address}"
            response = requests.get(url, timeout=10).json()
            balance = int(response.get("balance", 0)) / 1e8
            tx_count = response.get("transaction_count", 0)
            score, reason = calculate_risk_score({
                "balance": balance,
                "tx_count": tx_count,
                "wallet_age": 0
            })
            return {
                "address": address,
                "network": "HBAR",
                "balance": balance,
                "ai_score": score,
                "reason": reason,
                "wallet_age": 0,
                "tx_count": tx_count,
                "last5tx": []
            }
        except requests.exceptions.RequestException as e:
            print(f"[Hashscan Failed] {e}")
            try:
                # API 3: DragonGlass (public, no key for basic)
                url = f"https://api.dragonglass.me/hedera/v1/accounts/{address}"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("balance", 0)) / 1e8
                tx_count = response.get("tx_count", 0)
                score, reason = calculate_risk_score({
                    "balance": balance,
                    "tx_count": tx_count,
                    "wallet_age": 0
                })
                return {
                    "address": address,
                    "network": "HBAR",
                    "balance": balance,
                    "ai_score": score,
                    "reason": reason,
                    "wallet_age": 0,
                    "tx_count": tx_count,
                    "last5tx": []
                }
            except requests.exceptions.RequestException as e:
                print(f"[DragonGlass Failed] {e}")
                return default_result(address, "HBAR", API_REJECTED_MSG)

def fetch_base_data(address):
    try:
        # API 1: Blockscout (public, no key)
        url = f"https://base.blockscout.com/api/v2/addresses/{address}"
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
            "network": "Base",
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
            # API 2: Basescan (public basic query, no key for balance)
            url = f"https://api.basescan.org/api?module=account&action=balance&address={address}"
            response = requests.get(url, timeout=10).json()
            if response.get("status") == "1":
                balance = int(response.get("result", 0)) / 1e18
            else:
                balance = 0
            # tx_count not direct, set to 0 or add another call
            tx_count = 0
            score, reason = calculate_risk_score({
                "balance": balance,
                "tx_count": tx_count,
                "wallet_age": 0
            })
            return {
                "address": address,
                "network": "Base",
                "balance": balance,
                "ai_score": score,
                "reason": reason,
                "wallet_age": 0,
                "tx_count": tx_count,
                "last5tx": []
            }
        except requests.exceptions.RequestException as e:
            print(f"[Basescan Failed] {e}")
            try:
                # API 3: DeFiLlama (public, no key)
                url = f"https://coins.llama.fi/prices/current/base:{address}"
                response = requests.get(url, timeout=10).json()
                balance = response.get("coins", {}).get(f"base:{address}", {}).get("price", 0)
                tx_count = 0  # Not available
                score, reason = calculate_risk_score({
                    "balance": balance,
                    "tx_count": tx_count,
                    "wallet_age": 0
                })
                return {
                    "address": address,
                    "network": "Base",
                    "balance": balance,
                    "ai_score": score,
                    "reason": reason,
                    "wallet_age": 0,
                    "tx_count": tx_count,
                    "last5tx": []
                }
            except requests.exceptions.RequestException as e:
                print(f"[DeFiLlama Failed] {e}")
                return default_result(address, "Base", API_REJECTED_MSG)
