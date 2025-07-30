# blacklist.py

def is_blacklisted(address):
    # Senarai alamat yang disenarai hitam
    blacklist = [
        "0xScamExample1234567890",
        "TScammer987654321",
        "1FAKESCAMBTC123456",
        "TQWF3xEn44UrAS9a2bn7LKNssb1UbDeAx6",
        "TQooBX9o8iSSprLWW96YShBogx7Uwisuim"
    ]
    return address.strip() in blacklist
