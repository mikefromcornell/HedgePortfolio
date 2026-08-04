# HedgePortfolio

Professional-grade probabilistic analysis and Monte Carlo comparison of QQQ hedging strategies.

**Five Strategies Compared**:
1. QQQ Unhedged
2. QQQ + Protective Puts (Hedged)
3. MNQ Futures + Options Overlay
4. QQQ Deep ITM Calls (Capital Efficient)
5. SGOV $100k Cash Equivalent

**Key Features**:
- Real market + options data via yfinance
- Monte Carlo simulation (GBM + Merton jump diffusion)
- Portfolio drag, CVaR, Kelly criterion
- Mauboussin "Expectations Investing" + Ken Griffin / Citadel lens
- Interactive Streamlit dashboard

## Quick Start

```bash
cd HedgePortfolio
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
See `PRD.md` for full requirements.

## Status
MVP in active development. PRD complete.

---

*Built with ❤️ by Arena.ai Agent*