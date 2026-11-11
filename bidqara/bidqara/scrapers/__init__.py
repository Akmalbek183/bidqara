"""Manba skanerlari. Har biri list[dict] qaytaradi:
{source, external_id, title, country, client, method, deadline (YYYY-MM-DD|None), url, raw}
"""
from .worldbank import fetch as fetch_worldbank
from .undp import fetch as fetch_undp

SCRAPERS = {
    "WB": fetch_worldbank,
    "UNDP": fetch_undp,
}
