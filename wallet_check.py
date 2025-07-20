import requests

def ai_risk_score(balance, tx_count):
    if balance == 0 and tx_count == 0:
        return "Safe", True
    elif balance < 0.01 and tx_count < 3:
        return "Medium", True
    elif tx_count >= 10:
        return "High Risk", False
    else:
        return "Unknown", True

def check_wallet(address):
    result = {
        "network": "Unknown",
        "balance": "-",
        "status": "Not Detected",
        "risk_score": "-",
        "safe": True,
        "last_tx": []
    }

    ### ETH via Ethplorer (public API key)
    if address.startswith("0x") and len(address) == 42:
        result["network"] = "Ethereum"
        try:
            r = requests.get(f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey")
            data = r.json()
            bal = float(data.get("ETH", {}).get("balance", 0))
            tx_list = data.get("operations", [])[:10]
            result["balance"] = f"{bal:.5f} ETH"
            result["last_tx"] = [{"hash": tx["transactionHash"], "value": tx["value"], "to": tx["to"]} for tx in tx_list]
            result["status"] = "Active" if bal > 0 else "Empty"
            result["risk_score"], result["safe"] = ai_risk_score(bal, len(tx_list))
        except:
            result["status"] = "Error"

    ### TRON via Tronscan (no key)
    elif address.startswith("T"):
        result["network"] = "TRON"
        try:
            r = requests.get(f"https://apilist.tronscanapi.com/api/account?address={address}")
            data = r.json()
            bal = int(data.get("balance", 0)) / 1e6
            result["balance"] = f"{bal:.2f} TRX"
            result["status"] = "Active" if bal > 0 else "Empty"
            result["risk_score"], result["safe"] = ai_risk_score(bal, 0)
        except:
            result["status"] = "Error"

    ### BTC via Blockchair
    elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        result["network"] = "Bitcoin"
        try:
            r = requests.get(f"https://api.blockchair.com/bitcoin/dashboards/address/{address}")
            data = r.json()["data"][address]
            bal = int(data["address"]["balance"]) / 1e8
            result["balance"] = f"{bal:.8f} BTC"
            txs = data["transactions"][:10]
            result["last_tx"] = [{"hash": tx} for tx in txs]
            result["status"] = "Active" if bal > 0 else "Empty"
            result["risk_score"], result["safe"] = ai_risk_score(bal, len(txs))
        except:
            result["status"] = "Error"

    ### BSC via BscScan clone (limited public)
    elif address.startswith("0x") and len(address) == 42:
        result["network"] = "Binance Smart Chain"
        try:
            r = requests.get(f"https://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock=1&endblock=99999999&sort=desc")
            data = r.json()
            txs = data.get("result", [])[:10]
            result["last_tx"] = [{"hash": tx["hash"], "value": int(tx["value"]) / 1e18} for tx in txs]
            result["balance"] = "-"
            result["status"] = "Active"
            result["risk_score"], result["safe"] = ai_risk_score(0, len(txs))
        except:
            result["status"] = "Error"

    ### Solana via SolanaFM or public RPC
    elif 32 <= len(address) <= 44:
        result["network"] = "Solana"
        try:
            r = requests.post("https://api.mainnet-beta.solana.com", json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [address]
            })
            data = r.json()
            lamports = int(data["result"]["value"])
            sol = lamports / 1e9
            result["balance"] = f"{sol:.5f} SOL"
            result["status"] = "Active" if sol > 0 else "Empty"
            result["risk_score"], result["safe"] = ai_risk_score(sol, 0)
        except:
            result["status"] = "Error"

    ### XRP via XRPScan
    elif address.startswith("r") and len(address) >= 25:
        result["network"] = "XRP"
        try:
            r = requests.get(f"https://api.xrpscan.com/api/v1/account/{address}")
            data = r.json()
            bal = float(data.get("xrpBalance", 0))
            result["balance"] = f"{bal:.2f} XRP"
            result["status"] = "Active" if bal > 0 else "Empty"
            result["risk_score"], result["safe"] = ai_risk_score(bal, 0)
        except:
            result["status"] = "Error"

    return result