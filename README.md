# QuantStats Lab

**Reproducible probability, statistical inference, stochastic-process simulation and risk analytics for quant research.**

> **AI development disclosure:** Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

**Status:** `v0.2.1` — native multi-platform quantitative workbench. Python 3.11–3.15. MIT licence. No trading signals, broker connections, market-data subscriptions or paid accounts.

QuantStats Lab couples a **small, typed Python calculation library** with **native Windows, macOS and Linux desktop applications** and an optional legacy **interactive Streamlit interface**. It is designed for students, researchers, quantitative developers and traders wanting transparent assumptions, seeded simulations and simple ways to inspect risks or probability models.

## Why use it?

- **Reproduce your experiments:** same inputs and seed give the same Monte Carlo or bootstrap draws.
- **Use actual library functions:** the Streamlit front end calls the package's public API; calculations are not duplicated in UI code.
- **Inspect the assumptions:** annualised GBM parameters, IID bootstrap, Student-t confidence intervals, and tail-risk definitions are explicit.
- **Export results:** terminal Monte Carlo outcomes and risk metrics can be downloaded as CSV.
- **Bring your own returns:** import a simple-return CSV without needing a market-data API.

This tool deliberately focuses on **learning and experimentation rather than backtest reporting**. If you need a comprehensive portfolio tear sheet, [QuantStats](https://github.com/ranaroussi/quantstats) is a more mature option. For wide-ranging distribution fitting and copulas, [ProbViz](https://github.com/sanskarpan/probviz) offers a broader toolkit. The name *QuantStats Lab* denotes a separate independent project, not an affiliate of either.

## Features

| Module | Public API | Desktop and legacy browser UI |
| --- | --- | --- |
| Probability | Normal, Student-t, binomial, Poisson, exponential and lognormal PDF/PMF, CDF, SF, quantiles | Graph distributions and inspect statistics |
| Monte Carlo | Exact-timestep geometric Brownian motion; independent resampling of supplied return observations | Run and visualise scenario fans, export terminal outcomes |
| Inference | Student-t mean intervals, IID percentile bootstrap, one-sample t-test, Welch t-test, BH multiple-testing correction | Enter observations, compare interval methods and tests |
| Processes | Exact Ornstein–Uhlenbeck transitions and stationary AR(1) simulations | Explore convergence and random paths |
| Risk analytics | Empirical VaR/expected shortfall, Sharpe ratio, volatility, total/annualised return, maximum drawdown | Import CSV, view metrics/drawdown, export metrics |

## Download the desktop app — Windows, macOS and Linux

**v0.2.1 UI refresh:** tighter spacing, clear numeric inputs without spinner dots, compact plot controls, model-aware fields, better contrast for dropdown menus and consistent light/dark themes.

**[Download the latest version from GitHub Releases](https://github.com/yuvsta1/quantstats-lab/releases/latest)**

Choose the file matching your computer. These are real standalone native desktop applications, not browser-based apps. Python does **not** need to be installed separately to run them.

| Platform | Download file | Install and launch |
| --- | --- | --- |
| **Windows 10/11, x64** | `QuantStats-Lab-vX.Y.Z-Windows-x64.exe` | Download and double-click the executable. No Python or Terminal needed. Unsigned downloads can prompt SmartScreen. |
| **Mac with Apple Silicon (M1/M2/M3/M4/M5)** | `QuantStats-Lab-vX.Y.Z-macOS-Apple-Silicon.zip` | Unzip, drag `QuantStats Lab.app` into Applications, double-click. |
| **Mac with Intel processor** | `QuantStats-Lab-vX.Y.Z-macOS-Intel.zip` | Unzip, drag `QuantStats Lab.app` into Applications, double-click. |
| **Ubuntu/Debian Linux, x64** | `QuantStats-Lab-vX.Y.Z-Linux-x64.deb` | Open the .deb using your software installer, then launch from the app menu. |
| **Other compatible x64 Linux distributions** | `QuantStats-Lab-vX.Y.Z-Linux-x64.tar.gz` | Extract and launch `QuantStatsLab/QuantStatsLab`. Linux library compatibility varies. |

`X.Y.Z` is replaced by the actual release version, beginning at **v0.2.0**. Releases remain available at [Releases](https://github.com/yuvsta1/quantstats-lab/releases), and the `/releases/latest` link always points to the newest stable version.

**Security:** The first development release is unsigned/unnotarised. Windows SmartScreen or Apple Gatekeeper may warn or block the binary; only open it if you trust the repository. Avoid turning off system security globally. Release signing/notarisation is documented in [desktop release guidance](docs/DESKTOP.md).

### Run from Python source (optional)

The source package supports Python **3.11–3.15**, including the current stable **Python 3.15**. Developers may run:

```bash
python -m pip install -e ".[desktop,dev]"
python -m quantstats_lab.desktop
```

The packaged apps bundle Python and their dependencies so **users do not need a Python installation**. The original Streamlit browser interface remains available as a legacy optional extra.

## Install and launch the legacy browser interface

The source library targets Python 3.11–3.15; standalone release builds use Python 3.15.

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
src/quantstats_lab/     Reusable numerical library, native Qt desktop and legacy Streamlit app
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