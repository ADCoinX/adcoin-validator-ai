from flask import Flask, render_template, request, send_file
from api_handler import get_wallet_data
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    if request.method == "POST":
        address = request.form["wallet"].strip()
        network, data = get_wallet_data(address)
        result = {
            "address": address,
            "network": network,
            "balance": f"{data.get('balance', 0):,.6f}",
            "ai_score": data.get("risk_score", 0),
            "reason": data.get("reason", "No data"),
            "wallet_age": data.get("wallet_age", 0),
            "tx_count": data.get("tx_count", 0),
            "last5tx": data.get("last5tx", [])
        }
    return render_template("index.html", result=result)

@app.route("/export-iso")
def export_iso():
    address = request.args.get("wallet", "")
    try:
        with open(f"{address}_iso20022.xml", "rb") as f:
            xml_data = f.read()
        return send_file(
            io.BytesIO(xml_data),
            mimetype="application/xml",
            as_attachment=True,
            download_name=f"{address}_iso20022.xml"
        )
    except FileNotFoundError:
        return "ISO file not found", 404

if __name__ == "__main__":
    app.run(debug=True)
