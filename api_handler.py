from get_eth_data import get_eth_data
from get_tron_data import get_tron_data
from get_btc_data import get_btc_data
from get_xrp_data import get_xrp_data
from get_sol_data import get_sol_data
from get_base_data import get_base_data
from get_hedera_data import get_hedera_data
from get_bsc_data import get_bsc_data
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml
from datetime import datetime

def get_wallet_data(address):
    try:
        if address.startswith("0x") and len(address) == 42:
            if address.lower().startswith("0x") and address[2:4].isdigit():
                network = "BASE"
                data = get_base_data(address)
            else:
                network = "Ethereum"
                data = get_eth_data(address)

        elif address.startswith("T") and len(address) == 34:
            network = "TRON"
            data = get_tron_data(address)

        elif (address.startswith("1") or address.startswith("3") or address.startswith("bc1")):
            network = "Bitcoin"
            data = get_btc_data(address)

        elif address.startswith("r") and len(address) >= 25:
            network = "XRP"
            data = get_xrp_data(address)

        elif address.startswith("H") and len(address) > 10:
            network = "Hedera"
            data = get_hedera_data(address)

        elif address.endswith(".sol") or len(address) in [32, 44]:
            network = "Solana"
            data = get_sol_data(address)

        elif address.startswith("bnb") or address[0:2] == "0x":
            network = "BSC"
            data = get_bsc_data(address)

        else:
            return {
                "address": address,
                "network": "Unknown",
                "balance": 0,
                "ai_score": 0,
                "reason": "Unsupported or invalid wallet format.",
                "wallet_age": 0,
                "tx_count": 0,
                "last5tx": []
            }

        ai_score, reason = calculate_risk_score(data)

        result = {
            "address": address,
            "network": network,
            "balance": data.get("balance", 0),
            "ai_score": ai_score,
            "reason": reason,
            "wallet_age": data.get("wallet_age", 0),
            "tx_count": data.get("tx_count", 0),
            "last5tx": data.get("last5tx", [])
        }

        return result

    except Exception as e:
        return {
            "address": address,
            "network": "Unknown",
            "balance": 0,
            "ai_score": 0,
            "reason": f"System error: {str(e)}",
            "wallet_age": 0,
            "tx_count": 0,
            "last5tx": []
        }
