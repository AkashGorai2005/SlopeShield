import requests

from app.config import get_settings


def send_telegram_alert(
    location: str,
    risk_level: str,
    probability: float,
    rainfall: float,
    recommended_action: str,
) -> bool:
    settings = get_settings()

    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False

    message = (
        "🚨 SLOPESHIELD NER ALERT\n\n"
        f"Location: {location}\n"
        f"Risk Level: {risk_level.upper()}\n"
        f"Probability: {probability * 100:.1f}%\n"
        f"24h Rainfall: {rainfall:.1f} mm\n\n"
        f"Recommended Action:\n{recommended_action}"
    )

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={
                "chat_id": settings.telegram_chat_id,
                "text": message,
            },
            timeout=10,
        )
        response.raise_for_status()
        return bool(response.json().get("ok"))
    except Exception:
        # Telegram failure must never stop the monitoring cycle.
        return False