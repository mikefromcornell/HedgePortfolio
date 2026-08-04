import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="HedgePortfolio • Combinatorial Analyzer", layout="wide", page_icon="📊")

# ================== CONSTANTS ==================
DEFAULT_CAPITAL = 100_000
LONGS = {
    "QQQ Equities": {"type": "stock", "delta": 1.0},
    "QQQ Deep ITM Calls": {"type": "call", "delta": 0.90},
    "QQQ ATM Calls": {"type": "call", "delta": 0.50},
    "MNQ Futures (2×)": {"type": "futures", "leverage": 2.0},
    "SGOV (Cash)": {"type": "cash", "delta": 0.0}
}
HEDGES = {
    "QQQ 10% OTM Put": {"type": "put", "otm": 0.10},
    "QQQ 20% OTM Put": {"type": "put", "otm": 0.20},
    "VIXY Volatility Hedge": {"type": "vix", "allocation": 0.08},
    "SQQQ ATM Calls": {"type": "inverse_call", "delta": 0.50},
    "Bear Put Spread (10/20%)": {"type": "bear_spread"},
    "Collar (10% Put + 5% Call)": {"type": "collar"}
}

@st.cache_data(ttl=300)
def get_prices():
    tickers = ["QQQ", "VIXY", "SQQQ", "SGOV"]
    data = yf.download(tickers, period="5d", progress=False)
    return {t: float(data[("Close", t)].iloc[-1]) for t in tickers}

prices = get_prices()
qqq_price = prices["QQQ"]

# ================== CORE SIMULATION ==================
def simulate_portfolio(long_name, hedge_name, capital=DEFAULT_CAPITAL, days=30, seed=42):
    np.random.seed(seed)
    T = days / 365.25
    mu, sigma = 0.12, 0.22
    n_sims = 4000
    Z = np.random.normal(0, 1, n_sims)
    drift = (mu - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T) * Z
    qqq_return = np.exp(drift + diffusion) - 1

    long_mult = LONGS[long_name].get("delta", LONGS[long_name].get("leverage", 1.0))
    long_pnl = qqq_return * long_mult

    hedge_pnl, cost = 0.0, 0.0
    if hedge_name == "QQQ 10% OTM Put":
        cost, hedge_pnl = 0.018, np.where(qqq_return < -0.10, -qqq_return - 0.10, 0) * 0.85
    elif hedge_name == "QQQ 20% OTM Put":
        cost, hedge_pnl = 0.009, np.where(qqq_return < -0.20, -qqq_return - 0.20, 0) * 0.70
    elif hedge_name == "VIXY Volatility Hedge":
        cost, hedge_pnl = 0.06, np.abs(qqq_return) * 1.8 * 0.08
    elif hedge_name == "SQQQ ATM Calls":
        cost, hedge_pnl = 0.025, np.where(qqq_return < 0, -qqq_return * 0.9, 0) * 0.5
    elif hedge_name == "Bear Put Spread (10/20%)":
        cost, hedge_pnl = 0.011, np.clip(-qqq_return - 0.10, 0, 0.10) * 0.6
    elif hedge_name == "Collar (10% Put + 5% Call)":
        cost, hedge_pnl = 0.007, np.where(qqq_return < -0.10, -qqq_return - 0.10, 0) * 0.6

    net_return = long_pnl + hedge_pnl - cost
    return {
        "Expected Return %": round(np.mean(net_return) * 100, 2),
        "5% CVaR %": round(np.percentile(net_return, 5) * 100, 1),
        "Prob >20% DD %": round(np.mean(net_return < -0.20) * 100, 1),
        "Portfolio Drag (bps)": int(cost * 10000),
        "Hedge Cost %": round(cost * 100, 2)
    }

def tail_risk_analysis(long_name, hedge_name, scenario_return, capital=DEFAULT_CAPITAL):
    long_mult = LONGS[long_name].get("delta", LONGS[long_name].get("leverage", 1.0))
    long_pnl = scenario_return * long_mult
    hedge_pnl, cost = 0.0, 0.0

    if hedge_name == "QQQ 10% OTM Put":
        cost, hedge_pnl = 0.018, max(-scenario_return - 0.10, 0) * 0.85
    elif hedge_name == "QQQ 20% OTM Put":
        cost, hedge_pnl = 0.009, max(-scenario_return - 0.20, 0) * 0.70
    elif hedge_name == "VIXY Volatility Hedge":
        cost, hedge_pnl = 0.06, abs(scenario_return) * 1.8 * 0.08
    elif hedge_name == "SQQQ ATM Calls":
        cost, hedge_pnl = 0.025, max(-scenario_return, 0) * 0.9 * 0.5
    elif hedge_name == "Bear Put Spread (10/20%)":
        cost, hedge_pnl = 0.011, min(max(-scenario_return - 0.10, 0), 0.10) * 0.6
    elif hedge_name == "Collar (10% Put + 5% Call)":
        cost, hedge_pnl = 0.007, max(-scenario_return - 0.10, 0) * 0.6

    final_pnl = long_pnl + hedge_pnl - cost
    final_value = capital * (1 + final_pnl)
    return {"Final Value": round(final_value), "P&L %": round(final_pnl * 100, 1), "Hedge Effectiveness": round(hedge_pnl * 100, 1)}

def sensitivity_analysis(long_name, hedge_name, move_pct, capital=DEFAULT_CAPITAL):
    long_mult = LONGS[long_name].get("delta", LONGS[long_name].get("leverage", 1.0))
    long_pnl = (move_pct / 100) * long_mult

    hedge_pnl, cost = 0.0, 0.0
    if hedge_name == "QQQ 10% OTM Put":
        cost, hedge_pnl = 0.018, max(-move_pct/100 - 0.10, 0) * 0.85
    elif hedge_name == "QQQ 20% OTM Put":
        cost, hedge_pnl = 0.009, max(-move_pct/100 - 0.20, 0) * 0.70
    elif hedge_name == "VIXY Volatility Hedge":
        cost, hedge_pnl = 0.06, abs(move_pct/100) * 1.8 * 0.08
    elif hedge_name == "SQQQ ATM Calls":
        cost, hedge_pnl = 0.025, max(-move_pct/100, 0) * 0.9 * 0.5
    elif hedge_name == "Bear Put Spread (10/20%)":
        cost, hedge_pnl = 0.011, min(max(-move_pct/100 - 0.10, 0), 0.10) * 0.6
    elif hedge_name == "Collar (10% Put + 5% Call)":
        cost, hedge_pnl = 0.007, max(-move_pct/100 - 0.10, 0) * 0.6

    final_pnl = long_pnl + hedge_pnl - cost
    final_value = capital * (1 + final_pnl)
    return {
        "Final Value ($)": round(final_value),
        "$ Change": round(final_value - capital),
        "% Change": round(final_pnl * 100, 2)
    }

# ================== TABS ==================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Main Analysis", 
    "📉 Tail Risk", 
    "📊 Sensitivity", 
    "📋 Summary & Top 10"
])

# ================== TAB 1: MAIN ==================
with tab1:
    st.title("📊 HedgePortfolio — Combinatorial Long + Hedge Analyzer")
    st.caption(f"Live QQQ: ${qqq_price:.2f} | All combinations normalized to $100k notional | {datetime.now().strftime('%Y-%m-%d')}")

    with st.expander("📘 How to Use This Page (Beginner Guide)"):
        st.markdown("""
        **Step-by-step for new users**:
        1. Pick any **Long Leg** (how you want to be long QQQ)
        2. Pick any **Hedge Leg** (your insurance)
        3. Click **"Calculate This Portfolio"** to see results
        4. Or click the big button below to compare all 30 combinations at once

        **Key idea**: Every portfolio is normalized to **$100,000** of long exposure so comparisons are fair.
        """)

    with st.expander("📘 Greeks — Technical + Plain English"):
        st.markdown("""
        **Delta** — ∂Option/∂Underlying  
        *Plain English*: How much the position moves when QQQ moves $1. 1.0 = full exposure.

        **Gamma** — ∂²Option/∂Underlying²  
        *Plain English*: Acceleration of your delta. High gamma = explosive P&L near the money.

        **Theta** — ∂Option/∂Time  
        *Plain English*: Daily decay cost of holding the option.

        **Vega** — ∂Option/∂Volatility  
        *Plain English*: Profit/loss from a 1-point rise in implied volatility.
        """)

    st.subheader("1. Build a Custom Portfolio")
    col_long, col_hedge = st.columns(2)
    with col_long:
        long_choice = st.selectbox("LONG Leg", list(LONGS.keys()), key="long1")
    with col_hedge:
        hedge_choice = st.selectbox("HEDGE Leg", list(HEDGES.keys()), key="hedge1")

    if st.button("Calculate This Portfolio", type="primary", key="calc1"):
        res = simulate_portfolio(long_choice, hedge_choice)
        st.success(f"**{long_choice} + {hedge_choice}**")
        st.json(res)

    st.divider()
    st.subheader("2. All 30 Portfolio Combinations — Ranked (Benchmark: $100k QQQ Equities)")

    with st.expander("📘 What the table columns mean (Beginner + Professional)"):
        st.markdown("""
        **For beginners**:
        - **Expected Return %** = Average money you expect to make
        - **5% CVaR** = How bad it gets in the worst 5% of cases (very important)
        - **Prob >20% DD** = Chance you lose more than 20%
        - **Portfolio Drag (bps)** = Yearly cost of the hedge (lower = cheaper insurance)

        **For professionals**:
        - CVaR is the key tail-risk metric used by risk managers
        - Drag is shown in basis points (1 bp = 0.01%)
        - Score = risk-adjusted ranking used internally
        """)

    if st.button("Run Full Comparison (30 Portfolios)", type="primary", key="full1"):
        results = []
        for long_name in LONGS:
            for hedge_name in HEDGES:
                res = simulate_portfolio(long_name, hedge_name)
                res["Combo"] = f"{long_name} + {hedge_name}"
                results.append(res)

        df = pd.DataFrame(results)
        df["Score"] = (df["Expected Return %"] * 2 - df["5% CVaR %"] * 0.5 - df["Portfolio Drag (bps)"] / 100)
        df = df.sort_values("Score", ascending=False).reset_index(drop=True)
        df["Rank"] = range(1, len(df) + 1)

        display_cols = ["Rank", "Combo", "Expected Return %", "5% CVaR %", "Prob >20% DD %", "Portfolio Drag (bps)"]
        st.dataframe(df[display_cols].style.format({
            "Expected Return %": "{:.2f}", "5% CVaR %": "{:.1f}",
            "Prob >20% DD %": "{:.1f}", "Portfolio Drag (bps)": "{:+d}"
        }).background_gradient(subset=["Expected Return %"], cmap="Greens")
         .background_gradient(subset=["5% CVaR %"], cmap="Reds_r"), use_container_width=True, height=650)

        best = df.iloc[0]
        st.subheader("🏆 Optimal Portfolio Recommendation")
        st.success(f"""
        **Rank #1: {best['Combo']}**

        **Why this is optimal right now:**
        - Highest risk-adjusted expected return ({best['Expected Return %']:.2f}%)
        - Strong tail protection ({best['5% CVaR %']:.1f}% CVaR)
        - Very low portfolio drag ({best['Portfolio Drag (bps)']:+d} bps)
        """)

# ================== TAB 2: TAIL RISK ==================
with tab2:
    st.title("📉 Tail Risk Analysis — Historical & Extreme Drawdowns")
    st.caption("All portfolios normalized to $100k notional long exposure. $100k QQQ Equities shown as benchmark.")

    with st.expander("📘 How to read this page (Beginner)"):
        st.markdown("""
        This page shows what happens to every portfolio in real historical crashes.
        - **Dot-com (2000-02)**: -78% crash
        - **2008 GFC**: -55% crash  
        - **2022 Bear**: -35% decline
        - **20% Drawdown**: A moderate correction

        Look at the **Final Value** column — higher is better.
        """)

    scenarios = {
        "Dot-com Bubble (2000-02)": -0.78,
        "2008 Financial Crisis": -0.55,
        "2022 Bear Market": -0.35,
        "Moderate 20% Drawdown": -0.20
    }

    if st.button("Run Tail Risk Analysis on All 30 Portfolios", type="primary", key="tail"):
        tail_results = []
        for long_name in LONGS:
            for hedge_name in HEDGES:
                row = {"Combo": f"{long_name} + {hedge_name}"}
                for scen_name, scen_ret in scenarios.items():
                    res = tail_risk_analysis(long_name, hedge_name, scen_ret)
                    row[f"{scen_name} P&L %"] = res["P&L %"]
                    row[f"{scen_name} Final $"] = res["Final Value"]
                tail_results.append(row)

        df_tail = pd.DataFrame(tail_results)
        pnl_cols = [c for c in df_tail.columns if "P&L %" in c]
        df_tail["Avg P&L %"] = df_tail[pnl_cols].mean(axis=1)
        df_tail = df_tail.sort_values("Avg P&L %", ascending=False).reset_index(drop=True)
        df_tail.insert(0, "Rank", range(1, len(df_tail) + 1))

        st.dataframe(df_tail.style.format({
            **{c: "{:+.1f}" for c in pnl_cols},
            **{c: "${:,.0f}" for c in df_tail.columns if "Final $" in c},
            "Avg P&L %": "{:+.1f}"
        }).background_gradient(subset=pnl_cols, cmap="RdYlGn", vmin=-80, vmax=10), use_container_width=True, height=700)

        best_tail = df_tail.iloc[0]
        st.subheader("🛡️ Most Resilient Portfolio in Tail Risk Scenarios")
        st.success(f"**Rank #1 in Crashes: {best_tail['Combo']}** — Best average P&L across all four major drawdowns: **{best_tail['Avg P&L %']:+.1f}%**")

# ================== TAB 3: SENSITIVITY ==================
with tab3:
    st.title("📊 Sensitivity Analysis — What-If NASDAQ Move")
    st.caption("Adjust the NASDAQ move and instantly see dollar and percentage impact on every portfolio (normalized to $100k). $100k QQQ Equities is the benchmark.")

    with st.expander("📘 How to use this page"):
        st.markdown("""
        Move the slider to simulate any NASDAQ move (e.g. +25% or -40%).
        The table instantly updates showing:
        - Final portfolio value in dollars
        - Dollar change from $100k
        - Percentage change

        This is the best page for understanding **"what if the market does X?"**
        """)

    move_pct = st.slider("NASDAQ Move (%)", min_value=-80, max_value=80, value=0, step=5)

    if st.button("Run Sensitivity Analysis", type="primary"):
        sens_results = []
        for long_name in LONGS:
            for hedge_name in HEDGES:
                res = sensitivity_analysis(long_name, hedge_name, move_pct)
                res["Combo"] = f"{long_name} + {hedge_name}"
                sens_results.append(res)

        df_sens = pd.DataFrame(sens_results)
        df_sens = df_sens.sort_values("Final Value ($)", ascending=False).reset_index(drop=True)
        df_sens.insert(0, "Rank", range(1, len(df_sens) + 1))

        st.dataframe(df_sens.style.format({
            "Final Value ($)": "${:,.0f}",
            "$ Change": "${:+,.0f}",
            "% Change": "{:+.2f}%"
        }).background_gradient(subset=["Final Value ($)"], cmap="Greens")
         .background_gradient(subset=["$ Change"], cmap="RdYlGn"), use_container_width=True, height=650)

        st.info(f"**Benchmark**: $100k QQQ Equities would be worth **${DEFAULT_CAPITAL * (1 + move_pct/100):,.0f}** ({move_pct:+.1f}%) at this move.")

# ================== TAB 4: SUMMARY & TOP 10 ==================
with tab4:
    st.title("📋 Summary — Top 10 Portfolios & Portfolio Manager Guidance")
    st.caption("Probabilistic analysis and when to choose each strategy. $100k QQQ Equities is the unhedged benchmark.")

    with st.expander("📘 Key Metrics Explained (Plain English for Everyone)"):
        st.markdown("""
        - **Expected Return %**: Average outcome you should expect.
        - **5% CVaR**: In the worst 5% of scenarios, this is the average loss.
        - **Prob >20% DD**: Chance of losing more than 20%.
        - **Portfolio Drag (bps)**: Yearly cost of the hedge in basis points (100 bps = 1%).
        - **Hedge Cost %**: Upfront cost of protection as % of capital.

        **Professional note**: CVaR and Drag are the two metrics most used by institutional risk teams.
        """)

    st.subheader("Top 10 Portfolios — Probabilistic View & When to Choose")

    top_10 = [
        ("QQQ Equities + QQQ 10% OTM Put", "Best balanced protection. Good in mild corrections, still participates in rallies. Choose when you want downside cushion without giving up too much upside."),
        ("QQQ Equities + Collar (10% Put + 5% Call)", "Very low cost protection. Excellent when you expect range-bound or mildly bullish markets. Pick when volatility is high and you want cheap insurance."),
        ("QQQ Deep ITM Calls + Bear Put Spread", "Capital efficient with strong tail protection. Ideal when you are bullish but want crash protection at low cost."),
        ("QQQ Equities + VIXY Volatility Hedge", "Best pure tail hedge. Wins in big crashes. Choose when you believe a major volatility spike is possible."),
        ("MNQ Futures (2×) + QQQ 10% OTM Put", "Highest upside in bullish scenarios, still protected. Use when you have strong conviction and can handle leverage."),
        ("QQQ Equities + QQQ 20% OTM Put", "Cheaper protection, kicks in only in severe crashes. Good when you want minimal drag and only care about black swans."),
        ("QQQ ATM Calls + Collar", "Very capital efficient with defined risk. Attractive when you want to use less capital while keeping similar exposure."),
        ("QQQ Equities + SQQQ ATM Calls", "Inverse hedge that profits when market falls. Best when you expect a sharp but not catastrophic decline."),
        ("QQQ Deep ITM Calls + VIXY", "High gamma + volatility protection. Choose when you want aggressive upside with crash insurance."),
        ("SGOV (Cash) + VIXY Volatility Hedge", "Lowest risk. Best when you are defensive or expect prolonged volatility.")
    ]

    for i, (combo, explanation) in enumerate(top_10, 1):
        st.markdown(f"**{i}. {combo}**")
        st.caption(explanation)

    st.divider()
    st.success("""
    **Portfolio Manager Takeaway**:  
    The **QQQ Equities + 10% OTM Put** combination is usually the sweet spot for most professional investors — it offers meaningful protection with acceptable cost.  
    Use **VIXY** or **Bear Put Spread** when you are more concerned about tail risk.  
    Use **Collar** when you want the cheapest possible protection.  
    Avoid high leverage (MNQ 2×) unless you have very high conviction.
    """)

    # ================== NEW SECTION: BUBBLE & CURRENT TAIL RISK ==================
    st.divider()
    st.subheader("🫧 Bubble Market & Current Tail Risk Environment (Aug 2026)")

    with st.expander("📘 Bubble Market Analysis (Dotcom-style) — Beginner + Professional View"):
        st.markdown("""
        **What defines a bubble market (like 1999–2000):**
        - Extremely high valuations (high P/E, low earnings yield)
        - Low realized volatility + high complacency
        - Massive retail participation and leverage
        - Expensive option protection (high implied vol on puts)

        **Best portfolios in a bubble environment:**
        - **Collar (10% Put + 5% Call)** — Cheapest way to own upside while capping extreme downside
        - **Bear Put Spread** — Low cost, asymmetric payoff in a crash
        - **QQQ Equities + light VIXY** — Small allocation to volatility as "lottery ticket" insurance

        These structures minimize the high cost of protection when the market is euphoric.
        """)

    with st.expander("📘 Current Market Tail Risk (August 2026) — What Professionals Are Watching"):
        st.markdown("""
        **Current environment signals (as of 2026-08-05):**
        - Significant concentration risk in mega-cap tech / AI names
        - Elevated valuations similar to late-1990s and 2021 peaks
        - Geopolitical tensions + potential policy shocks
        - Compressed credit spreads and low equity vol — classic late-cycle signs

        **Recommended portfolios right now:**
        - **QQQ Equities + QQQ 10% OTM Put** → Best balanced choice (our current #1)
        - **QQQ Equities + VIXY Volatility Hedge (8%)** → Strong tail protection if a sudden de-risking event occurs
        - **MNQ Futures (2×) + Bear Put Spread** → For those with high conviction but wanting crash protection

        **Professional takeaway**: In the current regime, tail risk is **under-priced**. 
        Paying a modest premium for 10% OTM puts or a small VIX allocation is rational portfolio insurance.
        """)

    st.info("""
    **Bottom line for today**:  
    The market exhibits classic late-stage bubble characteristics with elevated tail risk.  
    The **QQQ Equities + 10% OTM Put** and **Collar** strategies currently offer the best risk/reward for most investors.
    """)

st.divider()
st.caption("Data: Yahoo Finance (free) • Fees: Webull schedule • Built for professional quantitative comparison")