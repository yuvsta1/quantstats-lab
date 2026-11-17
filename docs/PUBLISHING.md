# Publishing checklist and repository metadata

> Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

This source bundle does **not** prove that a GitHub repository, CI run, Streamlit deployment or PyPI release exists. These external steps must be completed and verified separately.

## Target GitHub repository

- Owner: `yuvsta1`
- Repository: `quantstats-lab`
- Visibility: **public**
- Branch: `main`
- Licence: MIT (already present in the source)
- Suggested repository description:

  **Reproducible quant probability, simulations and risk analytics. Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.**

- Topics (suggested): `quantitative-finance`, `statistics`, `monte-carlo`, `python`, `streamlit`, `risk-management`, `open-source`

The full AI-assisted-development disclosure must remain visible in the README and release notes even if a platform truncates the short repository description.

## Publishing sequence

1. Create the empty public repository on GitHub, without automatically generating a README/LICENSE/gitignore (provided here).
2. Import **all source files**, including hidden `.github/` CI and issue templates. The directory structure must be preserved.
3. Set default branch to `main` and allow GitHub Actions workflows.
4. Confirm the workflows run and inspect the full job logs. Do **not** claim CI passed unless it did.
5. Perform the browser smoke checklist in `docs/QUALITY.md` on an installation with `[app]` extras.
6. After all quality gates pass, publish a GitHub `v0.1.0` release using `docs/RELEASE_NOTES.md` and preserve AI attribution.
7. Hosting, PyPI publication and obtaining early adopters are optional separate tasks; never claim they are complete until verified.

## CLI fallback (when a remote repository already exists)

```bash
git init -b main
git add .
git commit -m "Initial QuantStats Lab v0.1.0 candidate"
git remote add origin https://github.com/yuvsta1/quantstats-lab.git
git push -u origin main
```

These commands require your machine's Git credentials and are not executed by this source bundle.