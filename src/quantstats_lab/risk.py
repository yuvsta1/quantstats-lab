"""Transparent descriptive risk metrics for simple-period returns, not forecasts."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .validation import finite_float, integer, probability, simple_returns


@dataclass(frozen=True)
class TailRisk:
    confidence: float
    value_at_risk: float
    expected_shortfall: float
    observations: int


@dataclass(frozen=True)
class PerformanceMetrics:
    total_return: float
    annualised_return: float
    annualised_volatility: float
    annualised_sharpe: float | None
    maximum_drawdown: float
    observations: int


def historical_var_es(returns: list[float] | NDArray[np.float64], confidence: float = 0.95) -> TailRisk:
    """Empirical loss VaR (linear quantile) and fractional-tail expected shortfall.

    Values are nonnegative loss fractions, floored at zero. The expected shortfall
    uses the worst (1-confidence) fraction of observed losses, including partial
    weight on the boundary observation when the tail size is fractional.
    """
    r = simple_returns(returns)
    conf = probability(confidence, "confidence", open_interval=True)
    loss = np.sort(-r)
    count = len(loss)
    tail_n = (1 - conf) * count
    whole = int(np.floor(tail_n))
    fraction = tail_n - whole
    tail_sum = float(np.sum(loss[-whole:])) if whole else 0.0
    if fraction > 0:
        tail_sum += fraction * float(loss[-whole - 1])
    es = tail_sum / tail_n
    var = float(np.quantile(loss, conf, method="linear"))
    return TailRisk(conf, max(0.0, var), max(0.0, es), count)


def drawdown_series(returns: list[float] | NDArray[np.float64]) -> NDArray[np.float64]:
    """Drawdown at every point including the initial wealth of 1.0."""
    r = simple_returns(returns)
    wealth = np.r_[1.0, np.cumprod(1.0 + r)]
    peak = np.maximum.accumulate(wealth)
    return wealth / peak - 1.0


def performance_metrics(
    returns: list[float] | NDArray[np.float64],
    *,
    periods_per_year: int = 252,
    annual_risk_free_rate: float = 0.0,
) -> PerformanceMetrics:
    """Annualisation assumes equally spaced periods; Sharpe uses sample std (ddof=1)."""
    r = simple_returns(returns)
    freq = integer(periods_per_year, "periods_per_year", minimum=1)
    annual_rf = finite_float(annual_risk_free_rate, "annual_risk_free_rate")
    if annual_rf <= -1:
        raise ValueError("annual_risk_free_rate must be greater than -100%")
    excess = r - ((1.0 + annual_rf) ** (1.0 / freq) - 1.0)
    sd = float(np.std(excess, ddof=1))
    sharpe = float(np.mean(excess) / sd * np.sqrt(freq)) if sd > 0 else None
    # Log-compounding is more numerically stable than multiplying many
    # gross returns. A -100% observation makes terminal wealth zero.
    if np.any(r == -1):
        total, annualised = -1.0, -1.0
    else:
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            log_growth = float(np.sum(np.log1p(r)))
            total = float(np.expm1(log_growth))
            annualised = float(np.expm1(log_growth * freq / len(r)))
        if not np.isfinite(total) or not np.isfinite(annualised):
            raise ValueError("return compounding overflowed; choose a numerically reasonable scale")
    drawdowns = drawdown_series(r)
    return PerformanceMetrics(
        total_return=total,
        annualised_return=annualised,
        annualised_volatility=float(np.std(r, ddof=1) * np.sqrt(freq)),
        annualised_sharpe=sharpe,
        maximum_drawdown=float(-np.min(drawdowns)),
        observations=len(r),
    )