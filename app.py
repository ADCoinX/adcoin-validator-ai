from flask import Flask, render_template, request
import os
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/result', methods=['POST'])
def result():
    address = request.form['address']
    is_valid = address.startswith('0x') and len(address) == 42
    return render_template('result.html', address=address, result="Valid ✅" if is_valid else "Invalid ❌")
if __name__ == '__main__':
    app.run()
