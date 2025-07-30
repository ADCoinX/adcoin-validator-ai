# blacklist.py

def is_blacklisted(address):
    # Senarai alamat yang disenarai hitam
    blacklist = [
        "0xScamExample1234567890",
        "TScammer987654321",
        "1FAKESCAMBTC123456"
    ]
    return address.strip() in blacklist
