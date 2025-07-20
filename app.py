from flask import Flask, render_template, request
from wallet_check import check_wallet

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        address = request.form["address"]
        result = check_wallet(address)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
