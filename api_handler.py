import requests
from get_eth_data import fetch_eth_data
from get_tron_data import fetch_tron_data
from get_btc_data import fetch_btc_data
from get_xrp_data import fetch_xrp_data
from get_solana_data import fetch_sol_data
from get_hedera_data import fetch_hbar_data
from get_base_data import fetch_base_data  # Jika ada fail ini
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml
from datetime import datetime

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
        elif len(address) == 44:  # Solana typical address length
            return fetch_sol_data(address)
        elif "-" in address and len(address) >= 42:
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
