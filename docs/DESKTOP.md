# Desktop Releases — Windows, macOS and Linux

## Official downloads

**Latest stable release:** https://github.com/yuvsta1/quantstats-lab/releases/latest

**All versions:** https://github.com/yuvsta1/quantstats-lab/releases

Versioned assets are attached directly to GitHub Releases and remain available independently of short-lived CI artifacts.

| Platform | Supported target | File | Install |
| --- | --- | --- | --- |
| Windows | Windows 10/11 x64 | `QuantStats-Lab-vX.Y.Z-Windows-x64.exe` | Download and double-click |
| Mac | macOS 15+ Apple Silicon | `QuantStats-Lab-vX.Y.Z-macOS-Apple-Silicon.zip` | Unzip, drag `QuantStats Lab.app` to Applications |
| Mac | macOS 15+ Intel | `QuantStats-Lab-vX.Y.Z-macOS-Intel.zip` | Unzip, drag `QuantStats Lab.app` to Applications |
| Linux | Ubuntu 22.04+/Debian-compatible x64 | `QuantStats-Lab-vX.Y.Z-Linux-x64.deb` | Open with Debian software installer |
| Linux | Linux x64 with compatible shared libraries | `QuantStats-Lab-vX.Y.Z-Linux-x64.tar.gz` | Extract, launch `QuantStatsLab/QuantStatsLab` |

Linux portable bundles are not guaranteed to run on every distribution; Debian/Ubuntu .deb is the preferred path where supported. This release does not build ARM64 Windows/Linux packages. Mac ARM64 and Intel packages are separate native builds.

**Standalone:** these apps bundle their own Python interpreter and native Qt libraries. Users do not have to install Python or open Terminal. The GUI does not use a web server or require network access for ordinary calculations. Clicking the optional "latest version" button explicitly opens GitHub in a browser.

## Automatic versioned GitHub Releases

The workflow `.github/workflows/desktop-releases.yml`:

1. Runs on pull requests and on `main` pushes.
2. Installs Python **3.15** and desktop build dependencies on all four GitHub-hosted runner targets (macOS arm64, macOS Intel, Windows x64 and Ubuntu Linux x64).
3. Executes numerical and native offscreen UI regression tests on each OS.
4. Builds the real app using PyInstaller and **runs the frozen executable with `--smoke-test`** on each OS.
5. Produces a signed? **No — unsigned** file set: Windows one-file EXE, two zipped Mac app bundles, Linux .deb and portable tarball.
6. On `main` only, **after all four builds pass**, gathers all five files, generates `SHA256SUMS.txt`, and publishes a GitHub Release at tag `vX.Y.Z` matching `pyproject.toml`.
7. If a matching release already exists, does not overwrite it. To publish the next version, increment `pyproject.toml`, `src/quantstats_lab/__init__.py`, and the release notes; merge the changes into `main` only after passing CI.

A source-code push to `main` does not generate a duplicate release when the version remains unchanged. The standard `CI` workflow additionally tests the Python 3.11–3.15 numerical library and 3.13–3.15 native Qt interface.

## Developer build

From the repository root, with Python 3.15 for your own platform:

```bash
python -m pip install -e ".[desktop,dev]" "pyinstaller>=6.21,<7" "pillow>=11,<14"
python -m pytest tests/test_desktop_core.py tests/test_desktop_ui.py -q
python scripts/build_desktop_release.py
```

The script produces the platform's versioned files inside `release-assets/`. On Linux, `dpkg-deb` is required for .deb creation; on macOS, Apple's built-in `iconutil`, `plutil` and `ditto` are used. The Windows icon comes from your navy/turquoise logo; both Mac bundles use the same supplied logo.

## Security and distribution

**These builds are currently unsigned and Apple-unnotarised.** On macOS, Gatekeeper may block a downloaded app. On Windows, SmartScreen can warn about an unsigned executable. Do not disable security protections globally; verify the GitHub source, version and SHA256 checksum before considering a security exception.

For broad public distribution, configure Apple Developer ID signing and notarisation, and Windows code signing. Publishing binaries as GitHub Release assets does **not** mean Apple or Microsoft has verified them.

PySide6 Qt libraries have their own licensing and notices; check LGPL obligations before commercial redistribution.

## Manual smoke tests (real hardware)

Automated CI cannot replace manual testing on actual hardware. Before treating any release as fully proven, test download, extraction, startup, icons and interaction on Windows x64, both Mac architectures and a supported Linux GUI.

Check the five research modules, reproducibility with a seed, local CSV validation, exports, chart pan/zoom/save, dark/light mode and app exit/relaunch. Verify that internet disconnection does not stop normal calculations.

**Known limits:** Large simulations can block the GUI event loop temporarily. GBM and IID-bootstrap assumptions remain model-based; risk metrics are descriptive, not market forecasts. See `docs/MATH.md`.

Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.
