# Release readiness and quality gates

> Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

## Mandatory automated checks

Run the following from a clean Python virtual environment:

```bash
python -m pip install -e ".[app,dev]"
ruff check .
pytest --cov=quantstats_lab --cov-report=term-missing
python -m build
python examples/research_walkthrough.py
```

CI exercises Python 3.11, 3.12, and 3.13. Numerical-library coverage below 85% should fail; the optional web app is excluded from that percentage and gets its own Streamlit AppTest smoke test. This measures executed lines/branches, **not** financial correctness.

Numerical unit tests verify distributions against frozen SciPy models, Student-t confidence intervals and tests against SciPy, deterministic GBM and OU trajectories against closed-form solutions, empirical bootstrap against a separate sample implementation, and historical tail-risk examples against hand-calculated reference values. Regression tests cover drawdown and p-value monotonicity.

## Interactive application smoke test (manual)

Run `streamlit run src/quantstats_lab/app.py` with the `[app]` extra installed, then:

1. **Distributions:** select each of the six distribution families; check PDF/PMF, CDF, SF and plot render; try Student-t `df=0.5` to confirm undefined moments are clearly labelled.
2. **Monte Carlo:** run twice with identical seed; verify graph and downloaded CSV identical. Change seed; verify terminal observations differ.
3. **Inference:** paste values, run t and bootstrap intervals; expand BH adjustment and compare output with a hand-worked example.
4. **Processes:** select OU and AR(1); run and check plots. Verify changing parameters changes path behaviour.
5. **Risk lab:** run synthetic data, upload `examples/sample_returns.csv`, verify the supplied numeric column is recognised, and export risk metrics. Check erroneous CSV gives an actionable error.
6. **Accessibility and layout:** test keyboard navigation, text zoom (200%), mobile-width responsiveness, readable chart labels and contrast; log any issues.
7. **Privacy:** verify no third-party data API calls, secrets, account requirements, or embedded tracking scripts were introduced.

**Important:** Automated library tests do not establish that every browser/UI workflow works on all browsers. Do not report manual smoke tests as passed until someone actually performs them.

## Known design limitations

- This is initial research/educational software, not audited risk infrastructure.
- No volatility clustering, jump diffusion, block bootstrap, factor models, dynamic interest rates, or market-data connectors.
- Backtesting and portfolio optimisation are out of scope.
- No live hosted deployment is configured by this repository.
- CSV parsing limits file size and row count but cannot determine whether the supplied numbers are correctly sourced returns.
- CI dependency ranges allow compatible minor updates; reproducible deployments should create and review a lockfile separately.

## Release process

1. Review `docs/MATH.md` and test results; resolve any failing checks.
2. Verify package build and local app launch on a clean environment.
3. Merge to `main` only after reviewing the PR and CI results.
4. Tag an initial `v0.1.0` release and include the AI assistance disclosure in the release description.
5. Keep a changelog for subsequent releases; solicit external issues and user feedback.