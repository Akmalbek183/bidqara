"""Asosiy pipeline: skaner → DB → Claude baho → Telegram.
Ishga tushirish:  python -m bidqara.run
Chat ID topish:   python -m bidqara.run --whoami
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

from .scrapers import SCRAPERS
from .analyze import assess
from .notify import send, format_message, whoami

load_dotenv()


def main():
    if "--whoami" in sys.argv:
        whoami()
        return

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    countries = [c.strip() for c in os.getenv("COUNTRIES", "Uzbekistan").split(",")]
    default_chat = os.getenv("TELEGRAM_CHAT_ID")

    # 1) Skanerlash va yangi tenderlarni saqlash
    new_tenders = []
    for name, fn in SCRAPERS.items():
        items = fn(countries)
        print(f"[{name}] {len(items)} ta e'lon")
        for t in items:
            exists = sb.table("tenders").select("id").eq("source", t["source"]).eq("external_id", t["external_id"]).execute().data
            if exists:
                continue
            row = sb.table("tenders").insert(t).execute().data[0]
            new_tenders.append(row)
    print(f"Yangi: {len(new_tenders)}")

    # 2) Har bir faol mijoz uchun baholash
    clients = sb.table("clients").select("*").eq("active", True).execute().data
    for t in new_tenders:
        for c in clients:
            try:
                a = assess(t, c["profile"])
            except Exception as e:
                print("[AI]", e)
                continue
            rec = {
                "tender_id": t["id"], "client_id": c["id"], "score": a["score"], "verdict": a["verdict"],
                "summary": a.get("summary"), "criteria": a.get("criteria"), "budget_estimate": a.get("budget_estimate"),
            }
            # 3) Chegaradan yuqori bo'lsa — Telegram
            chat = c.get("telegram_chat_id") or default_chat
            if chat and a["score"] >= int(c.get("min_score") or os.getenv("MIN_SCORE_TO_NOTIFY", 60)):
                rec["notified"] = send(chat, format_message(t, a))
            sb.table("assessments").upsert(rec, on_conflict="tender_id,client_id").execute()
            print(f"  {c['name']}: {a['verdict']} {a['score']} — {t['title'][:60]}")


if __name__ == "__main__":
    main()
