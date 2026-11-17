"""QuantStats Lab: statistical tools with explicit assumptions and reproducible simulations."""

from .distributions import DistributionResult, evaluate_distribution, make_distribution
from .inference import (
    ConfidenceInterval,
    TestResult,
    benjamini_hochberg,
    bootstrap_mean_interval,
    one_sample_ttest,
    t_mean_interval,
    welch_ttest,
)
from .processes import autoregressive_one, ornstein_uhlenbeck
from .risk import PerformanceMetrics, TailRisk, drawdown_series, historical_var_es, performance_metrics
from .simulation import SimulationResult, bootstrap_returns, geometric_brownian_motion

__version__ = "0.2.1"
__all__ = [
    "ConfidenceInterval",
    "DistributionResult",
    "PerformanceMetrics",
    "SimulationResult",
    "TailRisk",
    "TestResult",
    "autoregressive_one",
    "benjamini_hochberg",
    "bootstrap_mean_interval",
    "bootstrap_returns",
    "drawdown_series",
    "evaluate_distribution",
    "geometric_brownian_motion",
    "historical_var_es",
    "make_distribution",
    "one_sample_ttest",
    "ornstein_uhlenbeck",
    "performance_metrics",
    "t_mean_interval",
    "welch_ttest",
]