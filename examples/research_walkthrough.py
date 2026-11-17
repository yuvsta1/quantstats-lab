"""Run with: python examples/research_walkthrough.py"""

import numpy as np

from quantstats_lab import (
    benjamini_hochberg,
    bootstrap_mean_interval,
    geometric_brownian_motion,
    historical_var_es,
    performance_metrics,
)

rng = np.random.default_rng(2026)
returns = rng.normal(0.0002, 0.01, size=504)  # synthetic, not historical

print("Synthetic sample return mean confidence interval:")
print(bootstrap_mean_interval(returns, seed=2026))
print("Historical descriptive tail risk on synthetic returns:")
print(historical_var_es(returns, confidence=0.95))
print("Synthetic risk statistics:")
print(performance_metrics(returns))
print("Benjamini–Hochberg adjusted p-values:")
print(benjamini_hochberg([0.001, 0.02, 0.08, 0.3]))

sim = geometric_brownian_motion(100, 0.06, 0.2, steps=252, paths=2000, seed=2026)
print(f"GBM terminal mean: {sim.terminal_mean:.4f}; median: {sim.terminal_median:.4f}")