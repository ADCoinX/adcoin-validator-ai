
from flask import Flask, request, render_template
from validator_live import check_wallet_status

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        wallet = request.form.get("wallet")
        result = check_wallet_status(wallet)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
