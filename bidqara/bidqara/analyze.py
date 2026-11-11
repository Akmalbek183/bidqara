"""Claude orqali tender × mijoz profili baholash."""
import json
import os
import anthropic

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

SYSTEM = """Siz IFI (World Bank, ADB, EBRD, UNDP, AIIB, IsDB, JICA) tenderlari bo'yicha 15 yillik tajribaga ega bid-menejersiz.
Vazifa: berilgan tender e'lonini mijoz kompaniya profili bilan solishtirib, qisqa va aniq Go/No-Go baho berish.
Qoidalar:
- Ball 0-100: 70+ = GO, 45-69 = REVIEW (hamkor/shart tekshirish kerak), <45 = SKIP.
- Mijoz xorijiy lider bo'la olmasa va tender xalqaro firma tajribasini talab qilsa — ball 45-65 oralig'ida, verdict REVIEW, summary'da JV tavsiyasi.
- Muddat 5 kundan kam bo'lsa — buni criteria'da "mb" sifatida belgilang.
- Byudjet e'londa bo'lmasa — IFI amaliyotidan taxminiy diapazon bering va "(taxmin)" deb yozing.
- Faqat JSON qaytaring, boshqa matn yo'q. Til: o'zbek (lotin)."""

SCHEMA = """{
 "score": <int 0-100>,
 "verdict": "GO" | "REVIEW" | "SKIP",
 "summary": "<2-3 jumla: nega shu ball, keyingi qadam>",
 "budget_estimate": "<masalan '$80-120k (taxmin)'>",
 "criteria": [{"status": "ok"|"ko"|"mb", "text": "<qisqa>"}, ... 3-5 ta]
}"""


def assess(tender: dict, profile: dict) -> dict:
    client = anthropic.Anthropic()
    user = f"""TENDER:
{json.dumps({k: tender.get(k) for k in ("source","title","country","client","method","deadline","url")}, ensure_ascii=False, indent=1)}
Qo'shimcha (xom): {json.dumps(tender.get("raw", {}), ensure_ascii=False)[:3000]}

MIJOZ PROFILI:
{json.dumps(profile, ensure_ascii=False, indent=1)}

Javobni aynan shu JSON sxemada bering:
{SCHEMA}"""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=700,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = msg.content[0].text.strip()
    # ```json ... ``` bo'lsa tozalash
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):text.rfind("}") + 1]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"score": 0, "verdict": "SKIP", "summary": "AI javobini o'qib bo'lmadi: " + text[:200],
                "budget_estimate": "", "criteria": []}
    data["score"] = int(data.get("score", 0))
    data["verdict"] = data.get("verdict", "SKIP").upper()
    return data
