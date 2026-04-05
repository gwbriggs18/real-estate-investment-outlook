# Investment Outlook

Web app to compare **hypothetical stock market** vs **hypothetical real estate** investments over the same period. Example: “If I bought VOO in 2024, how much would it be worth in December 2025 vs putting 20% down on a $2M house at 7% interest?”

- **Stocks:** Historical prices via Alpha Vantage (split/dividend adjusted). Enter ticker, amount, buy/sell dates.
- **Real estate:** No API. Enter purchase price, down payment %, interest rate, buy and as-of dates; we compute mortgage balance and equity. Optional annual appreciation % for value growth.

## Quick start

### Run with Docker Compose (recommended)

1. **Get a free API key** (for stock data):
   - [Alpha Vantage](https://www.alphavantage.co/support/#api-key) – free tier: 25 requests/day, 5/minute.

2. **Create a `.env` file** in the project root (copy from `.env.example`):
   ```env
   ALPHA_VANTAGE_API_KEY=your_actual_key_here
   ```

3. **Build and start:**
   ```bash
   docker compose up --build
   ```

4. **Open:** [http://localhost:3000](http://localhost:3000)  
   Fill in **Stocks** (e.g. VOO, $400,000, buy/sell dates) and/or **Real estate** (e.g. $2M purchase, 20% down, 7% rate, buy + as-of date). Click **Compare**.

5. **Stop:** `Ctrl+C` or `docker compose down`.

### Run locally (Python 3.10+)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python app.py
```

Open [http://localhost:3000](http://localhost:3000).

## APIs used

| Provider | Purpose | Free tier |
|----------|---------|-----------|
| **Alpha Vantage** | US equity daily adjusted prices | 25 req/day, 5/min |

Real estate is **hypothetical only** (no property API): you supply purchase price, down payment, and rate; we compute mortgage and equity at the as-of date.

## API (backend)

- `GET /api/health` – health check.
- `GET /api/stock/hypothetical-return?symbol=&investedAmount=&buyDate=&sellDate=` – stock hypothetical return.
- `GET /api/stock/historical?symbol=&from=&to=` – daily adjusted close.
- `GET /api/real-estate/hypothetical?purchasePrice=&downPaymentPercent=&annualInterestRate=&buyDate=&asOfDate=&annualAppreciationPercent=0` – real estate hypothetical (mortgage + equity at as-of date).
- `GET /api/compare?...` – run both in one request. Combine stock params (symbol, investedAmount, buyDate, sellDate) and/or real estate params (purchasePrice, downPaymentPercent, annualInterestRate, reBuyDate, asOfDate, annualAppreciationPercent).

## Project layout

- `app.py` – Flask app, static frontend, `/api/stock`, `/api/real-estate`, `/api/compare`.
- `backend/routes/` – stock, real_estate, compare blueprints.
- `backend/services/` – alpha_vantage, returns (stock), real_estate (mortgage math).
- `frontend/` – HTML/CSS/JS comparison UI.

## Docker

- **Dockerfile:** Python 3.12 slim, runs `python app.py` on port 3000.
- **docker-compose:** Builds image, port 3000, `ALPHA_VANTAGE_API_KEY` from `.env`.

Do not commit `.env`; use `.env.example` as a template.

## Development Notes

- Improved explanation of leverage impact in property investing.
