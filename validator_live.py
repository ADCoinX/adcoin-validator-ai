
import os

ETHERSCAN_API = os.getenv("ETHERSCAN_API")

def validate_wallet(address):
    if address.startswith("0x"):
        return validate_eth_arb_bsc_optimism_polygon(address)
    elif address.startswith("T"):
        return validate_tron(address)
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        return validate_btc(address)
    elif address.startswith("r"):
        return validate_xrp(address)
    elif address.startswith("addr1"):
        return validate_cardano(address)
    else:
        return "❌ Unsupported wallet format"

def ai_score(balance, tx_count=0):
    score = 0
    if balance == 0:
        score += 40
    if tx_count < 5:
        score += 20
    if score >= 70:
        risk = "⚠️ HIGH RISK"
    elif score >= 40:
        risk = "⚠️ MEDIUM RISK"
    else:
        risk = "🛡️ LOW RISK"
    return f"<br><b>🧠 AI Score:</b> {score}/100<br>{risk}"

def validate_eth_arb_bsc_optimism_polygon(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API}"
    tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&apikey={ETHERSCAN_API}"
    r1 = requests.get(url).json()
    r2 = requests.get(tx_url).json()
    if r1["status"] == "1":
        bal = int(r1["result"]) / 1e18
        tx = len(r2.get("result", []))
        return f"✅ ETH/BSC/Polygon/Arbitrum/Optimism | Balance: {bal:.4f} | Tx: {tx}" + ai_score(bal, tx)
    return "❌ Failed to fetch EVM wallet"

def validate_tron(address):
    r = requests.get(f"https://api.trongrid.io/v1/accounts/{address}").json()
    if "data" in r and len(r["data"]) > 0:
        b = int(r["data"][0].get("balance", 0)) / 1e6
        tx = r["data"][0].get("total_transaction_count", 0)
        return f"✅ TRON | Balance: {b:.2f} TRX | Tx: {tx}" + ai_score(b, tx)
    return "❌ Failed TRON"

def validate_btc(address):
    r = requests.get(f"https://blockstream.info/api/address/{address}").json()
    ch = r.get("chain_stats", {})
    b = ch.get("funded_txo_sum", 0) - ch.get("spent_txo_sum", 0)
    tx = ch.get("tx_count", 0)
    btc = b / 1e8
    return f"✅ BTC | Balance: {btc:.8f} BTC | Tx: {tx}" + ai_score(btc, tx)

def validate_xrp(address):
    r = requests.get(f"https://api.xrpscan.com/api/v1/account/{address}").json()
    bal = float(r.get("balance", 0))
    return f"✅ XRP | Balance: {bal:.4f} XRP" + ai_score(bal)

def validate_cardano(address):
    return "✅ Cardano detected (Coming soon with Blockfrost API)"
