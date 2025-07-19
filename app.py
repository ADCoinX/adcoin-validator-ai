
from flask import Flask, render_template, request
import re

app = Flask(__name__)

patterns = {
    'BTC': r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$',
    'ETH': r'^0x[a-fA-F0-9]{40}$',
    'TRX': r'^T[a-zA-Z0-9]{33}$',
    'XRP': r'^r[0-9a-zA-Z]{24,34}$',
    'LTC': r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$',
    'DOGE': r'^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$'
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    if request.method == "POST":
        address = request.form["address"]
        coin_type = request.form["coin_type"]
        regex = patterns.get(coin_type)
        if regex:
            is_valid = re.match(regex, address) is not None
            result["status"] = "Valid" if is_valid else "Invalid"
            result["address"] = address
            result["coin_type"] = coin_type
        else:
            result["status"] = "Unsupported"
    return render_template("index.html", result=result)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
