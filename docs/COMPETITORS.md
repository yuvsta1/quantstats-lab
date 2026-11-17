# Comparable tools and intended differentiation

Market check performed 17 November 2026. These are public references, **not** evidence that QuantStats Lab has users or market demand.

> Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

| Existing project | Known strength | How QuantStats Lab differs |
| --- | --- | --- |
| [QuantStats](https://github.com/ranaroussi/quantstats) | Mature portfolio tearsheets, analytics and return-based reporting | Model and probability experimentation rather than broad historical portfolio reporting |
| [ProbViz](https://sanskarpan.github.io/probviz/) | Broad probability visualisation, distribution families, copulas and statistical tests | Deliberately smaller API with quant-specific GBM, AR(1)/OU, seeded return resampling and historical risk analysis in one app |
| [Statistics Playground](https://statisticsplayground.com/) | No-install browser-first general statistics learning | Domain-specific finance scenarios, risk analytics, CSV import and reusable Python functions |
| [SciPy stats](https://docs.scipy.org/doc/scipy/reference/stats.html) | Industry-standard distributions, inference and numerical algorithms | Discoverable finance-oriented workflows and chart interface *built on* SciPy, not a replacement for it |

## What we cannot honestly claim

- No independent users, stars, downloads or contributions have been measured for this release candidate.
- This project is not more accurate than SciPy; it directly depends on SciPy for distributions and t-tests.
- A broad feature list is not a product-market fit study. Adoption requires user interviews, outreach, issue responsiveness and sustained maintenance.

## Initial external feedback questions

1. Are you working with return data, probability problems or simulated stochastic processes? Which task recurs weekly?
2. Which assumptions in existing tools are difficult to inspect or reproduce?
3. Does the CSV importer accept your real-world non-confidential dataset format?
4. Would you incorporate the Python functions into an existing notebook or pipeline? Why or why not?
5. Which numerical or UI behaviour would make you trust or distrust the output?

A first real-user milestone is **ten independent users providing actionable feedback**, not a guaranteed target or an assertion of existing adoption.