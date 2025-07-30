from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
from api_handler import get_wallet_data
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml
import os
import io
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()
app = Flask(__name__)

# ✅ Guna ENV dari Render (JSON string)
def get_unique_user_count():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")  # ✅ DULU salah: GOOGLE_APPLICATION_CREDENTIALS_JSON
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("ADC_CryptoGuard_logs").sheet1

        data = sheet.get_all_records()
        unique_ips = set()

        for row in data:
            if 'IP' in row:
                unique_ips.add(row['IP'])

        return len(unique_ips)
    except Exception as e:
        print(f"❌ Error getting user count: {e}")
        return 0

@app.route("/", methods=["GET", "POST"])
def home():
    result = {}
    user_count = get_unique_user_count()

    if request.method == "POST":
        address = request.form["wallet"].strip()
        result["address"] = address

        user_ip = request.remote_addr
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("user_log.txt", "a") as f:
            f.write(f"{timestamp} | {user_ip} | {address}\n")

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

    return render_template("index.html", result=result, user_count=user_count)

@app.route("/export-iso", methods=["GET"])
def export_iso():
    wallet = request.args.get("wallet")
    network, wallet_data = get_wallet_data(wallet)

    if wallet_data:
        balance = wallet_data.get("balance")
    else:
        balance = "N/A"

    xml_data = generate_iso_xml(wallet, network, balance)
    return send_file(io.BytesIO(xml_data.encode()), mimetype='application/xml',
                     as_attachment=True, download_name=f"{wallet}_ISO20022.xml")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
