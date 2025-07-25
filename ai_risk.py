def calculate_risk_score(wallet_data):
    balance = wallet_data.get("balance", 0)
    tx_count = wallet_data.get("tx_count", 0)
    wallet_age = wallet_data.get("wallet_age", 0)

    # Inisialisasi skor
    score = 0
    reasons = []

    # -------------------------------
    # ✅ Logik AI Ringkas (boleh upgrade nanti ke ML model)
    # -------------------------------

    # 1. Balance rendah → tambah risiko
    if balance == 0:
        score += 30
        reasons.append("No balance in wallet")
    elif balance < 0.001:
        score += 15
        reasons.append("Very low wallet balance")

    # 2. Tx count sikit → mencurigakan
    if tx_count == 0:
        score += 30
        reasons.append("No transaction history")
    elif tx_count < 3:
        score += 15
        reasons.append("Low transaction activity")

    # 3. Wallet baru → risiko tinggi
    if wallet_age == 0:
        score += 25
        reasons.append("No age data / too new")
    elif wallet_age < 7:
        score += 15
        reasons.append(f"Wallet created {wallet_age} days ago")

    # Clamp score to 100 max
    final_score = min(score, 100)

    # Risk label (optional)
    if final_score >= 75:
        reasons.append("⚠️ High Risk Wallet")
    elif final_score >= 40:
        reasons.append("⚠️ Moderate Risk Wallet")
    else:
        reasons.append("✅ Low Risk Wallet")

    return final_score, "; ".join(reasons)
