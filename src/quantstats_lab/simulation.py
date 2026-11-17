"""Seeded geometric Brownian motion and IID historical bootstrap simulations."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .validation import finite_float, integer, seed_value, simple_returns


@dataclass(frozen=True)
class SimulationResult:
    paths: NDArray[np.float64]
    terminal_mean: float
    terminal_median: float
    terminal_p05: float
    terminal_p95: float


def _result(paths: NDArray[np.float64]) -> SimulationResult:
    terminal = paths[:, -1]
    if not np.all(np.isfinite(paths)):
        raise ValueError("simulation overflowed; use less extreme inputs")
    return SimulationResult(
        paths=paths,
        terminal_mean=float(np.mean(terminal)),
        terminal_median=float(np.median(terminal)),
        terminal_p05=float(np.quantile(terminal, 0.05)),
        terminal_p95=float(np.quantile(terminal, 0.95)),
    )


def _shape(steps: int, paths: int) -> tuple[int, int]:
    steps = integer(steps, "steps", minimum=1, maximum=2520)
    paths = integer(paths, "paths", minimum=1, maximum=20_000)
    if steps * paths > 3_000_000:
        raise ValueError("steps × paths must not exceed 3,000,000 (memory limit)")
    return steps, paths


def geometric_brownian_motion(
    initial: float,
    annual_drift: float,
    annual_volatility: float,
    *,
    steps: int = 252,
    paths: int = 1_000,
    periods_per_year: int = 252,
    seed: int | None = 42,
) -> SimulationResult:
    """Exact GBM discretisation: dS/S=mu dt+sigma dW; dt=1/periods_per_year."""
    initial = finite_float(initial, "initial")
    mu = finite_float(annual_drift, "annual_drift")
    sigma = finite_float(annual_volatility, "annual_volatility")
    if initial <= 0 or sigma < 0:
        raise ValueError("initial must be positive and annual_volatility nonnegative")
    steps, paths = _shape(steps, paths)
    periods_per_year = integer(periods_per_year, "periods_per_year", minimum=1)
    rng = np.random.default_rng(seed_value(seed))
    dt = 1.0 / periods_per_year
    increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * rng.standard_normal((paths, steps))
    log_paths = np.cumsum(increments, axis=1)
    values = np.concatenate([np.zeros((paths, 1)), log_paths], axis=1)
    with np.errstate(over="ignore", under="ignore"):
        result = initial * np.exp(values)
    return _result(result)


def bootstrap_returns(
    returns: NDArray[np.float64] | list[float],
    *,
    initial: float = 100.0,
    steps: int = 252,
    paths: int = 1_000,
    seed: int | None = 42,
) -> SimulationResult:
    """Draw empirical simple returns independently with replacement; ignores serial dependence."""
    values = simple_returns(returns)
    initial = finite_float(initial, "initial")
    if initial <= 0:
        raise ValueError("initial must be positive")
    steps, paths = _shape(steps, paths)
    rng = np.random.default_rng(seed_value(seed))
    sampled = rng.choice(values, size=(paths, steps), replace=True)
    wealth = np.cumprod(1.0 + sampled, axis=1)
    result = np.concatenate([np.ones((paths, 1)), wealth], axis=1) * initial
    return _result(result)