from openai import OpenAI

MODEL = "gpt-5.6-luna"

SYSTEM_PROMPT = """
Yuk e'lonini tahlil qil.

Mos bo'lsa:
HA

Mos bo'lmasa:
YO'Q

Mos:
- 3 tonnagacha
- qo'shimcha yuk
- KIA Bongo, Shineray, Porter, Labo kabi kichik yuk mashinasiga mos yuk
- kichik miqdordagi hayvonlar va boshqa kichik yuklar

Mos emas:
- 3 tonnadan ortiq
- fura yoki katta yuk mashinasi
- katta Isuzu kabi katta mashina talab qilinsa
- kichik mashinaga sig'maydigan yuk

Telefon, narx va ortiqcha gaplarni olib tashla.
Faqat bitta qator javob ber.
"""


def analyze_load(ad_text: str, api_key: str) -> str:
    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=ad_text,
            reasoning={"effort": "none"},
            max_output_tokens=30,
        )

        result = response.output_text.strip()

        if result.startswith("HA"):
            return result

        if result == "YO'Q" or result == "YO‘Q":
            return "YOQ"

        return "XATO"

    except Exception as e:
        return "XATO"