# Contoh senarai hitam. Boleh sambung dari file / API nanti.
BLACKLISTED_WALLETS = [
    "0x000000000000000000000000000000000000dead",
    "TQooBX9o8iSSprLWW96YShBogx7Uwisuim",
    "bc1qscamwallet123456...",
    "rScamXRPwallet1234..."
]

def is_blacklisted(address):
    return address in BLACKLISTED_WALLETS
