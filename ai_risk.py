def calculate_risk_score(data):
    score = 100
    reasons = []

    # Penalti jika balance rendah
    if data["balance"] < 0.01:
        score -= 30
        reasons.append("⚠️ Very low balance")

    # Penalti jika tx rendah
    if data["tx_count"] < 3:
        score -= 20
        reasons.append("⚠️ Few transactions")

    # Penalti jika wallet baru
    if data["wallet_age"] == 0:
        score -= 20
        reasons.append("⚠️ No age data / too new")

    # Bonus jika balance tinggi
    if data["balance"] > 1:
        score += 10
        reasons.append("✅ Strong wallet balance")

    # Hadkan antara 0 hingga 100
    score = max(0, min(100, score))

    # Penilaian akhir
    if score >= 80:
        reasons.append("✅ Low Risk Wallet")
    elif score >= 50:
        reasons.append("⚠️ Medium Risk Wallet")
    else:
        reasons.append("🚨 High Risk Wallet")

    return score, "; ".join(reasons)
