from flask import Flask, render_template, request, send_file
from api_handler import get_wallet_data
from iso_export import generate_iso_xml
import io
import os

app = Flask(__name__)

DEFAULT_RESULT = {
    "address": "",
    "network": "Unknown",
    "balance": 0,
    "ai_score": 0,
    "reason": "",
    "wallet_age": 0,
    "tx_count": 0,
    "last5tx": [],
}

@app.route('/', methods=['GET', 'POST'])
def home():
    result = DEFAULT_RESULT.copy()
    if request.method == 'POST':
        address = request.form.get('wallet', '').strip()
        if address:
            try:
                result = get_wallet_data(address)
                # Guarantee semua field wujud, elak crash UI
                for k, v in DEFAULT_RESULT.items():
                    if k not in result:
                        result[k] = v
            except Exception as e:
                print(f"[ERROR] get_wallet_data: {str(e)}")
                result = DEFAULT_RESULT.copy()
                result["address"] = address
                result["reason"] = f"System error: {str(e)}"
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
        print(f"[ERROR] export-iso: {str(e)}")
        return f"Failed to export XML: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port)
