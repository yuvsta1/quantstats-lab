# QuantStats Lab v0.2.1 — Compact workstation interface

This update improves usability on Windows, macOS and Linux using the user's screen recording as a real-world design reference.

- Cleaner, narrower left navigation and less wasted space throughout the research workstation
- Numeric inputs show meaningful digits instead of trailing zeroes; tiny spinner arrows/dots are hidden
- Reworked dropdowns with readable native popup palettes in both light and dark modes
- Simplified charts: compact text controls for Reset, Pan, Zoom and Save PNG replace oversized toolbar icons
- Consistent muted labels, borders and accessible contrast across the UI and plots
- Context-sensitive Monte Carlo and stochastic-process inputs; irrelevant parameters no longer clutter the panel
- Initial research chart renders when navigating to a tool
- Scrollable parameter sections for smaller screens while exports and result summaries remain visible
- New headless Qt tests for input formatting, theme contrast, toolbar behaviour and conditional inputs
- All quantitative calculation APIs and reproducibility logic preserved

Cross-platform standalone application downloads contain their own Python runtime. No manual Python installation is necessary.

**Distribution limitations:** macOS builds are not Apple-notarised; Windows builds are unsigned. Your operating system might prompt you to confirm the publisher. Review the project source and checksums. Automated smoke tests do not replace manual testing on real hardware.

**Quantitative limitation:** the tools are educational/research calculations, not investment advice or market forecasts.

Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.
