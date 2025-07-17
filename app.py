
from flask import Flask, request, render_template
from validator import validate_wallet

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        wallet = request.form.get("wallet")
        result = validate_wallet(wallet)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
