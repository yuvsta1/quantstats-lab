# Verification record — 17 November 2026

> Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

This is a record of *local* evidence, not certification or an assertion of zero defects.

## Verified locally

- Environment: Python 3.13.5; NumPy 2.3.5; SciPy 1.17.0; pytest 9.0.2; pandas 2.2.3; Plotly 6.5.2.
- Numerical and app-component tests: **98 passed**. Optional Streamlit app test: **1 skipped** because Streamlit could not be installed in the available environment.
- Numerical package (`src/quantstats_lab` excluding optional `app.py`) branch/statement aggregate coverage: **95.84%**.
- `python examples/research_walkthrough.py` executed and generated finite risk and Monte Carlo outputs.
- A wheel built successfully with setuptools and was installed into a separate target folder; import and sample calculations succeeded.
- All Python source compiled successfully.

## Not verified in this environment

- Ruff lint output (Ruff could not be installed offline).
- Streamlit application launch in a real browser or `streamlit.testing` AppTest (Streamlit unavailable offline).
- GitHub-hosted CI runs, repository creation/publication, branch protection or GitHub releases.
- Third-party dependency vulnerability scan or any production hosting.
- Independent external user adoption and usage statistics.

Do **not** describe this repository as fully deployed or all quality gates passed until the above missing checks are completed.