"""Classical and resampling inference with documented assumptions."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import stats

from .validation import finite_float, integer, observations, probability, seed_value


@dataclass(frozen=True)
class ConfidenceInterval:
    estimate: float
    lower: float
    upper: float
    confidence: float
    method: str


@dataclass(frozen=True)
class TestResult:
    statistic: float
    p_value: float
    degrees_of_freedom: float
    method: str


def t_mean_interval(data: list[float] | NDArray[np.float64], confidence: float = 0.95) -> ConfidenceInterval:
    """Student-t interval assumes IID observations with approximately normal sample mean."""
    x = observations(data)
    conf = probability(confidence, "confidence", open_interval=True)
    mean = float(np.mean(x))
    sem = float(stats.sem(x))
    if sem == 0:
        return ConfidenceInterval(mean, mean, mean, conf, "student-t (zero sample variance)")
    lower, upper = stats.t.interval(conf, df=len(x) - 1, loc=mean, scale=sem)
    return ConfidenceInterval(mean, float(lower), float(upper), conf, "student-t")


def bootstrap_mean_interval(
    data: list[float] | NDArray[np.float64],
    *,
    confidence: float = 0.95,
    resamples: int = 5000,
    seed: int | None = 42,
) -> ConfidenceInterval:
    """IID percentile bootstrap, computed in batches to bound temporary memory."""
    x = observations(data)
    conf = probability(confidence, "confidence", open_interval=True)
    resamples = integer(resamples, "resamples", minimum=100, maximum=100_000)
    rng = np.random.default_rng(seed_value(seed))
    means = np.empty(resamples, dtype=np.float64)
    batch_size = max(1, min(2048, 2_000_000 // len(x)))
    for start in range(0, resamples, batch_size):
        end = min(start + batch_size, resamples)
        draws = rng.choice(x, size=(end - start, len(x)), replace=True)
        means[start:end] = draws.mean(axis=1)
    alpha = (1.0 - conf) / 2.0
    lower, upper = np.quantile(means, [alpha, 1.0 - alpha])
    return ConfidenceInterval(float(np.mean(x)), float(lower), float(upper), conf, "IID percentile bootstrap")


def one_sample_ttest(data: list[float] | NDArray[np.float64], null_mean: float = 0.0) -> TestResult:
    x = observations(data)
    null = finite_float(null_mean, "null_mean")
    if np.ptp(x) == 0:
        return TestResult(
            0.0 if x[0] == null else float("inf"),
            1.0 if x[0] == null else 0.0,
            float(len(x) - 1),
            "two-sided one-sample t (zero sample variance)",
        )
    result = stats.ttest_1samp(x, null, alternative="two-sided")
    return TestResult(float(result.statistic), float(result.pvalue), float(len(x) - 1), "two-sided one-sample t")


def welch_ttest(first: list[float], second: list[float]) -> TestResult:
    a, b = observations(first), observations(second)
    var_a, var_b = float(np.var(a, ddof=1)), float(np.var(b, ddof=1))
    if var_a == 0 and var_b == 0:
        equal = float(np.mean(a)) == float(np.mean(b))
        return TestResult(0.0 if equal else float("inf"), 1.0 if equal else 0.0, float("inf"), "two-sided Welch t (zero variances)")
    result = stats.ttest_ind(a, b, equal_var=False, alternative="two-sided")
    return TestResult(float(result.statistic), float(result.pvalue), float(result.df), "two-sided Welch t")


def benjamini_hochberg(p_values: list[float] | NDArray[np.float64]) -> NDArray[np.float64]:
    """BH-adjusted p-values controlling false discovery rate under applicable dependence conditions."""
    values = observations(p_values, minimum=1)
    if np.any((values < 0) | (values > 1)):
        raise ValueError("p-values must lie in [0, 1]")
    order = np.argsort(values, kind="stable")
    sorted_p = values[order]
    count = len(values)
    adjusted = sorted_p * count / np.arange(1, count + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    out = np.empty_like(values)
    out[order] = np.clip(adjusted, 0, 1)
    return out