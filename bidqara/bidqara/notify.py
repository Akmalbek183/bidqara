"""Telegram Bot API orqali xabar yuborish."""
import os
import httpx

API = "https://api.telegram.org/bot{token}/{method}"
ICON = {"GO": "🟢", "REVIEW": "🟡", "SKIP": "🔴"}
MARK = {"ok": "✓", "ko": "✗", "mb": "!"}


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_message(tender: dict, a: dict) -> str:
    crit = "\n".join(f"  {MARK.get(c.get('status'),'•')} {_esc(c.get('text',''))}" for c in a.get("criteria", []))
    days = ""
    if tender.get("deadline"):
        from datetime import date
        try:
            d = (date.fromisoformat(tender["deadline"]) - date.today()).days
            days = f" ({d} kun)"
        except Exception:
            pass
    return (
        f"{ICON.get(a['verdict'],'•')} <b>{a['verdict']} · {a['score']}/100</b>\n"
        f"<b>{_esc(tender['title'])}</b>\n"
        f"{_esc(tender['source'])} · {_esc(tender.get('client',''))} · {_esc(tender.get('method',''))}\n"
        f"🌍 {_esc(tender.get('country',''))}   💰 {_esc(a.get('budget_estimate',''))}\n"
        f"⏰ {_esc(tender.get('deadline') or 'ko‘rsatilmagan')}{days}\n\n"
        f"{crit}\n\n"
        f"<i>{_esc(a.get('summary',''))}</i>\n\n"
        f"🔗 <a href=\"{tender.get('url','')}\">E'lonni ochish</a>"
    )


def send(chat_id: str, text: str, token: str | None = None) -> bool:
    token = token or os.environ["TELEGRAM_BOT_TOKEN"]
    r = httpx.post(API.format(token=token, method="sendMessage"), json={
        "chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True,
    }, timeout=30)
    if r.status_code != 200:
        print("[TG]", r.text[:300])
    return r.status_code == 200


def whoami(token: str | None = None):
    """Chat ID topish uchun: botga /start yozing, keyin shu funksiyani chaqiring."""
    token = token or os.environ["TELEGRAM_BOT_TOKEN"]
    r = httpx.get(API.format(token=token, method="getUpdates"), timeout=30).json()
    seen = set()
    for u in r.get("result", []):
        m = u.get("message") or u.get("channel_post") or {}
        c = m.get("chat", {})
        if c.get("id") not in seen:
            seen.add(c["id"])
            print(c.get("id"), c.get("type"), c.get("title") or c.get("username") or c.get("first_name"))
