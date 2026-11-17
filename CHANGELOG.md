## [0.2.2] - 2026-11-18

### Fixed
- Restored reliable keyboard entry for all numeric input fields using native text editors instead of restricted spin controls.
- Validate numerical values on calculation with clear error messages, supporting intermediate edits.
- Added GUI tests that send real keyboard events to displayed numeric fields in both themes and validate inputs.

## [0.2.1] - 2026-11-17

### Changed
- Refined the desktop UI to a compact, minimalist quantitative workstation based on user screen-recording feedback.
- Removed spinner dots and excess decimal zeros; improved dropdown menus, plotting controls, readable dark/light themes, and form layout.
- Automatically display a chart on first entry and hide parameters unused by the selected statistical model.

### Tests
- Added GUI regression tests for theme contrast, numerical formatting, navigation, and conditional inputs.

# Changelog

## [0.1.0] - 2026-11-17

Initial release candidate:

- Python numerical API for six probability distributions, statistical inference, seeded GBM and empirical bootstrap simulation, OU and AR(1) processes, and historical risk analytics.
- Optional Streamlit app with charting, CSV input, export and explicit modelling caveats.
- Unit/integration tests, reproducible example, mathematical notes, CI and contribution guidance.

**Disclosure:** Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.