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
            return default_result(address, "Unknown", "❌ Invalid wallet format")

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
            return default_result(address, "Unknown", "❌ Invalid wallet format")
    except requests.exceptions.RequestException as re:
        return default_result(address, "Unknown", f"❌ Error: {str(re)}")
    except ValueError as ve:
        return {"status": "0", "message": "NOTOK", "result": str(ve)}
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
        # API 1: Ethplorer (public)
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
            # API 2: Blockscout
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
                # API 3: OpenChain
                url = f"https://api.openchain.xyz/address/{address}"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("balance", 0))
                tx_count = response.get("transaction_count", 0)
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
                print(f"[OpenChain Failed] {e}")
                return default_result(address, "Ethereum", API_REJECTED_MSG)

def fetch_tron_data(address):
    try:
        # API 1: Tronscan
        url = f"https://apilist.tronscanapi.com/api/account?address={address}"
        response = requests.get(url, timeout=10).json()
        balance = int(response.get("balance", 0)) / 1e6
        tx_count = response.get("totalTransactions", 0)
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
            # API 2: Trongrid
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
                # API 3: Shasta (testnet public)
                url = f"https://api.shasta.trongrid.io/v1/accounts/{address}"
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
                print(f"[Shasta Failed] {e}")
                return default_result(address, "TRON", API_REJECTED_MSG)

def fetch_btc_data(address):
    try:
        # API 1: Blockcypher
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
            # API 2: Blockstream
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
                # API 3: Chain.so
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
        # API 1: XRPSCAN
        url = f"https://api.xrpscan.com/api/v1/account/{address}/balances"
        response = requests.get(url, timeout=10).json()
        balance = float(response[0].get("value", 0))
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
        print(f"[XRPSCAN Failed] {e}")
        try:
            # API 2: Ripple Data API
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
                # API 3: Bithomp
                url = f"https://bithomp.com/api/v2/addresses/{address}/info"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("balance", 0))
                tx_count = response.get("transactions", 0)
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
        # API 1: Solscan
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
            # API 2: Solana Explorer
            url = f"https://explorer.solana.com/api/v1/address/{address}"
            response = requests.get(url, timeout=10).json()
            balance = float(response.get("balance", 0)) / 1e9
            tx_count = response.get("tx_count", 0)
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
            print(f"[Solana Explorer Failed] {e}")
            try:
                # API 3: QuickNode (public endpoint)
                url = f"https://public-api.quicknode.com/solana/mainnet/address/{address}/balance"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("balance", 0)) / 1e9
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
                print(f"[QuickNode Failed] {e}")
                return default_result(address, "Solana", API_REJECTED_MSG)

def fetch_hbar_data(address):
    try:
        # API 1: Hedera Mirror Node
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
            # API 2: Hashscan
            url = f"https://hashscan.io/api/mainnet/account/{address}"
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
                # API 3: DragonGlass
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
        # API 1: Blockscout
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
            # API 2: Basescan
            url = f"https://api.basescan.org/api?module=account&action=balance&address={address}"
            response = requests.get(url, timeout=10).json()
            balance = int(response.get("result", 0)) / 1e18
            tx_count = response.get("tx_count", 0)
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
                # API 3: OpenChain
                url = f"https://api.openchain.xyz/address/{address}"
                response = requests.get(url, timeout=10).json()
                balance = float(response.get("balance", 0))
                tx_count = response.get("transaction_count", 0)
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
                print(f"[OpenChain Failed] {e}")
                return default_result(address, "Base", API_REJECTED_MSG)
