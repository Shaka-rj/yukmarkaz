import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

JSON_PATH = BASE_DIR / "data" / "places.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    PLACE_MAP = json.load(f)

CYRILLIC_MAP = str.maketrans({
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"yo",
    "ж":"j","з":"z","и":"i","й":"y","к":"k","л":"l","м":"m",
    "н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u",
    "ф":"f","х":"x","ц":"s","ч":"ch","ш":"sh","щ":"sh",
    "ъ":"","ь":"","э":"e","ю":"yu","я":"ya",
    "қ":"q","ғ":"g","ҳ":"h","ў":"o","ò":"o","ĝ":"g","õ":"o"
})

def normalize_text(text):
    text = text.lower()

    # Kirill -> lotin
    text = text.translate(CYRILLIC_MAP)

    # Apostroflarni bir xil qilish
    text = (text.replace("ʻ", "")
                .replace("’", "")
                .replace("`", "")
                .replace("‘", ""))

    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def find_regions(message):
    text = normalize_text(message)
    regions = []

    # Kalit so'zlarni uzunligi bo'yicha saralaymiz (uzunroq so'zlar birinchi tekshiriladi)
    # Masalan: "toshkent viloyati" birinchi, "toshkent" esa keyin tekshiriladi.
    sorted_keywords = sorted(PLACE_MAP.keys(), key=len, reverse=True)

    for keyword in sorted_keywords:
        pattern = r"\b" + re.escape(keyword) + r"\w*\b"
        
        match = re.search(pattern, text)
        if match:
            region = PLACE_MAP[keyword]
            if region not in regions:
                regions.append(region)
            
            # Topilgan so'zni matndan o'chirib tashlaymiz 
            # (qisqa kalit so'zlar qayta topilmasligi uchun)
            text = re.sub(pattern, " ", text)

    return regions