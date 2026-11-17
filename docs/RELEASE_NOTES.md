# QuantStats Lab v0.2.2 — Keyboard input repair

Fixes a critical usability issue reported on the Mac application: numeric parameter boxes could appear uneditable and refused typed digits.

- Replace problematic custom Qt spin boxes with normal, keyboard-friendly numeric text editors.
- Enter decimals, negative numbers and whole-number parameters directly, by clicking and typing.
- Allow incomplete values while typing; when running an analysis, validate finite numbers and explain missing, nonnumeric or out-of-range values.
- Keep the uncluttered v0.2.1 appearance and light/dark theme, with explicit text-field contrast and focus styling.
- Add automated tests that **simulate actual keyboard typing** into displayed parameter fields in dark and light mode; include macOS, Windows and Linux build/startup tests.
- Preserve the existing scientific calculations, plotting, CSV import/export and model choices.

**Important:** Analysis outputs and summaries are deliberately read-only. Dropdowns select models; numeric parameter fields and data-entry fields are editable.

### Update
Download your operating system's v0.2.2 package from the GitHub Releases page and replace your existing app. Desktop distributions bundle Python, so no separate Python installation is needed.

**Security:** Windows builds are currently unsigned and macOS builds are unnotarised. Gatekeeper/SmartScreen may warn. Check source and checksums; avoid disabling system-wide security controls.

Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.
