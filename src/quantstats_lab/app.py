"""Interactive Streamlit UI. Run: streamlit run src/quantstats_lab/app.py"""

from __future__ import annotations

import io
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from quantstats_lab import (
    autoregressive_one,
    benjamini_hochberg,
    bootstrap_mean_interval,
    bootstrap_returns,
    drawdown_series,
    evaluate_distribution,
    geometric_brownian_motion,
    historical_var_es,
    make_distribution,
    one_sample_ttest,
    ornstein_uhlenbeck,
    performance_metrics,
    t_mean_interval,
)

ACKNOWLEDGEMENT = (
    "Created by Yuvi with the assistance of AI (OpenAI ChatGPT) "
    "for software development, testing, and documentation."
)


def demo_returns(seed: int = 42, periods: int = 504) -> np.ndarray:
    """Synthetic example only; do not confuse simulated data with real market history."""
    return np.random.default_rng(seed).normal(0.0003, 0.012, size=periods)


def metric_columns(items: list[tuple[str, str]]) -> None:
    for col, (label, value) in zip(st.columns(len(items)), items, strict=True):
        col.metric(label, value)


def plot_simulation(paths: np.ndarray, title: str) -> go.Figure:
    fig = go.Figure()
    x = np.arange(paths.shape[1])
    p05, p50, p95 = np.quantile(paths, [0.05, 0.5, 0.95], axis=0)
    fig.add_trace(go.Scatter(x=x, y=p95, name="95th percentile", line_color="#64748b", line_width=0))
    fig.add_trace(go.Scatter(x=x, y=p05, name="5–95% band", fill="tonexty", fillcolor="rgba(56,189,248,0.2)", line_color="#64748b", line_width=0))
    fig.add_trace(go.Scatter(x=x, y=p50, name="Median path", line_color="#38bdf8", line_width=3))
    for path in paths[: min(12, len(paths))]:
        fig.add_trace(go.Scatter(x=x, y=path, mode="lines", line_color="rgba(148,163,184,0.20)", showlegend=False))
    fig.update_layout(title=title, xaxis_title="Steps", yaxis_title="Simulated value", height=440)
    return fig


def parse_csv_returns(uploaded: Any) -> tuple[np.ndarray, str]:
    raw = uploaded.getvalue()
    if len(raw) > 5_000_000:
        raise ValueError("CSV exceeds 5 MB. Please select a smaller file.")
    try:
        df = pd.read_csv(io.BytesIO(raw), nrows=100_001)
    except (UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise ValueError("The file is not a readable CSV") from exc
    if len(df) > 100_000:
        raise ValueError("CSV exceeds the 100,000-row analysis limit")
    numeric_columns = []
    for col in df.columns:
        try:
            pd.to_numeric(df[col], errors="raise")
            numeric_columns.append(col)
        except (TypeError, ValueError):
            continue
    if not numeric_columns:
        raise ValueError("No numeric columns found. Provide simple returns as decimal values.")
    chosen = st.selectbox("Column with simple returns (0.01 = 1%)", numeric_columns)
    if df[chosen].isna().any():
        raise ValueError("The selected column contains missing values; clean them first")
    return df[chosen].to_numpy(dtype=np.float64), chosen


def distributions_tab() -> None:
    st.subheader("Probability distributions")
    st.caption("Density or probability mass, cumulative probability, survival probability, and quantiles.")
    kind = st.selectbox("Distribution", ["normal", "student_t", "binomial", "poisson", "exponential", "lognormal"])
    with st.form("distribution_form"):
        if kind == "normal":
            parameters = {"mean": st.number_input("Mean", value=0.0), "std": st.number_input("Standard deviation", min_value=0.001, value=1.0)}
            x = st.number_input("Evaluate at x", value=0.0)
        elif kind == "student_t":
            parameters = {"df": st.number_input("Degrees of freedom", min_value=0.01, value=5.0), "loc": st.number_input("Location", value=0.0), "scale": st.number_input("Scale", min_value=0.001, value=1.0)}
            x = st.number_input("Evaluate at x", value=0.0)
        elif kind == "binomial":
            parameters = {"n": st.number_input("Trials", min_value=0, max_value=100000, value=20), "p": st.slider("Success probability", 0.0, 1.0, 0.5)}
            x = st.number_input("Evaluate at x", value=10, step=1)
        elif kind == "poisson":
            parameters = {"rate": st.number_input("Rate λ", min_value=0.001, value=5.0)}
            x = st.number_input("Evaluate at x", value=5, step=1)
        elif kind == "exponential":
            parameters = {"scale": st.number_input("Scale", min_value=0.001, value=1.0)}
            x = st.number_input("Evaluate at x", value=1.0)
        else:
            parameters = {"shape": st.number_input("Log shape (σ)", min_value=0.001, value=0.5), "scale": st.number_input("Scale", min_value=0.001, value=1.0)}
            x = st.number_input("Evaluate at x", value=1.0)
        run = st.form_submit_button("Calculate distribution", type="primary")
    if not run:
        return
    try:
        result = evaluate_distribution(kind, x, **parameters)
        frozen, discrete = make_distribution(kind, **parameters)
        metric_columns([("PDF / PMF", f"{result.mass_or_density:.5g}"), ("CDF", f"{result.cdf:.5g}"), ("P(X > x)", f"{result.survival:.5g}")])
        st.write(f"**Mean:** {result.mean:.5g} · **SD:** {result.standard_deviation:.5g} · **5–95% quantiles:** {result.q05:.5g} to {result.q95:.5g}")
        if not np.isfinite(result.mean) or not np.isfinite(result.standard_deviation):
            st.info("This parameterisation has undefined mean or variance; NaN denotes an undefined moment.")
        low, high = float(frozen.ppf(0.001)), float(frozen.ppf(0.999))
        if discrete:
            a, b = max(0, int(np.floor(low))), int(np.ceil(high))
            xx = np.unique(np.linspace(a, b, min(201, b - a + 1)).astype(int))
            fig = px.bar(x=xx, y=frozen.pmf(xx), labels={"x": "Outcome", "y": "Probability mass"}, title="Probability mass function")
        else:
            xx = np.linspace(low, high, 400)
            fig = px.line(x=xx, y=frozen.pdf(xx), labels={"x": "Value", "y": "Probability density"}, title="Probability density function")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Probability density is not a probability; integrate the density over a range to obtain one.")
    except (ValueError, OverflowError) as exc:
        st.error(str(exc))


def monte_carlo_tab(seed: int) -> None:
    st.subheader("Monte Carlo laboratory")
    st.caption("Reproducible geometric Brownian motion; parameters are assumptions, not return forecasts.")
    with st.form("gbm_form"):
        c1, c2, c3 = st.columns(3)
        initial = c1.number_input("Initial value", min_value=0.01, value=100.0)
        drift = c2.number_input("Annual drift (e.g. 0.06)", value=0.06, step=0.01)
        volatility = c3.number_input("Annual volatility", value=0.2, min_value=0.0, step=0.01)
        steps = st.slider("Steps (trading days)", 10, 1000, 252)
        count = st.slider("Simulation paths", 100, 2000, 500, step=100)
        run = st.form_submit_button("Run Monte Carlo", type="primary")
    if not run:
        return
    try:
        result = geometric_brownian_motion(initial, drift, volatility, steps=steps, paths=count, seed=seed)
        metric_columns([("Terminal mean", f"{result.terminal_mean:.2f}"), ("Terminal median", f"{result.terminal_median:.2f}"), ("5–95% terminal", f"{result.terminal_p05:.2f} – {result.terminal_p95:.2f}")])
        st.plotly_chart(plot_simulation(result.paths, "GBM simulation fan chart"), use_container_width=True)
        final = pd.DataFrame({"simulation_id": np.arange(1, count + 1), "terminal_value": result.paths[:, -1]})
        st.download_button("Download terminal outcomes (CSV)", final.to_csv(index=False), file_name="gbm_terminal_values.csv", mime="text/csv")
        st.warning("These are model-generated outcomes under constant drift and volatility. They are not calibrated forecasts or investment advice.")
    except (ValueError, OverflowError) as exc:
        st.error(str(exc))


def inference_tab(seed: int) -> None:
    st.subheader("Statistical inference")
    st.caption("Compare a Student-t interval with an IID percentile bootstrap; test the sample mean.")
    values_text = st.text_area("Comma-separated observations", value="0.2, 0.4, -0.1, 0.8, 0.5, 0.0, 0.3, 0.2", height=100)
    confidence = st.slider("Confidence level", 0.8, 0.99, 0.95, step=0.01)
    resamples = st.slider("Bootstrap resamples", 500, 10000, 3000, step=500)
    null = st.number_input("Hypothesised population mean", value=0.0)
    if st.button("Run inference", type="primary"):
        try:
            data = np.array([float(item.strip()) for item in values_text.split(",")], dtype=float)
            classical = t_mean_interval(data, confidence)
            boot = bootstrap_mean_interval(data, confidence=confidence, resamples=resamples, seed=seed)
            hypothesis = one_sample_ttest(data, null_mean=null)
            st.dataframe(pd.DataFrame([
                {"Method": classical.method, "Mean": classical.estimate, "Lower": classical.lower, "Upper": classical.upper},
                {"Method": boot.method, "Mean": boot.estimate, "Lower": boot.lower, "Upper": boot.upper},
            ]), hide_index=True, use_container_width=True)
            metric_columns([("t statistic", f"{hypothesis.statistic:.4g}"), ("Two-sided p-value", f"{hypothesis.p_value:.5g}"), ("Sample size", str(len(data)))])
            st.info("The p-value is conditional on the null model. It is not the probability that the null hypothesis is true.")
            st.caption("Both intervals assume independent observations. For dependent financial returns, use appropriate time-series methods; this IID bootstrap can understate uncertainty.")
        except (ValueError, OverflowError) as exc:
            st.error(f"Check your observations: {exc}")
    with st.expander("Multiple-testing adjustment (Benjamini–Hochberg)"):
        p_text = st.text_input("Comma-separated p-values", value="0.001, 0.02, 0.03, 0.4")
        if st.button("Adjust p-values"):
            try:
                raw = [float(item.strip()) for item in p_text.split(",")]
                adjusted = benjamini_hochberg(raw)
                st.dataframe(pd.DataFrame({"raw_p": raw, "BH_adjusted_p": adjusted}), hide_index=True)
            except ValueError as exc:
                st.error(str(exc))


def processes_tab(seed: int) -> None:
    st.subheader("Stochastic processes")
    mode = st.radio("Model", ["Ornstein–Uhlenbeck", "AR(1)"], horizontal=True)
    with st.form("processes_form"):
        c1, c2, c3 = st.columns(3)
        initial = c1.number_input("Initial state", value=1.0)
        mean = c2.number_input("Long-run mean", value=0.0)
        steps = c3.number_input("Steps", min_value=5, max_value=1000, value=252, step=1)
        if mode == "Ornstein–Uhlenbeck":
            theta = st.number_input("Mean-reversion speed (annual)", min_value=0.001, value=3.0)
            vol = st.number_input("Diffusion volatility (annual)", min_value=0.0, value=0.6)
        else:
            theta = st.slider("AR coefficient φ", -0.99, 0.99, 0.85, step=0.01)
            vol = st.number_input("Innovation standard deviation", min_value=0.0, value=0.3)
        run = st.form_submit_button("Simulate process", type="primary")
    if not run:
        return
    try:
        if mode == "Ornstein–Uhlenbeck":
            paths = ornstein_uhlenbeck(initial, mean, theta, vol, steps=steps, seed=seed)
        else:
            paths = autoregressive_one(initial, mean, theta, vol, steps=steps, seed=seed)
        st.plotly_chart(plot_simulation(paths, f"{mode} sample paths"), use_container_width=True)
        st.caption("OU uses exact transitions with dt = 1/252 years; AR(1) uses discrete steps. These are state processes, not automatically valid price models.")
    except (ValueError, OverflowError) as exc:
        st.error(str(exc))


def risk_tab(seed: int) -> None:
    st.subheader("Historical risk analytics")
    st.caption("Supply a CSV of simple period returns, or use synthetic demonstration data.")
    uploaded = st.file_uploader("Upload CSV (≤5 MB, ≤100,000 rows)", type="csv")
    try:
        if uploaded:
            returns, name = parse_csv_returns(uploaded)
            st.info(f"Using uploaded column: {name}. Check that it contains decimal simple returns, not prices or percentages.")
        else:
            returns = demo_returns(seed)
            st.info("Using **synthetic sample returns**, not real market data. Upload your own CSV for actual observations.")
        confidence = st.slider("Tail confidence", 0.8, 0.99, 0.95, step=0.01)
        periods = st.selectbox("Periods per year", [252, 365, 52, 12], index=0)
        risk = historical_var_es(returns, confidence=confidence)
        perf = performance_metrics(returns, periods_per_year=periods)
        metric_columns([("Historical VaR", f"{risk.value_at_risk:.2%}"), ("Historical ES", f"{risk.expected_shortfall:.2%}"), ("Max drawdown", f"{perf.maximum_drawdown:.2%}")])
        metric_columns([("Annualised return", f"{perf.annualised_return:.2%}"), ("Annualised volatility", f"{perf.annualised_volatility:.2%}"), ("Sharpe", "Undefined" if perf.annualised_sharpe is None else f"{perf.annualised_sharpe:.2f}")])
        chart = pd.DataFrame({"Observation": np.arange(len(returns) + 1), "Drawdown": drawdown_series(returns)})
        st.plotly_chart(px.area(chart, x="Observation", y="Drawdown", title="Underwater (drawdown) chart"), use_container_width=True)
        st.download_button("Download risk metrics (CSV)", pd.DataFrame([{"VaR": risk.value_at_risk, "ES": risk.expected_shortfall, "Maximum drawdown": perf.maximum_drawdown, "Annualised volatility": perf.annualised_volatility, "Annualised return": perf.annualised_return}]).to_csv(index=False), file_name="risk_metrics.csv", mime="text/csv")
        st.caption("Risk metrics describe the supplied observations; they are not reliable tail-risk forecasts. Annualisation assumes equally spaced observations. Returns must be in decimal units.")
        if st.checkbox("Show IID bootstrap alternative"):
            simulation = bootstrap_returns(returns, paths=300, steps=252, seed=seed)
            st.plotly_chart(plot_simulation(simulation.paths, "IID resampled-return paths"), use_container_width=True)
            st.warning("IID bootstrap discards time dependence and volatility clustering; not suitable for every market regime.")
    except (ValueError, OverflowError, TypeError) as exc:
        st.error(f"Unable to analyse returns: {exc}")


def main() -> None:
    st.set_page_config(page_title="QuantStats Lab", page_icon="📈", layout="wide")
    st.markdown("""<style>
    .block-container {max-width: 1150px; padding-top: 2rem}
    h1 {letter-spacing: -0.035em}
    [data-testid="stMetricValue"] {font-size: 1.6rem}
    </style>""", unsafe_allow_html=True)
    st.title("QuantStats Lab")
    st.markdown("**Reproducible probability, statistical inference, and risk experimentation.**")
    st.sidebar.header("Research settings")
    seed = st.sidebar.number_input("Random seed", min_value=0, max_value=2**32 - 1, value=42, step=1)
    st.sidebar.caption("Same seed + inputs → same pseudo-random simulations. No market-data subscription or login required.")
    st.sidebar.markdown("---")
    st.sidebar.caption("Local-first calculations. Uploaded data are processed in this app session. Do not upload confidential data to third-party-hosted deployments.")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Distributions", "Monte Carlo", "Inference", "Processes", "Risk lab", "About"])
    with tab1:
        distributions_tab()
    with tab2:
        monte_carlo_tab(seed)
    with tab3:
        inference_tab(seed)
    with tab4:
        processes_tab(seed)
    with tab5:
        risk_tab(seed)
    with tab6:
        st.subheader("Open-source research tools, not trading signals")
        st.write("QuantStats Lab v0.1.0 provides transparent educational and research calculations. Always check modelling assumptions before using numerical output in a decision.")
        st.markdown("[Source and issues](https://github.com/yuvsta1/quantstats-lab)")
        st.caption(ACKNOWLEDGEMENT)
    st.divider()
    st.caption(f"QuantStats Lab v0.1.0 · MIT License · {ACKNOWLEDGEMENT}")


if __name__ == "__main__":
    main()