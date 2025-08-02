from flask import Flask, render_template, request, send_file
from api_handler import get_wallet_data
from iso_export import generate_iso_xml
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = {}
    if request.method == 'POST':
        address = request.form.get('wallet', '').strip()
        if address:
            try:
                result = get_wallet_data(address)
            except Exception as e:
                result = {
                    "address": address,
                    "network": "Unknown",
                    "balance": 0,
                    "ai_score": 0,
                    "reason": f"System error: {str(e)}",
                    "wallet_age": 0,
                    "tx_count": 0,
                    "last5tx": [],
                    "blacklisted": False
                }
    return render_template('index.html', result=result)

@app.route('/export-iso')
def export_iso():
    wallet = request.args.get("wallet", "")
    if not wallet:
        return "Invalid wallet", 400
    try:
        xml_data = generate_iso_xml(wallet)
        return send_file(
            io.BytesIO(xml_data.encode()),
            mimetype='application/xml',
            as_attachment=True,
            download_name=f'{wallet}_iso20022.xml'
        )
    except Exception as e:
        return f"Failed to export XML: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port)
