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
    "германия",
    "алашанькоу",

    "olamiz",
    "оламиз",
    "yuramiz",
    "yuraman",
    "bo'shadik",
    "bo‘shadik",
    "tashiymiz",
    "boshladik",
    "xizmati",
    "yuk kerak",
    "yuk kera",
    "yuk bormi",
    "yuk olaman",
    "kerak bolsa",
    "олиб кетамиз",
    "moshinalar tayyor"
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


################ kichkina mashinalar uchun

# Krill-Lotin transliteratsiya xaritasi
CYRILLIC_TO_LATIN = str.maketrans({
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'қ': 'q', 'ғ': 'g', 'ҳ': 'h', 'ў': 'o'
})

# Taqiqlangan avtomobil va kalit so'zlar ro'yxati
FORBIDDEN_WORDS = (
    "isuzu", "isuzi", "izuzi", "esuzzi", "esuziy", "esuzi", "usuzi",
    "shacman", "shakman", "chakman", "kamaz", "samasval",
    "pagruzchik", "traler", "trailer", "tiraller", 
    "shalanda", "ref", "plashatka", "katta moshin",
    "evakuvator", "evakuator", "ekskavator",
    "yuk #",
    "sement", "sment", "sement", "shefir", "kumir",
    "tanar", "plashadka"
)

# Regseks patternedini dinamik va toza ko'rinishda yig'ish
FORBIDDEN_VEHICLES_PATTERN = re.compile(
    r'\b(' + '|'.join(map(re.escape, FORBIDDEN_WORDS)) + r')\w*',
    re.IGNORECASE
)


def extract_max_weight(text: str) -> float | None:
    # 1. Tonna va Kilogramm birliklarini ushlab oluvchi bitta umumiy regex
    # Group 1: 1-son, Group 2: 2-son (diapazon bolsa), Group 3: o'lchov birligi
    pattern = (
        r'(?<!\d)\b(\d+(?:[\.,]\d+)?)'
        r'(?:\s*-\s*(\d+(?:[\.,]\d+)?))?'
        r'[\s-]*(tonna|тонна|tona|тона|tn|тн|ton|тон|[tт]|kg|кг|kilo|кило)\b'
    )
    
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    if not matches:
        return None
    
    max_weight = 0.0
    for match in matches:
        val1 = float(match[0].replace(',', '.'))
        val2 = float(match[1].replace(',', '.')) if match[1] else val1
        unit = match[2].lower()
        
        # Kilogrammda kelsa, tonnaga o'tkazamiz
        if unit in ('kg', 'кг'):
            val1 /= 1000.0
            val2 /= 1000.0
        
        current_max = max(val1, val2)
        
        # Mantiqiy cheklov (Anomaliya filtri - 100 tonnadan ko'plar o'tkazilmaydi)
        if current_max > 100:
            continue
            
        if current_max > max_weight:
            max_weight = current_max
            
    return max_weight if max_weight > 0 else None

# katta mashina bulsa true
def mini_cars(text: str) -> bool:
    if weight is not None and weight > 3:
        return True

    """Matnni lotinchaga o'tkazib, taqiqlangan avtomobil nomlarini izlaydi."""
    normalized_text = text.lower().translate(CYRILLIC_TO_LATIN)
    return bool(FORBIDDEN_VEHICLES_PATTERN.search(normalized_text))
