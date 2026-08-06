import re
import time
import hashlib


# RAM kesh: { message_hash: timestamp }
_SENT_MESSAGES = {}


def _get_md5(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode('utf-8')).hexdigest()


def _is_duplicate_recent(text: str, interval_seconds: int = 600) -> bool:
    """
    Xabar oxirgi N soniya (default: 600 soniya = 10 daqiqa)
    ichida yuborilgan bo'lsa True qaytaradi.
    """
    now = time.time()
    msg_hash = _get_md5(text)

    expired_keys = [h for h, ts in _SENT_MESSAGES.items() if now - ts > interval_seconds]
    for h in expired_keys:
        del _SENT_MESSAGES[h]

    if msg_hash in _SENT_MESSAGES:
        return True

    _SENT_MESSAGES[msg_hash] = now
    return False


blocked_words = [
    "reklama",
    "spam",
    "test",
    "астрахан",
    "волгоград",
    "беларус",
    "москва",
    "moskva",
    "малатя",
    "ekaterin",
    "serov",
    "tent",
    "fura",
    "тент",
    "фура",
    "новоросси",
    "росси",
    "manisa",
    "izmir",
    "шымкент",
    "шимкент",
    "омск",

    "olamiz",
    "оламиз",
    "yuramiz",
    "bo'shadik",
    "bo‘shadik",
    "tashiymiz",
    "boshladik",
]

def filter_message(text):
    if not text:
        return False

    if not (15 <= len(text.replace(" ", "")) <= 150):
        return

    if _is_duplicate_recent(text, interval_seconds=600):
        return False

    text_lower = text.lower()

    # 1. Blocked words tekshirish
    for word in blocked_words:
        if word.lower() in text_lower:
            return False


    # 2. O'zbekiston telefon raqami qidirish
    phone_pattern = r"""
        (?:
            \+?998[\s\-]?
        )?
        (?:
            (?:20|33|87|90|91|93|94|95|97|98|99|88|77|50)
        )
        [\s\-]?
        \d{3}
        [\s\-]?
        \d{2}
        [\s\-]?
        \d{2}
    """

    if re.search(phone_pattern, text, re.VERBOSE):
        return True

    return False
