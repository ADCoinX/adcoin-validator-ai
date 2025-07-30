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
        address = request.form['wallet'].strip()
        result = get_wallet_data(address)
        log_user(address, result.get("network", "Unknown"))
    return render_template('index.html', result=result)

@app.route('/export-iso')
def export_iso():
    wallet = request.args.get("wallet")
    xml_data = generate_iso_xml(wallet)
    return send_file(io.BytesIO(xml_data.encode()), mimetype='application/xml',
                     as_attachment=True, download_name=f'{wallet}_iso20022.xml')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port)
