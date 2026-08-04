# HedgePortfolio - Product Requirements Document (PRD)

## 1. Executive Summary
HedgePortfolio is an interactive analytics platform that enables professional traders and sophisticated investors to compare probabilistic returns across five distinct strategies for a $100k QQQ exposure:

1. **QQQ Unhedged** - Long QQQ ETF only
2. **QQQ Hedged** - Long QQQ + protective puts (collar or protective put)
3. **MNQ Futures + Options Hedge** - Micro E-mini Nasdaq-100 futures with options overlay
4. **QQQ Calls Only** - Synthetic long via deep ITM calls (capital efficient)
5. **SGOV Equivalent $100k** - Short-term Treasury ETF (cash drag benchmark)

The tool ingests real-time market data (Yahoo Finance + options chains) and runs professional-grade quantitative analysis including Monte Carlo simulations, Greeks, tail-risk, and scenario analysis.

## 2. Core Objectives & Success Metrics
- **Primary Goal**: Quantify expected value, downside protection, and "portfolio drag" of each hedge relative to unhedged QQQ.
- **Key Deliverables**:
  - Interactive Streamlit dashboard
  - Real-time options & futures data ingestion
  - Monte Carlo simulation engine (10k+ paths)
  - Professional trader metrics (Sharpe, Sortino, MaxDD, CVaR, Kelly)
  - Mauboussin & Ken Griffin style frameworks
- **Target Users**: Quant traders, options market makers, family offices, hedge fund analysts.

## 3. User Stories
- As a trader, I want to see the distribution of 30/90/252-day returns for each strategy under different volatility regimes.
- As an analyst, I want to understand the cost-of-carry / drag of each hedge expressed in bps and expected return erosion.
- As a risk manager, I want to view 5% and 1% CVaR and probability of >20% drawdown.
- As a strategist, I want to run "what-if" scenarios (Fed hike, earnings gap, vol spike) and see which hedge wins.

## 4. Functional Requirements

### 4.1 Data Layer
- Real-time quotes: `QQQ`, `MNQ=F`, `SGOV`, VIX, rates
- Full options chain for QQQ and MNQ (strikes, expirations, IV, Greeks)
- Historical daily prices (5+ years) for backtesting
- Implied vol surface & term structure

### 4.2 Strategies (Hard-coded 5)
1. **Unhedged QQQ** (`QQQ`)
2. **QQQ + 5% OTM Put Hedge** (protective put)
3. **MNQ 2x leveraged futures + OTM put spread**
4. **QQQ Deep ITM Call (0.90 delta) + cash**
5. **SGOV 100% allocation** (risk-free benchmark)

### 4.3 Quantitative Engine
- Monte Carlo: Geometric Brownian Motion + jump diffusion (Merton model)
- Parameters: mu, sigma (from historical + implied), skew/kurtosis
- Greeks calculation (delta, gamma, vega, theta) per position
- Portfolio drag calculation: expected annual return reduction vs unhedged
- Optimal trade identification using Kelly criterion & risk-adjusted metrics

### 4.4 Mauboussin & Ken Griffin Lens
- **Expectations Investing** (Mauboussin):
  - Expected return decomposition: earnings growth + multiple change + yield
  - Margin of safety vs. implied move
  - Scenario-weighted probabilities
- **Ken Griffin / Citadel Lens**:
  - Market-making view: bid-ask, gamma scalping P&L
  - Edge vs. retail pricing of options
  - Tail hedging efficiency (cost per unit of protection)

## 5. Non-Functional Requirements
- Performance: Monte Carlo (10k paths) < 8 seconds on standard laptop
- UI: Streamlit with Plotly charts (distribution, Greeks heatmaps, efficient frontier)
- Reproducibility: All seeds fixed, data snapshots saved
- Extensibility: Easy to add new strategies via strategy class

## 6. Technical Architecture
```
hedge_portfolio/
├── app.py                 # Streamlit main app
├── data/
│   ├── fetcher.py         # yfinance + options scraping
│   └── cache/             # parquet snapshots
├── strategies/
│   ├── base.py
│   ├── unhedged.py
│   ├── qqq_hedged.py
│   ├── mnq_futures.py
│   ├── calls_only.py
│   └── sgov.py
├── simulation/
│   ├── monte_carlo.py     # GBM + Merton
│   └── metrics.py         # Sharpe, CVaR, Kelly etc.
├── analysis/
│   ├── mauboussin.py
│   └── griffin.py
└── utils/
    └── helpers.py
```

## 7. MVP Scope (Phase 1)
- Streamlit single-page app with 5 strategies
- Real-time data fetch (QQQ, MNQ, SGOV, options)
- 1-day, 30-day, 90-day Monte Carlo (5k paths)
- Summary table: EV, Drag (bps), 5% CVaR, P(>20% DD)
- "Optimal Trade" recommendation box
- Mauboussin & Griffin commentary panels

## 8. Future Phases
- Phase 2: Live order book integration & Greeks live P&L
- Phase 3: Multi-asset (SPX, IWM) + correlation hedging
- Phase 4: Backtesting engine + walk-forward optimization

## 9. Open Questions / Decisions
- Should we include transaction costs & slippage? (Recommended: yes for realism)
- Default capital assumption: $100k (fixed)
- Preferred option expiry: 30DTE or 90DTE? (Default 45DTE)

## 10. Success Criteria
- Dashboard launches with live data in <10s
- Clear winner identified for current vol regime
- Professional traders can export PDF report with all charts

---

**Document Owner**: Arena.ai Agent  
**Version**: 1.0  
**Date**: 2026-08-04

*Next step: Implement MVP using the architecture above.*