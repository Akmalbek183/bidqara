# Bidqara — MVP (skaner → Claude → Telegram)

## O'rnatish (10 daqiqa)
1. `pip install -r requirements.txt`
2. `.env.example` → `.env` nusxalang, kalitlarni to'ldiring.
3. Supabase → SQL Editor → `sql/schema.sql` ni ishga tushiring (jadvallar + birinchi mijoz).
4. Telegram'da botingizga `/start` yozing, so'ng: `python -m bidqara.run --whoami` → chiqqan ID'ni `.env` dagi `TELEGRAM_CHAT_ID` ga qo'ying.
5. Sinov: `python -m bidqara.run`

## Avtomat (GitHub Actions, bepul)
Repo → Settings → Secrets and variables → Actions → 5 ta secret qo'shing
(ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SUPABASE_URL, SUPABASE_SERVICE_KEY).
`.github/workflows/scan.yml` har 30 daqiqada ishlaydi. Actions → "Bidqara scan" → Run workflow bilan qo'lda sinang.

## Keyingi qadamlar
- `bidqara/scrapers/` ga ADB, EBRD (ECEPP), xarid.uzex, AIIB, IsDB qo'shish (bir xil dict formatida qaytarsa bo'ldi).
- ToR PDF yuklab, `analyze.py` ga to'liq matnni berish (pypdf allaqachon requirements'da).
- Mijoz onboarding: Telegram botda savol-javob → `clients` jadvaliga yozish.
- EOI generator va to'lov — 3–4-hafta.
