# QuantStats Lab

**Reproducible probability, statistical inference, stochastic-process simulation and risk analytics for quant research.**

> **AI development disclosure:** Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

**Status:** `v0.1.0` — initial open-source release candidate. Python 3.11–3.13. MIT licence. No trading signals, broker connections, market-data subscriptions or paid accounts.

QuantStats Lab couples a **small, typed Python calculation library** with an optional **interactive Streamlit interface**. It is designed for students, researchers, quantitative developers and traders wanting transparent assumptions, seeded simulations and simple ways to inspect risks or probability models.

## Why use it?

- **Reproduce your experiments:** same inputs and seed give the same Monte Carlo or bootstrap draws.
- **Use actual library functions:** the Streamlit front end calls the package's public API; calculations are not duplicated in UI code.
- **Inspect the assumptions:** annualised GBM parameters, IID bootstrap, Student-t confidence intervals, and tail-risk definitions are explicit.
- **Export results:** terminal Monte Carlo outcomes and risk metrics can be downloaded as CSV.
- **Bring your own returns:** import a simple-return CSV without needing a market-data API.

This tool deliberately focuses on **learning and experimentation rather than backtest reporting**. If you need a comprehensive portfolio tear sheet, [QuantStats](https://github.com/ranaroussi/quantstats) is a more mature option. For wide-ranging distribution fitting and copulas, [ProbViz](https://github.com/sanskarpan/probviz) offers a broader toolkit. The name *QuantStats Lab* denotes a separate independent project, not an affiliate of either.

## Features

| Module | Public API | Web interface |
| --- | --- | --- |
| Probability | Normal, Student-t, binomial, Poisson, exponential and lognormal PDF/PMF, CDF, SF, quantiles | Graph distributions and inspect statistics |
| Monte Carlo | Exact-timestep geometric Brownian motion; independent resampling of supplied return observations | Run and visualise scenario fans, export terminal outcomes |
| Inference | Student-t mean intervals, IID percentile bootstrap, one-sample t-test, Welch t-test, BH multiple-testing correction | Enter observations, compare interval methods and tests |
| Processes | Exact Ornstein–Uhlenbeck transitions and stationary AR(1) simulations | Explore convergence and random paths |
| Risk analytics | Empirical VaR/expected shortfall, Sharpe ratio, volatility, total/annualised return, maximum drawdown | Import CSV, view metrics/drawdown, export metrics |

## Install and launch

Requires Python 3.11+.

```bash
# Clone https://github.com/yuvsta1/quantstats-lab and enter its root:
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[app]"
streamlit run src/quantstats_lab/app.py
```

Open the local address that Streamlit reports (usually `http://localhost:8501`). No API keys required.

**Library-only installation** (does not install Streamlit, pandas or Plotly):

```bash
python -m pip install -e .
```

## Python in 60 seconds

```python
import numpy as np
from quantstats_lab import (
    bootstrap_mean_interval,
    geometric_brownian_motion,
    historical_var_es,
    performance_metrics,
)

rng = np.random.default_rng(2026)
returns = rng.normal(0.0002, 0.01, size=504)  # synthetic example, NOT actual history

print(bootstrap_mean_interval(returns, seed=2026))
print(historical_var_es(returns, confidence=0.95))
print(performance_metrics(returns, periods_per_year=252))

paths = geometric_brownian_motion(
    initial=100.0, annual_drift=0.06, annual_volatility=0.20,
    steps=252, paths=1_000, seed=2026,
)
print(paths.terminal_p05, paths.terminal_median, paths.terminal_p95)
```

For a runnable standalone example, use:

```bash
python examples/research_walkthrough.py
```

## CSV format

A risk-series CSV must contain a numeric column of **simple period returns in decimals**, not prices or whole percentages:

```csv
return
0.012
-0.009
0.003
0.004
```

Example file: [`examples/sample_returns.csv`](examples/sample_returns.csv). A decimal value of `0.012` means **1.2%** for one period. The app allows the user to choose among numeric columns and rejects missing observations, infinity, values below −100%, excessive file sizes and insufficient observations. No automatic cleaning occurs.

**Data and privacy:** calculations happen in the running app process. If you deploy to a third-party host, do not upload confidential data without reviewing the host's retention/security policies. There is no account registration, analytics, or external data collection code in this project.

## Mathematical specifications

See [`docs/MATH.md`](docs/MATH.md) for exact formulas, numerical conventions, confidence-interval assumptions, failure cases, and important limitations.

The tools are **descriptive or model-based**. Results should not be described as predictions, guaranteed portfolio performance, validated alpha, or professional financial advice.

## Development and verification

```bash
python -m pip install -e ".[app,dev]"
ruff check .
python -m pytest --cov=quantstats_lab --cov-report=term-missing
python -m build
```

CI (`.github/workflows/ci.yml`) runs lint, unit/integration tests, a coverage threshold, and package build checks on multiple supported Python versions. Static inspection does not replace interactive browser testing; see [`docs/QUALITY.md`](docs/QUALITY.md) for the manual smoke-test checklist.

Before using quantitative outputs in high-consequence decisions, independently verify the specific function and dataset. Seeded Monte Carlo reproducibility does not imply modelling validity.

## Project layout

```text
src/quantstats_lab/     Pure-Python-facing numerical library plus optional Streamlit app
examples/               Runnable Python research workflow and sample CSV
tests/                  Numerical references, regressions, validation and integration checks
docs/                   Mathematics, quality assurance and release guidance
.github/                CI, dependency updates, issue templates
```

## Contribute

Feedback from independent researchers and developers is welcome. If there is a reproducible bug or a mathematical convention you think should change, open an issue using the bug/feature templates. Before contributing, read [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), and [`SECURITY.md`](SECURITY.md).

## Licence and attribution

MIT-licensed (see [`LICENSE`](LICENSE)). This codebase is separate from, and does not copy code from, the existing QuantStats or ProbViz projects.

**Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.**