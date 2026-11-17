"""Shared input validators: never silently discard bad observations."""

from collections.abc import Iterable
from numbers import Integral, Real

import numpy as np
from numpy.typing import NDArray


def finite_float(value: Real, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{name} must be a finite real number")
    return number


def integer(value: Integral, name: str, *, minimum: int = 0, maximum: int = 1_000_000) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name} must be an integer")
    number = int(value)
    if not minimum <= number <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return number


def probability(value: Real, name: str = "probability", *, open_interval: bool = False) -> float:
    number = finite_float(value, name)
    if (not 0 < number < 1) if open_interval else (not 0 <= number <= 1):
        raise ValueError(f"{name} must be {'strictly between' if open_interval else 'between'} 0 and 1")
    return number


def observations(data: Iterable[Real], *, minimum: int = 2) -> NDArray[np.float64]:
    try:
        array = np.asarray(data, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("observations must contain numeric values") from exc
    if array.ndim != 1 or array.size < minimum:
        raise ValueError(f"observations must be one-dimensional with at least {minimum} values")
    if not np.all(np.isfinite(array)):
        raise ValueError("observations contain NaN or infinity; clean the source data first")
    return array


def simple_returns(data: Iterable[Real], *, minimum: int = 2) -> NDArray[np.float64]:
    values = observations(data, minimum=minimum)
    if np.any(values < -1):
        raise ValueError("simple returns cannot be below -100%; use a valid return series")
    return values


def seed_value(seed: int | None) -> int | None:
    if seed is None:
        return None
    return integer(seed, "seed", maximum=2**32 - 1)