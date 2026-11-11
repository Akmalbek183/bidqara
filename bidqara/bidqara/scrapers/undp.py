"""UNDP Procurement Notices — procurement-notices.undp.org (ochiq sahifa + JSON feed).
Rasmiy API yo'q; sahifa jadvali barqaror. Agar struktura o'zgarsa, bu modul faqat log yozadi.
"""
import re
import httpx
from datetime import datetime

LIST_URL = "https://procurement-notices.undp.org/"

COUNTRY_ALIASES = {
    "Kyrgyz Republic": "Kyrgyzstan",
}


def _date(s):
    for fmt in ("%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date().isoformat()
        except Exception:
            pass
    return None


def fetch(countries: list[str], rows: int = 100) -> list[dict]:
    try:
        html = httpx.get(LIST_URL, timeout=40, follow_redirects=True).text
    except Exception as e:
        print(f"[UNDP] {e}")
        return []

    wanted = {COUNTRY_ALIASES.get(c, c).lower() for c in countries}
    out = []
    # Har bir e'lon <a href="view_notice.cfm?notice_id=NNN"> ... ichida: title, country, deadline
    for m in re.finditer(r'href="(view_notice\.cfm\?notice_id=(\d+))"(.*?)</a>', html, re.S):
        href, nid, body = m.group(1), m.group(2), m.group(3)
        text = re.sub(r"<[^>]+>", "|", body)
        parts = [p.strip() for p in text.split("|") if p.strip()]
        if not parts:
            continue
        joined = " ".join(parts).lower()
        if not any(c in joined for c in wanted):
            continue
        title = parts[0]
        country = next((c for c in countries if COUNTRY_ALIASES.get(c, c).lower() in joined), "")
        deadline = None
        dm = re.search(r"\d{1,2}-[A-Za-z]{3}-\d{2,4}", " ".join(parts))
        if dm:
            deadline = _date(dm.group(0))
        out.append({
            "source": "UNDP",
            "external_id": nid,
            "title": title,
            "country": country,
            "client": "UNDP " + country,
            "method": next((p for p in parts if p.upper() in ("RFP", "RFQ", "ITB", "EOI", "IC")), ""),
            "deadline": deadline,
            "url": LIST_URL + href,
            "raw": {"parts": parts},
        })
        if len(out) >= rows:
            break
    return out
