from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from api_handler import get_wallet_data, is_wallet_format_ok
from iso_export import generate_iso_xml
import io
import os

ERROR_PREFIX = "❌"
ERR_INVALID_WALLET = f"{ERROR_PREFIX} Sila masukkan wallet address yang valid!"
ERR_UNKNOWN = f"{ERROR_PREFIX} Error tidak diketahui!"
ERR_VALIDATE = f"{ERROR_PREFIX} Terjadi error semasa validate wallet. Cuba lagi!"
ERR_EXPORT_NEED_WALLET = f"{ERROR_PREFIX} Wallet address diperlukan untuk export!"

USER_COUNT_FILE = os.path.join('static', 'user_count.txt')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super_secret_key')

def read_user_count() -> int:
    try:
        if not os.path.exists(USER_COUNT_FILE):
            os.makedirs(os.path.dirname(USER_COUNT_FILE), exist_ok=True)
            with open(USER_COUNT_FILE, 'w') as f:
                f.write("0")
            return 0
        with open(USER_COUNT_FILE, 'r') as f:
            return int((f.read() or "0").strip())
    except (ValueError, OSError):
        return 0

def update_user_count() -> int:
    try:
        count = read_user_count() + 1
        with open(USER_COUNT_FILE, 'w') as f:
            f.write(str(count))
        return count
    except OSError:
        return read_user_count()

@app.route('/', methods=['GET', 'POST'])
def home():
    result = {}
    user_count = read_user_count()

    if request.method == 'POST':
        address = (request.form.get('wallet') or "").strip()
        if not address or not is_wallet_format_ok(address):
            flash(ERR_INVALID_WALLET)
            return redirect(url_for('home'))

        try:
            result = get_wallet_data(address)

            if (isinstance(result, dict) and (
                result.get('status') == "0" or
                result.get('error') or
                (isinstance(result.get('reason'), str) and result['reason'].startswith(ERROR_PREFIX))
            )):
                msg = result.get('message') or result.get('reason') or result.get('error') or ERR_UNKNOWN
                extra = result.get('result')
                flash(f"{msg}{(' ' + extra) if extra else ''}")
                return redirect(url_for('home'))

            update_user_count()
            return render_template('index.html', result=result, user_count=read_user_count())

        except Exception:
            flash(ERR_VALIDATE)
            return redirect(url_for('home'))

    return render_template('index.html', result=result, user_count=user_count)

@app.route('/export-iso')
def export_iso():
    wallet = (request.args.get("wallet") or "").strip()
    if not wallet or not is_wallet_format_ok(wallet):
        flash(ERR_EXPORT_NEED_WALLET)
        return redirect(url_for('home'))

    safe_name = secure_filename(wallet)[:80] or "wallet"
    xml_data = generate_iso_xml(wallet)
    return send_file(
        io.BytesIO(xml_data.encode('utf-8')),
        mimetype='application/xml',
        as_attachment=True,
        download_name=f'{safe_name}_iso20022.xml'
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port, debug=True)
