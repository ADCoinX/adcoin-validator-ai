from flask import Flask, render_template, request, send_file
from get_eth_data import get_eth_data
from get_btc_data import get_btc_data
from get_tron_data import get_tron_data
from get_xrp_data import get_xrp_data
from get_solana_data import get_solana_data
from get_hedera_data import get_hedera_data
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = {}
    if request.method == 'POST':
        address = request.form['wallet'].strip()
        try:
            if address.startswith("0x") and len(address) == 42:
                result = get_eth_data(address)
            elif address.startswith("T") and len(address) >= 34:
                result = get_tron_data(address)
            elif address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
                result = get_btc_data(address)
            elif address.startswith("r") and len(address) >= 25:
                result = get_xrp_data(address)
            elif len(address) == 44 and address.endswith("=="):
                result = get_solana_data(address)
            elif address.startswith("0.") or address.startswith("1."):
                result = get_hedera_data(address)
            else:
                result = {
                    "wallet": address,
                    "network": "Unknown",
                    "balance": 0,
                    "tx_count": 0,
                    "wallet_age": 0,
                    "error": "Unsupported wallet address format."
                }

            score, reason = calculate_risk_score(result)
            result["ai_score"] = score
            result["ai_reason"] = reason

        except Exception as e:
            result = {
                "wallet": address,
                "network": "Unknown",
                "balance": 0,
                "tx_count": 0,
                "wallet_age": 0,
                "ai_score": 0,
                "ai_reason": f"Error: {str(e)}"
            }

    return render_template('index.html', result=result)

@app.route('/export-iso')
def export_iso():
    wallet = request.args.get("wallet")
    xml_data = generate_iso_xml(wallet)
    return send_file(io.BytesIO(xml_data.encode()), mimetype='application/xml',
                     as_attachment=True, download_name=f'{wallet}_iso20022.xml')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
