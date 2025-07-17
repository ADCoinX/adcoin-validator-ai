
from flask import Flask, render_template, request
from validator_live import validate_wallet

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        address = request.form["wallet"]
        result = validate_wallet(address)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run()
