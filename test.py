import re
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
    weight = extract_max_weight(text)
    if weight is not None and weight > 3:
        return True

    """Matnni lotinchaga o'tkazib, taqiqlangan avtomobil nomlarini izlaydi."""
    normalized_text = text.lower().translate(CYRILLIC_TO_LATIN)
    return bool(FORBIDDEN_VEHICLES_PATTERN.search(normalized_text))

print(mini_cars("ГУЛИСТОН МОСТАН САМАРКАНДГА ХУНДАЙ КИЯ КЕРАК СРОЧНИ 977742600"))