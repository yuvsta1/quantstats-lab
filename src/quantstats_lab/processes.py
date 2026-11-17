"""Self-contained stochastic-process simulators for research and education."""

import numpy as np
from numpy.typing import NDArray

from .simulation import _shape
from .validation import finite_float, seed_value


def ornstein_uhlenbeck(
    initial: float,
    long_run_mean: float,
    mean_reversion: float,
    volatility: float,
    *,
    steps: int = 252,
    paths: int = 100,
    dt: float = 1 / 252,
    seed: int | None = 42,
) -> NDArray[np.float64]:
    """Exact OU transitions: dX=theta*(mean-X)dt+sigma*dW."""
    initial = finite_float(initial, "initial")
    long_run_mean = finite_float(long_run_mean, "long_run_mean")
    theta = finite_float(mean_reversion, "mean_reversion")
    sigma = finite_float(volatility, "volatility")
    dt = finite_float(dt, "dt")
    if theta <= 0 or sigma < 0 or dt <= 0:
        raise ValueError("mean_reversion and dt must be positive; volatility must be nonnegative")
    steps, paths = _shape(steps, paths)
    factor = np.exp(-theta * dt)
    noise_std = sigma * np.sqrt(-np.expm1(-2 * theta * dt) / (2 * theta))
    rng = np.random.default_rng(seed_value(seed))
    noise = rng.standard_normal((paths, steps))
    output = np.empty((paths, steps + 1), dtype=np.float64)
    output[:, 0] = initial
    for t in range(steps):
        output[:, t + 1] = long_run_mean + factor * (output[:, t] - long_run_mean) + noise_std * noise[:, t]
    if not np.all(np.isfinite(output)):
        raise ValueError("simulation overflowed; choose less extreme parameters")
    return output


def autoregressive_one(
    initial: float,
    long_run_mean: float,
    phi: float,
    innovation_std: float,
    *,
    steps: int = 252,
    paths: int = 100,
    seed: int | None = 42,
) -> NDArray[np.float64]:
    """Stationary AR(1): X[t]=mean+phi*(X[t-1]-mean)+epsilon[t]."""
    initial = finite_float(initial, "initial")
    long_run_mean = finite_float(long_run_mean, "long_run_mean")
    phi = finite_float(phi, "phi")
    innovation_std = finite_float(innovation_std, "innovation_std")
    if abs(phi) >= 1 or innovation_std < 0:
        raise ValueError("abs(phi) must be below 1 and innovation_std nonnegative")
    steps, paths = _shape(steps, paths)
    rng = np.random.default_rng(seed_value(seed))
    noise = rng.normal(0, innovation_std, size=(paths, steps))
    output = np.empty((paths, steps + 1), dtype=np.float64)
    output[:, 0] = initial
    for t in range(steps):
        output[:, t + 1] = long_run_mean + phi * (output[:, t] - long_run_mean) + noise[:, t]
    if not np.all(np.isfinite(output)):
        raise ValueError("simulation overflowed; choose less extreme parameters")
    return output