# macOS desktop release and verification

## Architecture

- `quantstats_lab.desktop`: a **native PySide6/Qt** application (no browser engine, Streamlit server, local port, or remote connection).
- `quantstats_lab.desktop_core`: independent strict text / CSV input and CSV export helpers.
- Existing distribution, inference, process, simulation and risk Python APIs remain the single source of numerical calculations.
- Embedded Matplotlib Qt canvas provides pan/zoom/save, line/bar/fan/drawdown charts.
- `assets/logo-original.png` preserves a cropped, resized and optimised raster derivative of the user-supplied navy/turquoise/white logo, including its transparent rounded background. `scripts/make_macos_icon.py` produces the retina icon sizes and macOS `.icns` for Dock and Finder. A design-reference vector is also available in `assets/logo.svg`.
- `src/quantstats_lab/app.py` (Streamlit) is retained as a separately installable legacy interface.

## Build a standalone macOS .app

Requires an **Apple Silicon Mac**, Python 3.13, and macOS `iconutil` (preinstalled with macOS).
Run from repository root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[desktop,dev]" "pyinstaller>=6.13,<7"
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_desktop_core.py tests/test_desktop_ui.py
python scripts/make_macos_icon.py
python -m PyInstaller --clean --noconfirm --onedir --windowed \
  --name "QuantStats Lab" \
  --icon "assets/logo.icns" \
  --add-data "assets/logo-original.png:assets" \
  --osx-bundle-identifier "io.github.yuvsta1.quantstatslab" \
  scripts/desktop_entry.py
```

The resulting file is `dist/QuantStats Lab.app`. Drag it to `/Applications`, then double-click it.
The app bundles the Python runtime, Qt, NumPy/SciPy and Matplotlib. Users do not need a separate Python installation.

## Download GitHub Actions builds

The `macOS Desktop App` workflow runs on an **Apple Silicon macOS 15** runner, tests desktop UI offscreen,
renders a retina iconset, generates a `.app` with PyInstaller, checks the bundle layout, starts and stops the packaged application in headless smoke-test mode, and uploads a ZIP artifact.

Artifacts are CI development builds, **not** officially released or notarised distributions. Downloading from an
untrusted branch or pull request may be unsafe. The artifact expires according to GitHub retention settings.

## Apple distribution and Gatekeeper

- For sharing beyond local testing, obtain an **Apple Developer Program** membership and **Developer ID Application** certificate.
- Sign **all nested binaries and frameworks**, enable hardened runtime where necessary, then sign the final app bundle.
- Notarise the ZIP/DMG with Apple's `notarytool`; staple the ticket to the app or disk image and verify with `spctl`.
- Use a build with a trusted certificate and reproducible source review. GitHub CI currently does **not** sign or notarise.
- For your own Mac, a blocked, unnotarised app can generally be opened through Finder's Open action or
  System Settings → Privacy & Security → Open Anyway after confirming you trust the source. Do not turn off Gatekeeper globally.

## Manual smoke test (required before calling a release complete)

1. Double-click the packaged app from `/Applications` **with Terminal closed**. Confirm there is no browser page.
2. Confirm the navy/turquoise application icon appears in Finder, Dock, and window title.
3. Toggle light/dark mode and resize the desktop window; the chart should remain visible.
4. On Distributions, calculate **each of the six families** and use chart toolbar pan/zoom/save.
5. On Monte Carlo, run GBM and bootstrap, verify same seed yields same outcomes, export CSV.
6. On Inference, check Student-t, IID bootstrap, one-sample test, optional Welch, optional BH.
7. On Processes, run OU and AR(1), check exported terminal states.
8. On Risk, explicitly note synthetic sample mode; import a CSV with decimal simple returns,
   choose a numeric column, inspect VaR/ES/drawdown, export results.
9. Try invalid numeric input, malformed/missing CSV, negative returns less than -100%, and huge files.
   The app must show a recoverable validation error rather than crash.
10. Disconnect internet and re-run ordinary calculations. No online services should be required.
11. Check macOS Activity Monitor for the native Qt process and quit/relaunch from Applications.

## Notes and limitations

- CI tests do not replace the above on-device macOS verification. macOS Gatekeeper behaviour and rendering vary.
- Computational work currently runs on the GUI event loop; very large simulations can temporarily freeze the interface.
- IID bootstrap ignores serial dependence. GBM is model-based and not a price forecast. Historical VaR/ES does not
  guarantee forward tail coverage. Consult `docs/MATH.md` for assumptions.
- Security/privacy: no telemetry or network calls are made by the desktop app. Imported CSV data stay in memory
  until closing the app; exporting is an explicit user action.
- All 99 original tests remain part of the regular CI suite; the desktop adds separate GUI and import tests.

**Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.**
