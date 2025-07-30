import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def log_user(wallet, network):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)

        sheet = client.open("ADC_CryptoGuard_Logs").sheet1  # tukar nama sheet kalau perlu
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        sheet.append_row([now, wallet, network])

    except Exception as e:
        print("Logging Error:", e)
