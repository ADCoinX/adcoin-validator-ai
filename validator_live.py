
import requests

ETHERSCAN_API_KEY = 'QZ2IEY7FFB5DVPMCYA5FCH2BQIYG4QSTHH'

def check_wallet_status(address):
    if address.startswith("0x") and len(address) == 42:
        try:
            balance_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey={ETHERSCAN_API_KEY}"
            tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"

            balance_res = requests.get(balance_url).json()
            tx_res = requests.get(tx_url).json()

            if balance_res['status'] != '1':
                return {'status': '❌ Address not found or invalid'}

            balance_eth = int(balance_res['result']) / 1e18
            tx_list = tx_res.get('result', [])[:5]
            transactions = [f"{tx['from']} → {tx['to']} | {int(tx['value'])/1e18:.4f} ETH" for tx in tx_list]

            return {
                'status': '✅ Valid Ethereum Wallet',
                'balance': f"{balance_eth:.6f} ETH",
                'tokens': ['(ERC-20 token list coming soon)'],
                'transactions': transactions if transactions else ['No recent transactions']
            }
        except Exception as e:
            return {'status': f'❌ Error: {str(e)}'}

    elif address.startswith("T") and len(address) == 34:
        return {
            'status': '✅ Valid TRON Wallet (TRONGRID API not yet wired)',
            'balance': 'LIVE soon',
            'tokens': [],
            'transactions': []
        }
    elif address.startswith("bc1") or address.startswith("1") or address.startswith("3"):
        return {
            'status': '✅ Valid Bitcoin Wallet (blockchain info coming)',
            'balance': 'LIVE soon',
            'tokens': [],
            'transactions': []
        }
    else:
        return {'status': '❌ Invalid or Unsupported Wallet Address'}
