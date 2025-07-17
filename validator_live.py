
def validate_wallet(address):
    if address.startswith("0x"):
        return f"✅ ETH Wallet Detected: {address[:8]}..."
    elif address.startswith("T"):
        return f"✅ TRON Wallet Detected: {address[:8]}..."
    elif address.startswith("bc1") or address.startswith("1") or address.startswith("3"):
        return f"✅ BTC Wallet Detected: {address[:8]}..."
    elif address.startswith("r"):
        return f"✅ XRP Wallet Detected: {address[:8]}..."
    elif len(address) > 20:
        return f"✅ Possible Solana Wallet Detected: {address[:8]}..."
    else:
        return "❌ Invalid or unsupported wallet format."
