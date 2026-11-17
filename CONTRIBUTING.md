# Contributing to QuantStats Lab

Thanks for considering a contribution. The most useful early contributions are reproducible numerical bugs, tests against independent references, improved mathematical explanations, accessibility fixes, and genuine research use cases.

> Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

## How to contribute

1. Search open issues before opening a new one.
2. For bugs, provide a minimal input, observed vs expected result, Python/package versions and a trusted reference when mathematics is involved. Remove personal or confidential datasets.
3. For new functionality, first describe the real user problem and modelling assumptions.
4. Work in a focused branch; add tests for any new numerical behaviour.
5. Run `ruff check .` and `pytest --cov=quantstats_lab --cov-report=term-missing` before submitting a PR.
6. Explain any numerical assumptions, units, convention changes, backwards compatibility and potential user-facing effect.
7. Keep AI-assistance attribution transparent. Contributors should not claim manual authorship or review of work they did not perform.

## Code style

Prefer small pure functions, typed arguments/returns, rigorous validation, deterministic tests, public docstrings, and clear errors. Do not silently impute invalid observations. Do not introduce network requests, trackers or secrets without a compelling reason and approval.

## Scientific integrity

Tests must not be weakened merely to obtain a passing run. Distinguish analytical identities from statistical Monte Carlo tolerances, and be explicit about estimator bias, independence assumptions and sample sizes. Do not advertise simulated performance as predicted investment returns.