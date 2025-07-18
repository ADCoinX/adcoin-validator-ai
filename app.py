
from flask import Flask, render_template, request
from validator_live import validate_wallet

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
  if request.method == 'POST':
    address = request.form.get('address', '').strip()
    if not address:
        return render_template('index.html', wallet_info="No wallet entered.", status="Invalid")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
