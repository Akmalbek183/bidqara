"""World Bank Procurement Notices — ochiq JSON API.
Hujjat: https://search.worldbank.org/api/v2/procnotices
"""
import httpx
from datetime import datetime

API = "https://search.worldbank.org/api/v2/procnotices"


def _date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "")).date().isoformat()
    except Exception:
        return None


def fetch(countries: list[str], rows: int = 100) -> list[dict]:
    out = []
    for country in countries:
        params = {
            "format": "json",
            "rows": rows,
            "os": 0,
            "srt": "noticedate",
            "order": "desc",
            "project_ctry_name_exact": country,
            # faqat konsalting va ochiq e'lonlar
            "notice_type_exact": "Request for Expression of Interest",
        }
        try:
            r = httpx.get(API, params=params, timeout=40)
            r.raise_for_status()
            data = r.json().get("procnotices", [])
        except Exception as e:  # manba yiqilsa, boshqalarini to'xtatmaymiz
            print(f"[WB] {country}: {e}")
            continue
        for n in data:
            nid = n.get("id") or n.get("notice_id")
            if not nid:
                continue
            out.append({
                "source": "WB",
                "external_id": str(nid),
                "title": (n.get("project_name") or "") + " — " + (n.get("bid_description") or n.get("notice_type") or ""),
                "country": n.get("project_ctry_name") or country,
                "client": n.get("procuring_entity") or n.get("borrower") or "",
                "method": n.get("procurement_method_name") or n.get("procurement_method") or "",
                "deadline": _date(n.get("submission_deadline_date")),
                "url": n.get("url") or f"https://projects.worldbank.org/en/projects-operations/procurement-detail/{nid}",
                "raw": n,
            })
    return out
