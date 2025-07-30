from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
from api_handler import get_wallet_data
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml
import os
import io
from datetime import datetime

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    user_count = "LIVE"  # Dummy placeholder if not using Google Sheet

    if request.method == "POST":
        address = request.form["wallet"].strip()
        result["address"] = address

        user_ip = request.remote_addr
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("user_log.txt", "a") as f:
            f.write(f"{timestamp} | {user_ip} | {address}\n")

        try:
            result["network"], wallet_data = get_wallet_data(address)
            result["user_count"] = user_count

            if wallet_data:
                result["balance"] = wallet_data.get("balance")
                result["tx_count"] = wallet_data.get("tx_count")
                result["wallet_age"] = wallet_data.get("wallet_age")
                result["last5tx"] = wallet_data.get("last5tx", [])
                result["ai_score"], result["reason"] = calculate_risk_score(wallet_data)
            else:
                result["error"] = "Wallet not found or API error."

        except Exception as e:
            result["error"] = f"❌ Error: {str(e)}"

    return render_template("index.html", result=result, user_count=user_count)

@app.route("/export-iso", methods=["GET"])
def export_iso():
    wallet = request.args.get("wallet")
    network, wallet_data = get_wallet_data(wallet)

    balance = wallet_data.get("balance") if wallet_data else "N/A"
    xml_data = generate_iso_xml(wallet, network, balance)

    return send_file(
        io.BytesIO(xml_data.encode()),
        mimetype='application/xml',
        as_attachment=True,
        download_name=f"{wallet}_ISO20022.xml"
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
