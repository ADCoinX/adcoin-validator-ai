
import re

def validate_wallet(address):
    if address.startswith("0x") and len(address) == 42:
        return "✅ Valid Ethereum/BSC/Polygon wallet"
    elif address.startswith("T") and len(address) == 34:
        return "✅ Valid TRON wallet"
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        return "✅ Valid Bitcoin wallet"
    elif len(address) >= 32 and all(c.isalnum() for c in address):
        return "✅ Valid Solana wallet"
    else:
        return "❌ Unknown or invalid wallet address"
