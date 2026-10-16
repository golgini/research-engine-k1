import os


ENABLED = bool(os.getenv("GOLDSYS_TELEGRAM_TOKEN")) and os.getenv("GOLDSYS_TELEGRAM_ENABLED", "0") == "1"


def send_message(message):
    if not ENABLED:
        return False
    raise NotImplementedError("Telegram transport is intentionally disabled in this build")
