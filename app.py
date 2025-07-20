from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ ADC CryptoGuard is live & running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)# Placeholder for app.py
