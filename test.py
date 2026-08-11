other_countries = [

    # flags
    "🇨🇳","🇰🇿","🇷🇺","🇹🇷","🇦🇿",

    # Rossiya
    "rossiya", "россия", "russia", "🇷🇺",

    # Qozog‘iston
    "qozog‘iston", "qozogiston", "казахстан", "kazakhstan", "🇰🇿",

    # Qirg‘iziston
    "qirg‘iziston", "qirgiziston", "киргизия", "кыргызстан",
    "kyrgyzstan", "🇰🇬",

    # Tojikiston
    "tojikiston", "тоҷикистон", "таджикистан", "tajikistan", "🇹🇯",

    # Turkmaniston
    "turkmaniston", "туркменистан", "turkmenistan", "🇹🇲",

    # Afg‘oniston
    "afg‘oniston", "afgoniston", "афганистан", "afghanistan", "🇦🇫",

    # Xitoy
    "xitoy", "китай", "china", "🇨🇳",

    # Turkiya
    "turkiya", "турция", "türkiye", "turkey", "🇹🇷",

    # Eron
    "eron", "иран", "iran", "🇮🇷",

    # BAA
    "baa", "оаэ", "uae", "dubai", "dubay", "🇦🇪",

    # Saudiya
    "saudiya", "саудовская аравия", "saudi arabia", "🇸🇦",

    # Pokiston
    "pokiston", "пакистан", "pakistan", "🇵🇰",

    # Hindiston
    "hindiston", "индия", "india", "🇮🇳",

    # Ukraina
    "ukraina", "украина", "ukraine", "🇺🇦",

    # Belarus
    "belarus", "беларусь", "belarus", "🇧🇾",

    # Gruziya
    "gruziya", "грузия", "georgia", "🇬🇪",

    # Armaniston
    "armaniston", "армении", "армения", "armenia", "🇦🇲",

    # Ozarbayjon
    "ozarbayjon", "azerbayjon", "азербайджан", "azerbaijan", "🇦🇿",
]

text = '''🇺🇿САМАРКАНД - 🇷🇺ЧЕЧНЯ 

🚚: 4 та

🇺🇿САМАРКАНД -> 🇷🇺СЫСЕРТ

🚚: 1 ТА 

🇺🇿САМАРКАНД -> 🇷🇺ОРЕНБУРГ
 
🚚: 3 та

🇺🇿 САМАРКАНД -> 🇷🇺 МАГНИТОГОРСК 

🚚: 1 ТА 


ТЕЛЕФОН: +998958442555'''
text_lower = text.lower()
for country in other_countries:
    if country.lower() in text_lower:
        print("yooooooooooooooo")