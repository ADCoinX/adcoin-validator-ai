from flask import Flask, render_template, request, send_file, flash
from api_handler import get_wallet_data
from iso_export import generate_iso_xml
import io
import os
import logging

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Untuk flash message, ganti dengan secret sebenar kalau production

logging.basicConfig(level=logging.DEBUG)  # Tambah logging untuk debug

def read_user_count():
    count_file = os.path.join('static', 'user_count.txt')
    try:
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                count = int(f.read().strip())
        else:
            count = 0
    except Exception as e:
        logging.error(f"Error reading user count: {e}")
        count = 0
    return count

def update_user_count():
    count_file = os.path.join('static', 'user_count.txt')
    try:
        count = read_user_count()
        count += 1
        with open(count_file, 'w') as f:
            f.write(str(count))
    except Exception as e:
        logging.error(f"Error updating user count: {e}")
        count = 0
    return count

@app.route('/', methods=['GET', 'POST'])
def home():
    result = {}
    user_count = read_user_count()  # Baca count dulu setiap load page
    if request.method == 'POST':
        address = request.form['wallet'].strip()
        if not address:
            flash("❌ Sila masukkan wallet address yang valid!")
        else:
            try:
                result = get_wallet_data(address)
                logging.debug(f"Result dari API: {result}")  # Debug result
                if 'status' in result and result['status'] == "0":
                    flash(result.get('message', '❌ Error tidak diketahui!') + ' ' + result.get('result', ''))
                    result = {}
                elif 'reason' in result and result['reason'].startswith('❌'):
                    flash(result['reason'])
                    result = {}
                else:
                    user_count = update_user_count()  # Update count bila success
            except Exception as e:
                logging.error(f"Error dalam get_wallet_data: {e}")
                flash("❌ Terjadi error semasa validate wallet. Cuba lagi!")
                result = {}
    return render_template('index.html', result=result, user_count=user_count)

@app.route('/export-iso')
def export_iso():
    wallet = request.args.get("wallet")
    if not wallet:
        flash("❌ Wallet address diperlukan untuk export!")
        return redirect('/')
    xml_data = generate_iso_xml(wallet)
    return send_file(
        io.BytesIO(xml_data.encode()),
        mimetype='application/xml',
        as_attachment=True,
        download_name=f'{wallet}_iso20022.xml'
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port, debug=True)  # Debug=True untuk tengok error mudah
