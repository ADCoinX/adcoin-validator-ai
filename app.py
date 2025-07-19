{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from flask import Flask, request, render_template\
import requests\
import os\
from dotenv import load_dotenv\
from sklearn.ensemble import IsolationForest\
import pandas as pd\
\
app = Flask(__name__)\
load_dotenv()\
\
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')\
\
def check_ethereum_balance(address):\
    if not ETHERSCAN_API_KEY:\
        return \{"error": "No API key available"\}\
    url = f"https://api.etherscan.io/api?module=account&action=balance&address=\{address\}&tag=latest&apikey=\{ETHERSCAN_API_KEY\}"\
    response = requests.get(url).json()\
    if response['status'] == '1':\
        return float(response['result']) / 1e18  # Convert wei to ETH\
    return \{"error": "Invalid address or error"\}\
\
def get_ethereum_transactions(address):\
    if not ETHERSCAN_API_KEY:\
        return []\
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address=\{address\}&startblock=0&endblock=99999999&sort=desc&limit=5&apikey=\{ETHERSCAN_API_KEY\}"\
    response = requests.get(url).json()\
    if response['status'] == '1':\
        return response['result'][:5]  # Get the latest 5 transactions\
    return []\
\
def ai_risk_scoring(transactions):\
    if not transactions:\
        return []\
    features = [[float(tx.get('value', 0)) / 1e18 for tx in transactions]]\
    model = IsolationForest(contamination=0.2, random_state=42)\
    model.fit(features)\
    scores = model.predict(features)\
    return [\{'tx': tx, 'risk': 'High' if score == -1 else 'Low'\} for tx, score in zip(transactions, scores)]\
\
@app.route('/')\
def index():\
    return render_template('index.html')\
\
@app.route('/validate', methods=['POST'])\
def validate():\
    data = request.json\
    address = data.get('address')\
    if not address:\
        return \{"error": "Please enter a wallet address"\}, 400\
    balance = check_ethereum_balance(address)\
    transactions = get_ethereum_transactions(address)\
    risk_scores = ai_risk_scoring(transactions)\
    return \{\
        "address": address,\
        "balance": balance if isinstance(balance, (int, float)) else balance.get('error'),\
        "transactions": transactions,\
        "risk_scores": risk_scores\
    \}\
\
if __name__ == '__main__':\
    app.run(debug=True)}