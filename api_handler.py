from __future__ import annotations
import time
import re
from typing import Any, Dict, List, Optional
import requests
from urllib.parse import quote
from requests.exceptions import RequestException, Timeout

API_REJECTED = "❌ API rejected"
NETWORK_TIMEOUT = 12

WALLET_PATTERNS = [
    re.compile(r"^0x[a-fA-F0-9]{40}$"),                     # ETH/EVM
    re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$"),             # TRON
    re.compile(r"^(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$"),  # BTC
    re.compile(r"^r[1-9A-HJ-NP-Za-km-z]{24,}$"),            # XRP
    re.compile(r"^[1-9A-HJ-NP-Za-km-z]{44}$"),              # SOL
    re.compile(r"^0\.0\.\d+$"),                             # HBAR
]

def is_wallet_format_ok(addr: str) -> bool:
    return any(p.fullmatch(addr) for p in WALLET_PATTERNS)

def _http_get_json(url: str, params: dict | None = None, timeout: int = NETWORK_TIMEOUT) -> Dict[str, Any]:
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Timeout as e:
        return {"error": f"timeout: {e}"}
    except RequestException as e:
        return {"error": f"network: {e}"}
    except ValueError as e:
        return {"error": f"json: {e}"}

def _http_post_json(url: str, payload: dict, timeout: int = NETWORK_TIMEOUT) -> Dict[str, Any]:
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Timeout as e:
        return {"error": f"timeout: {e}"}
    except RequestException as e:
        return {"error": f"network: {e}"}
    except ValueError as e:
        return {"error": f"json: {e}"}

def _wei_to_eth(wei_hex_or_int: Any) -> float:
    try:
        if isinstance(wei_hex_or_int, str):
            val = int(wei_hex_or_int, 16)
        else:
            val = int(wei_hex_or_int)
        return val / 10**18
    except Exception:
        return 0.0

def _lamports_to_sol(lamports: int) -> float:
    try:
        return int(lamports) / 10**9
    except Exception:
        return 0.0

def _hbar_tinybars_to_hbar(tinybars: int) -> float:
    try:
        return int(tinybars) / 10**8
    except Exception:
        return 0.0

def _score(ai_inputs: Dict[str, Any]) -> int:
    tx = int(ai_inputs.get("tx_count") or 0)
    age_days = float(ai_inputs.get("wallet_age") or 0.0)
    bal = float(ai_inputs.get("balance") or 0.0)

    score = 50
    score += min(20, age_days / 30)
    score += min(20, max(0, 5 - tx))
    if tx > 100: score -= 10
    if bal == 0: score -= 10
    return max(0, min(100, round(score)))

def _normalize_result(address: str, network: str, balance: float = 0.0,
                      tx_count: int = 0, wallet_age_days: float = 0.0,
                      last5tx: Optional[List[Dict[str, Any]]] = None,
                      reason: str = "OK") -> Dict[str, Any]:
    return {
        "address": address,
        "network": network,
        "balance": balance,
        "tx_count": tx_count,
        "wallet_age": round(wallet_age_days, 2) if wallet_age_days else 0,
        "last5tx": last5tx or [],
        "reason": reason,
        "ai_score": _score({"tx_count": tx_count, "wallet_age": wallet_age_days, "balance": balance})
    }

# ---------- ETH / EVM ----------
def fetch_eth(address: str) -> Dict[str, Any]:
    rpcs = [
        "https://cloudflare-eth.com",
        "https://rpc.ankr.com/eth",
        "https://ethereum.publicnode.com",
        "https://rpc.flashbots.net",
        "https://eth-mainnet.public.blastapi.io",
    ]
    nonce = None
    balance = None
    for rpc in rpcs:
        r1 = _http_post_json(rpc, {"jsonrpc":"2.0","id":1,"method":"eth_getBalance","params":[address, "latest"]})
        if not r1.get("error") and r1.get("result"):
            balance = _wei_to_eth(r1["result"])
        r2 = _http_post_json(rpc, {"jsonrpc":"2.0","id":2,"method":"eth_getTransactionCount","params":[address, "latest"]})
        if not r2.get("error") and r2.get("result"):
            try:
                nonce = int(r2["result"], 16)
            except Exception:
                pass
        if balance is not None and nonce is not None:
            break
    if balance is None and nonce is None:
        return {"status": "0", "message": API_REJECTED}
    return _normalize_result(address, "Ethereum", balance=balance or 0.0, tx_count=nonce or 0)

# ---------- BTC ----------
def fetch_btc(address: str) -> Dict[str, Any]:
    safe_addr = quote(address, safe="")
    endpoints = [
        f"https://blockchain.info/rawaddr/{safe_addr}",
        f"https://blockstream.info/api/address/{safe_addr}",
        f"https://api.blockcypher.com/v1/btc/main/addrs/{safe_addr}",
        f"https://api.blockchair.com/bitcoin/dashboards/address/{safe_addr}",
        f"https://mempool.space/api/address/{safe_addr}",
    ]
    data = {}
    for url in endpoints:
        data = _http_get_json(url)
        if data and not data.get("error"):
            break
    if not data or data.get("error"):
        return {"status": "0", "message": API_REJECTED}

    balance = 0.0
    tx_count = 0
    last5tx = []

    if "final_balance" in data or "n_tx" in data:
        balance = (data.get("final_balance") or 0)/1e8
        tx_count = data.get("n_tx") or 0
        txs = data.get("txs") or []
        for tx in txs[:5]:
            h = tx.get("hash") or ""
            t = tx.get("time")
            if t: t = time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))
            last5tx.append({"hash": h, "time": t, "from": "-", "to": "-", "value": "-"})
    elif "chain_stats" in data:
        bal_sat = (data["chain_stats"].get("funded_txo_sum", 0) - data["chain_stats"].get("spent_txo_sum", 0))
        balance = max(0, bal_sat)/1e8
        tx_count = data["chain_stats"].get("tx_count", 0)
    elif "data" in data and isinstance(data["data"], dict):
        dash = (data["data"].get(address) or {}).get("address", {})
        balance = (dash.get("balance") or 0)/1e8
        tx_count = dash.get("transaction_count") or 0
    elif "balance" in data and "final_n_tx" in data:
        balance = (data.get("final_balance") or data.get("balance") or 0)/1e8
        tx_count = data.get("final_n_tx") or data.get("n_tx") or 0

    return _normalize_result(address, "Bitcoin", balance=balance, tx_count=tx_count, last5tx=last5tx)

# ---------- TRON ----------
def fetch_tron(address: str) -> Dict[str, Any]:
    safe_addr = quote(address, safe="")
    endpoints = [
        f"https://apilist.tronscanapi.com/api/account?address={safe_addr}",
        f"https://apilist.trongrid.io/v1/accounts/{safe_addr}",
        f"https://apilist.tronscan.org/api/account?address={safe_addr}",
        f"https://apilist.trongrid.io/v1/accounts/{safe_addr}/transactions",
        f"https://tronscan.org/api/accountv2?address={safe_addr}",
    ]
    data = {}
    for url in endpoints:
        data = _http_get_json(url)
        if data and not data.get("error"):
            break
    if not data or data.get("error"):
        return {"status": "0", "message": API_REJECTED}

    balance = 0.0
    tx_count = 0
    last5tx: List[Dict[str, Any]] = []

    if "balance" in data:
        try:
            balance = float(data.get("balance") or 0)
        except Exception:
            balance = 0.0
    elif "data" in data and isinstance(data["data"], list) and data["data"]:
        acc = data["data"][0]
        balance = float(acc.get("balance", 0))/1e6 if isinstance(acc.get("balance"), (int, float)) else 0.0

    txs = data.get("tokenTransferTxs") or data.get("transaction") or data.get("data") or []
    if isinstance(txs, list):
        tx_count = len(txs)
        for tx in txs[:5]:
            h = tx.get("hash") or tx.get("txID") or ""
            t = tx.get("timestamp") or tx.get("block_timestamp")
            if t and isinstance(t, (int, float)):
                t = time.strftime("%Y-%m-%d %H:%M", time.gmtime(t/1000 if t > 1e12 else t))
            last5tx.append({
                "hash": h,
                "time": t,
                "from": tx.get("transferFromAddress") or "-",
                "to": tx.get("transferToAddress") or "-",
                "value": tx.get("amount") or "-"
            })

    return _normalize_result(address, "TRON", balance=balance, tx_count=tx_count, last5tx=last5tx)

# ----------------------------
# XRP FETCH — gunakan rippled JSON-RPC (balance tepat) + Ripple Data API (age/tx)
# ----------------------------
def fetch_xrp(address: str) -> Dict[str, Any]:
    from urllib.parse import quote
    import time
    safe_addr = quote(address, safe="")

    # 1) Dapatkan BALANCE melalui rippled JSON-RPC (public nodes — tiada API key)
    rippled_nodes = [
        "https://xrplcluster.com",          # community cluster
        "https://s1.ripple.com:51234/",     # Ripple public
        "https://s2.ripple.com:51234/",     # Ripple public
        "https://xrpl.link/rpc",            # gateway
        "https://rippled.xrpldata.com/"     # community
    ]
    balance = None
    for rpc in rippled_nodes:
        res = _http_post_json(rpc, {
            "method": "account_info",
            "params": [{"account": address, "ledger_index": "validated", "strict": True}]
        })
        if res.get("result") and res["result"].get("status") == "success":
            acct = res["result"].get("account_data") or {}
            bal_drops = acct.get("Balance")
            if bal_drops is not None:
                try:
                    balance = float(bal_drops) / 1_000_000.0  # drops -> XRP
                    break
                except Exception:
                    balance = 0.0

    # Jika semua RPC gagal, cuba Ripple Data API /balances (kadang bagi nilai terus)
    if balance is None:
        resp = _http_get_json(f"https://data.ripple.com/v2/accounts/{safe_addr}/balances")
        if resp and not resp.get("error"):
            try:
                for b in resp.get("balances", []):
                    if b.get("currency") == "XRP":
                        balance = float(b.get("value", 0))
                        break
            except Exception:
                balance = 0.0

    if balance is None:
        # Semua fallback gagal
        return {"status": "0", "message": API_REJECTED}

    # 2) Dapatkan umur & kiraan transaksi (anggaran) dari Ripple Data API (public)
    wallet_age_days = 0.0
    tx_count = 0

    meta = _http_get_json(f"https://data.ripple.com/v2/accounts/{safe_addr}")
    if meta and not meta.get("error"):
        inc = meta.get("inception")
        if inc:
            try:
                secs = int(inc)  # API lazimnya bagi epoch seconds
                wallet_age_days = max(0.0, (time.time() - secs) / 86400.0)
            except Exception:
                pass

    tx_meta = _http_get_json(f"https://data.ripple.com/v2/accounts/{safe_addr}/transactions?limit=1")
    if tx_meta and not tx_meta.get("error"):
        try:
            tx_count = int(tx_meta.get("count") or 0)
        except Exception:
            tx_count = 0

    # 3) (Optional) 5 transaksi terakhir untuk UI
    last5tx = []
    txs = _http_get_json(f"https://data.ripple.com/v2/accounts/{safe_addr}/transactions?result=tesSUCCESS&limit=5")
    if txs and not txs.get("error"):
        for item in (txs.get("transactions") or [])[:5]:
            tx = item.get("tx") or {}
            h = tx.get("hash") or item.get("hash") or ""
            t = item.get("date")
            if isinstance(t, (int, float)):
                t = time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))
            frm = tx.get("Account") or "-"
            to = tx.get("Destination") or "-"
            val = tx.get("Amount")
            if isinstance(val, str) and val.isdigit():  # drops -> XRP
                try:
                    val = f"{(float(val)/1_000_000.0):.6f} XRP"
                except Exception:
                    pass
            last5tx.append({"hash": h, "time": t, "from": frm, "to": to, "value": val or "-"})

    return _normalize_result(
        address, "XRP",
        balance=balance,
        tx_count=tx_count,
        wallet_age_days=wallet_age_days,
        last5tx=last5tx
    )

# ---------- SOL ----------
def fetch_solana(address: str) -> Dict[str, Any]:
    rpcs = [
        "https://api.mainnet-beta.solana.com",
        "https://rpc.ankr.com/solana",
        "https://solana.publicnode.com",
        "https://api.solana.com",
        "https://solana-api.projectserum.com",
    ]
    balance = None
    for rpc in rpcs:
        res = _http_post_json(rpc, {"jsonrpc":"2.0","id":1,"method":"getBalance","params":[address]})
        if not res.get("error") and res.get("result"):
            value = res["result"].get("value")
            if value is not None:
                balance = _lamports_to_sol(value)
                break
    if balance is None:
        return {"status": "0", "message": API_REJECTED}
    return _normalize_result(address, "Solana", balance=balance, tx_count=0)

# ---------- HBAR ----------
def fetch_hbar(address: str) -> Dict[str, Any]:
    safe_addr = quote(address, safe="")
    endpoints = [
        f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{safe_addr}",
        f"https://mainnet-public.mirrornode.hedera.com/api/v1/balances?account.id={safe_addr}",
        f"https://mainnet-public.mirrornode.hedera.com/api/v1/transactions?account.id={safe_addr}",
        f"https://testnet.mirrornode.hedera.com/api/v1/accounts/{safe_addr}",
        f"https://mainnet-public.mirrornode.hedera.com/api/v1/tokens?account.id={safe_addr}",
    ]
    data = {}
    for url in endpoints:
        data = _http_get_json(url)
        if data and not data.get("error"):
            break
    if not data or data.get("error"):
        return {"status": "0", "message": API_REJECTED}

    balance = 0.0
    tx_count = 0

    if "balance" in data and isinstance(data.get("balance"), dict) and "balance" in data["balance"]:
        balance = _hbar_tinybars_to_hbar(data["balance"]["balance"])
    elif "balances" in data and isinstance(data["balances"], list) and data["balances"]:
        balance = _hbar_tinybars_to_hbar((data["balances"][0] or {}).get("balance", 0))

    if "transactions" in data and isinstance(data["transactions"], list):
        tx_count = len(data["transactions"])

    return _normalize_result(address, "Hedera", balance=balance, tx_count=tx_count)

# ---------- Router ----------
def get_wallet_data(address: str) -> Dict[str, Any]:
    if not is_wallet_format_ok(address):
        return {"status": "0", "message": "❌ Invalid wallet format", "result": ""}

    if address.startswith("0x") and len(address) == 42:
        return fetch_eth(address)
    if address.startswith("T") and len(address) == 34:
        return fetch_tron(address)
    if address.startswith(("1", "3", "bc1")):
        return fetch_btc(address)
    if address.startswith("r") and len(address) >= 25:
        return fetch_xrp(address)
    if len(address) == 44 and re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{44}", address):
        return fetch_solana(address)
    if address.startswith("0.0.") and address.count(".") == 2:
        return fetch_hbar(address)

    return {"status": "0", "message": "❌ Chain not recognized"}
