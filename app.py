# crypto_validator.py (Updated with Enhanced Features)
import re
import json
import requests
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import webbrowser

class CryptoWalletValidator:
    def __init__(self):
        self.load_patterns()
        self.load_scam_database()
        self.load_blacklists()

    def load_patterns(self):
        """Load cryptocurrency regex patterns"""
        self.patterns = {
            'BTC': {'regex': r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$', 'explorer': 'https://blockstream.info/address/'},
            'ETH': {'regex': r'^0x[a-fA-F0-9]{40}$', 'explorer': 'https://etherscan.io/address/'},
            'USDT': {'regex': r'^0x[a-fA-F0-9]{40}$', 'explorer': 'https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7?a='},
            'XRP': {'regex': r'^r[0-9a-zA-Z]{24,34}$', 'explorer': 'https://xrpscan.com/account/'},
            'LTC': {'regex': r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$', 'explorer': 'https://blockchair.com/litecoin/address/'},
            'DOGE': {'regex': r'^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$', 'explorer': 'https://dogechain.info/address/'},
            'TRX': {'regex': r'^T[a-zA-Z0-9]{33}$', 'explorer': 'https://tronscan.org/#/address/'}
        }

    def load_scam_database(self):
        """Load scam database from local file"""
        try:
            with open('data/scam_db.json', 'r') as f:
                self.scam_db = json.load(f)
        except:
            self.scam_db = {'addresses': {}, 'blacklists': []}

    def load_blacklists(self):
        """Load community blacklists"""
        if not os.path.exists('data/blacklists'):
            os.makedirs('data/blacklists')

        self.blacklists = []
        for file in os.listdir('data/blacklists'):
            if file.endswith('.json'):
                with open(f'data/blacklists/{file}') as f:
                    self.blacklists.extend(json.load(f))

    def validate_address(self, address, coin_type):
        """Validate wallet address format"""
        if coin_type not in self.patterns:
            return False, f"Unsupported cryptocurrency: {coin_type}"

        if re.match(self.patterns[coin_type]['regex'], address):
            return True, "Valid address format"
        return False, "Invalid address format"

    def check_safety(self, address):
        """Comprehensive safety check"""
        results = {
            'is_scam': False,
            'details': [],
            'risk_score': 0
        }

        # Check local scam database
        if address in self.scam_db['addresses']:
            results['is_scam'] = True
            results['details'].append(self.scam_db['addresses'][address])
            results['risk_score'] = 100

        # Check blacklists
        for entry in self.blacklists:
            if address.lower() == entry['address'].lower():
                results['is_scam'] = True
                results['details'].append(entry)
                results['risk_score'] = max(results['risk_score'], entry.get('risk_score', 80))

        if not results['is_scam']:
            results['details'].append({"status": "Clean", "description": "No known scam associations"})

        return results

    def get_transaction_sample(self, coin_type):
        """Sample transaction data for demo"""
        samples = {
            'BTC': [
                {"txid": "a1b2c3d4...", "amount": 0.15, "date": "2023-05-15", "direction": "in"},
                {"txid": "e5f6g7h8...", "amount": 0.02, "date": "2023-05-10", "direction": "out"}
            ],
            'ETH': [
                {"txid": "0x9i8j7k6...", "amount": 1.5, "date": "2023-05-12", "direction": "in"},
                {"txid": "0xl5m4n3...", "amount": 0.3, "date": "2023-05-08", "direction": "out"}
            ]
        }
        return samples.get(coin_type, [])

class ValidatorApp:
    def __init__(self, root):
        self.root = root
        self.validator = CryptoWalletValidator()
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface"""
        self.root.title("Crypto Shield Validator Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f2f5")

        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass

        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")

        try:
            logo_img = Image.open("assets/logo.png").resize((200, 50))
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(header_frame, image=self.logo, bg="#2c3e50").pack(side="left", padx=20)
        except:
            tk.Label(header_frame, text="CRYPTO SHIELD", font=('Arial', 20, 'bold'), 
                    fg="white", bg="#2c3e50").pack(side="left", padx=20)

        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        input_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove", padx=15, pady=15)
        input_frame.pack(fill="x", pady=(0, 20))

        tk.Label(input_frame, text="Wallet Address:", font=('Arial', 10, 'bold'), bg="white").grid(row=0, column=0, sticky="e")
        self.address_entry = tk.Entry(input_frame, width=60, font=('Arial', 10))
        self.address_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="Currency:", font=('Arial', 10, 'bold'), bg="white").grid(row=1, column=0, sticky="e")
        self.coin_var = tk.StringVar(value="BTC")
        coins = list(self.validator.patterns.keys())
        ttk.Combobox(input_frame, textvariable=self.coin_var, values=coins, state="readonly").grid(row=1, column=1, padx=10, pady=5, sticky="w")

        btn_frame = tk.Frame(input_frame, bg="white")
        btn_frame.grid(row=2, column=1, sticky="w", pady=10)

        tk.Button(btn_frame, text="Validate", command=self.validate_wallet, 
                 bg="#27ae60", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="View Explorer", command=self.open_explorer, 
                 bg="#3498db", fg="white", font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_results, 
                 bg="#e74c3c", fg="white", font=('Arial', 10)).pack(side="left", padx=5)

        self.results_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
        self.results_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.validation_tab = tk.Frame(self.notebook)
        self.notebook.add(self.validation_tab, text="Validation")
        self.setup_validation_tab()

        self.transactions_tab = tk.Frame(self.notebook)
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.setup_transactions_tab()

        self.safety_tab = tk.Frame(self.notebook)
        self.notebook.add(self.safety_tab, text="Safety Report")
        self.setup_safety_tab()

    def setup_validation_tab(self):
        frame = tk.Frame(self.validation_tab, padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        self.validation_text = scrolledtext.ScrolledText(frame, width=80, height=10, 
                                                      font=('Consolas', 10), wrap="word")
        self.validation_text.pack(fill="both", expand=True)
        self.validation_text.insert("end", "Validation results will appear here...")
        self.validation_text.config(state="disabled")

    def setup_transactions_tab(self):
        frame = tk.Frame(self.transactions_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("#1", "#2", "#3", "#4")
        self.tx_tree = ttk.Treeview(frame, columns=columns, show="headings")

        self.tx_tree.heading("#1", text="Date")
        self.tx_tree.heading("#2", text="Direction")
        self.tx_tree.heading("#3", text="Amount")
        self.tx_tree.heading("#4", text="TXID")

        self.tx_tree.column("#1", width=100, anchor="center")
        self.tx_tree.column("#2", width=80, anchor="center")
        self.tx_tree.column("#3", width=100, anchor="center")
        self.tx_tree.column("#4", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tx_tree.yview)
        self.tx_tree.configure(yscrollcommand=scrollbar.set)

        self.tx_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i in range(5):
            self.tx_tree.insert("", "end", values=(
                f"2023-05-{15-i}", 
                "In" if i%2 == 0 else "Out", 
                f"{0.1*(i+1):.2f}", 
                f"abc123xyz{i}..."))

    def setup_safety_tab(self):
        frame = tk.Frame(self.safety_tab, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        self.safety_text = scrolledtext.ScrolledText(frame, width=80, height=10, 
                                                   font=('Consolas', 10), wrap="word")
        self.safety_text.pack(fill="both", expand=True)
        self.safety_text.insert("end", "Safety analysis will appear here...")
        self.safety_text.config(state="disabled")

        risk_frame = tk.Frame(frame)
        risk_frame.pack(fill="x", pady=10)

        tk.Label(risk_frame, text="Risk Level:", font=('Arial', 10, 'bold')).pack(side="left")

        self.risk_meter = ttk.Progressbar(risk_frame, orient="horizontal", 
                                        length=200, mode="determinate")
        self.risk_meter.pack(side="left", padx=10)

        self.risk_label = tk.Label(risk_frame, text="0%", font=('Arial', 10))
        self.risk_label.pack(side="left")

    def validate_wallet(self):
        address = self.address_entry.get().strip()
        coin_type = self.coin_var.get()

        if not address:
            messagebox.showerror("Error", "Please enter a wallet address")
            return

        self.clear_results()

        is_valid, valid_msg = self.validator.validate_address(address, coin_type)

        self.validation_text.config(state="normal")
        self.validation_text.delete(1.0, "end")

        if is_valid:
            self.validation_text.insert("end", f"✔️ VALID {coin_type} ADDRESS
", "valid")
            self.validation_text.insert("end", f"
Address: {address}
")
            self.validation_text.insert("end", f"Network: {coin_type}
")
            self.validation_text.insert("end", f"Format: {valid_msg}
")
        else:
            self.validation_text.insert("end", f"❌ INVALID ADDRESS
", "invalid")
            self.validation_text.insert("end", f"
Error: {valid_msg}
")
            self.validation_text.tag_config("invalid", foreground="red")

        self.validation_text.tag_config("valid", foreground="green")
        self.validation_text.config(state="disabled")

        if not is_valid:
            return

        safety = self.validator.check_safety(address)

        self.safety_text.config(state="normal")
        self.safety_text.delete(1.0, "end")

        if safety['is_scam']:
            self.safety_text.insert("end", "⚠️ HIGH RISK WALLET DETECTED!
", "danger")
            self.safety_text.insert("end", "
This address has been flagged for:
")
            for detail in safety['details']:
                self.safety_text.insert("end", f"
• {detail.get('type', 'Unknown')}: ")
                self.safety_text.insert("end", f"{detail.get('description', 'No details')}
")
                if 'reported' in detail:
                    self.safety_text.insert("end", f"  Reported on: {detail['reported']}
")
        else:
            self.safety_text.insert("end", "✔️ CLEAN WALLET
", "safe")
            self.safety_text.insert("end", "
No known scam associations found
")

        self.safety_text.tag_config("danger", foreground="red")
        self.safety_text.tag_config("safe", foreground="green")
        self.safety_text.config(state="disabled")

        self.risk_meter['value'] = safety['risk_score']
        self.risk_label.config(text=f"{safety['risk_score']}%")

        self.update_transactions(address, coin_type)

    def update_transactions(self, address, coin_type):
        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)

        transactions = self.validator.get_transaction_sample(coin_type)

        for tx in transactions:
            self.tx_tree.insert("", "end", values=(
                tx['date'],
                tx.get('direction', 'Unknown'),
                f"{tx['amount']:.2f} {coin_type}",
                tx['txid']
            ))

    def open_explorer(self):
        address = self.address_entry.get().strip()
        coin_type = self.coin_var.get()

        if not address:
            messagebox.showerror("Error", "No address to explore")
            return

        if coin_type not in self.validator.patterns:
            messagebox.showerror("Error", "Unsupported cryptocurrency")
            return

        explorer_url = self.validator.patterns[coin_type]['explorer'] + address
        webbrowser.open_new_tab(explorer_url)

    def clear_results(self):
        self.validation_text.config(state="normal")
        self.validation_text.delete(1.0, "end")
        self.validation_text.insert("end", "Validation results will appear here...")
        self.validation_text.config(state="disabled")

        self.safety_text.config(state="normal")
        self.safety_text.delete(1.0, "end")
        self.safety_text.insert("end", "Safety analysis will appear here...")
        self.safety_text.config(state="disabled")

        self.risk_meter['value'] = 0
        self.risk_label.config(text="0%")

        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)

def main():
    root = tk.Tk()
    app = ValidatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
