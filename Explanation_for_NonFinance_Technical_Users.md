# Understanding HedgePortfolio Data — Guide for Non-Finance Technical Users

This guide explains how to read and interpret the numbers in HedgePortfolio if you come from a technical/engineering background rather than finance.

---

## 1. How to Think About the Data

Think of every portfolio as a **combination of two parts**:

- **Long Leg** — The part that makes money when QQQ goes up (your actual bet on the market)
- **Hedge Leg** — The insurance policy that protects you when QQQ goes down

All numbers in the tool are normalized to **$100,000** of long exposure so you can compare them fairly.

---

## 2. Risk of Each Portfolio (Simplified)

| Metric                  | What It Means (Plain English)                                      | How to Read It                              | Risk Level Guide                  |
|-------------------------|--------------------------------------------------------------------|---------------------------------------------|-----------------------------------|
| **Expected Return %**   | Average outcome you should expect over the time period             | Higher = better on average                  | —                                 |
| **5% CVaR**             | In the worst 5% of scenarios, this is roughly how much you lose    | More negative = worse tail risk             | -5% = low risk, -25% = high risk  |
| **Prob >20% DD**        | Chance your portfolio drops more than 20% from its peak            | Lower % = safer                             | < 5% = very safe, > 15% = risky   |
| **Portfolio Drag**      | Annual cost of holding the hedge (explained in detail below)       | Lower = cheaper to own the protection       | —                                 |

**Rule of thumb for technical users**:
- Look at **CVaR** and **Prob >20% DD** first — these tell you the real downside risk.
- **Expected Return** is useful but can be misleading if the downside is catastrophic.

---

## 3. Annual Drag — APY vs APR (Made Simple)

"Drag" is the cost of buying protection. We show it two ways so it's easy to understand:

### APR (Annual Percentage Rate)
- Simple yearly cost
- Example: 1.8% APR = you pay roughly **$1,800 per year** on a $100k portfolio

### APY (Annual Percentage Yield)
- The real compounded cost (more accurate)
- Slightly higher than APR because of compounding
- Example: 1.82% APY on the same portfolio

**How to use it**:
- If a hedge shows **180 bps drag** → that's **1.8% per year**
- On $100,000 that costs you **$1,800/year** in expected return
- Think of it like the "insurance premium" you're paying every year

---

## 4. % of Capital Taken Up by the Hedge

This tells you **how much of your $100k is effectively "spent" on protection**.

| Hedge Type                    | Typical Cost | % of $100k Capital Used | Real Dollar Cost | Interpretation |
|-------------------------------|--------------|--------------------------|------------------|----------------|
| QQQ 10% OTM Put               | 1.8%        | 1.8%                    | $1,800          | Moderate insurance |
| QQQ 20% OTM Put               | 0.9%        | 0.9%                    | $900            | Cheaper, less protection |
| VIXY Volatility Hedge         | 6.0%        | 6.0%                    | $6,000          | Expensive but powerful in crashes |
| Bear Put Spread               | 1.1%        | 1.1%                    | $1,100          | Good value |
| Collar                        | 0.7%        | 0.7%                    | $700            | Cheapest protection |

**Key insight**: Higher % = more capital is "locked" in the hedge instead of working for you.

---

## 5. Notional Value Being Protected

This answers: **"How much of my actual exposure is the hedge actually covering?"**

| Portfolio Example                          | Notional Long | Hedge Notional Protected | % of Portfolio Protected | Notes |
|--------------------------------------------|---------------|---------------------------|---------------------------|-------|
| QQQ Equities + 10% OTM Put                 | $100,000     | ~$85,000                 | 85%                      | Covers most but not all downside |
| QQQ Equities + 20% OTM Put                 | $100,000     | ~$70,000                 | 70%                      | Only protects severe crashes |
| MNQ Futures (2×) + 10% OTM Put             | $200,000     | ~$170,000                | 85%                      | Hedge sized to the leveraged exposure |
| QQQ Deep ITM Calls + Bear Put Spread       | $100,000     | ~$60,000                 | 60%                      | Cheaper but less coverage |

**Rule**:
- You usually want the hedge to protect **70–100%** of your notional long exposure.
- If your hedge only protects 40%, you're still taking a lot of risk.

---

## 6. How Much to Size the Hedge (Practical Guide)

### Simple Sizing Rule

| Goal                              | Recommended Hedge Size                  | When to Use |
|-----------------------------------|-----------------------------------------|-------------|
| **Light protection**              | 50–70% of notional long                 | Bullish outlook, want cheap insurance |
| **Balanced protection**           | 80–100% of notional long                | Most common professional choice |
| **Strong crash protection**       | 100–120% of notional long               | Expecting volatility or recession |
| **Maximum safety**                | 150%+ of notional long                  | Very risk-averse or large portfolio |

### Example Calculations

**Example 1: $100k QQQ Equities + 10% OTM Put**
- Notional long = $100,000
- Recommended hedge size = **$85,000 – $100,000**
- You would typically buy **4 contracts** (each contract = ~$25k notional)

**Example 2: MNQ Futures 2× ($200k notional)**
- Notional long = $200,000
- Recommended hedge size = **$170,000 – $200,000**
- You need roughly **twice** as many put contracts compared to regular QQQ

---

## 7. Quick Decision Framework for Technical Users

| Question                              | Look at This Metric                     | Good Value          | Action |
|---------------------------------------|-----------------------------------------|---------------------|--------|
| How risky is the downside?            | 5% CVaR + Prob >20% DD                  | CVaR > -12%, Prob < 8% | Prefer this |
| How much is the insurance costing me? | Portfolio Drag (APY)                    | < 1.5%             | Acceptable |
| How much capital is the hedge using?  | Hedge Cost %                            | < 2%               | Good |
| How much of my exposure is protected? | Notional Protected %                    | 80%+               | Well hedged |
| Should I increase the hedge size?     | Current protection % vs goal            | —                  | Adjust contracts |

---

## 8. One-Page Mental Model

```
Portfolio = Long Exposure + Insurance (Hedge)

- Long Exposure   → Makes money when market goes up
- Hedge           → Costs money every year (drag) but pays off in crashes
- Goal            → Find the cheapest insurance that still protects most of your money

Key numbers to watch every time:
1. 5% CVaR          → Worst-case pain
2. Drag (APY)       → Yearly insurance cost
3. % Protected      → How much of your money is actually insured
```

---

**Bottom line for technical users**:
Treat this like any engineering system with **upside performance**, **failure modes**, and **maintenance cost**.  
The best portfolios minimize **failure mode severity** (CVaR) while keeping **maintenance cost** (drag) low and **coverage** (notional protected) high.

---

*This document is meant to be read alongside the main dashboard.*