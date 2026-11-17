"""An explicit, small catalogue of SciPy distributions and summary statistics."""

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import stats

from .validation import finite_float, integer, probability

SUPPORTED = ("normal", "student_t", "binomial", "poisson", "exponential", "lognormal")


@dataclass(frozen=True)
class DistributionResult:
    name: str
    x: float
    mass_or_density: float
    cdf: float
    survival: float
    mean: float
    standard_deviation: float
    q05: float
    median: float
    q95: float
    discrete: bool


def make_distribution(name: str, **parameters: Any) -> tuple[Any, bool]:
    """Return a frozen SciPy distribution, rejecting unknown parameter combinations."""
    schemas = {
        "normal": {"mean", "std"},
        "student_t": {"df", "loc", "scale"},
        "binomial": {"n", "p"},
        "poisson": {"rate"},
        "exponential": {"scale"},
        "lognormal": {"shape", "scale"},
    }
    if name not in schemas:
        raise ValueError(f"Unknown distribution {name!r}; choose from {', '.join(SUPPORTED)}")
    if set(parameters) != schemas[name]:
        raise ValueError(f"{name} expects exactly {', '.join(sorted(schemas[name]))}")
    if name == "normal":
        mean = finite_float(parameters["mean"], "mean")
        std = finite_float(parameters["std"], "std")
        if std <= 0:
            raise ValueError("std must be positive")
        return stats.norm(loc=mean, scale=std), False
    if name == "student_t":
        df = finite_float(parameters["df"], "df")
        loc = finite_float(parameters["loc"], "loc")
        scale = finite_float(parameters["scale"], "scale")
        if df <= 0 or scale <= 0:
            raise ValueError("df and scale must be positive")
        return stats.t(df=df, loc=loc, scale=scale), False
    if name == "binomial":
        n = integer(parameters["n"], "n", maximum=100_000)
        p = probability(parameters["p"], "p")
        return stats.binom(n=n, p=p), True
    if name == "poisson":
        rate = finite_float(parameters["rate"], "rate")
        if rate <= 0:
            raise ValueError("rate must be positive")
        return stats.poisson(mu=rate), True
    if name == "exponential":
        scale = finite_float(parameters["scale"], "scale")
        if scale <= 0:
            raise ValueError("scale must be positive")
        return stats.expon(scale=scale), False
    shape = finite_float(parameters["shape"], "shape")
    scale = finite_float(parameters["scale"], "scale")
    if shape <= 0 or scale <= 0:
        raise ValueError("shape and scale must be positive")
    return stats.lognorm(s=shape, scale=scale), False


def evaluate_distribution(name: str, x: float, **parameters: Any) -> DistributionResult:
    """Evaluate the PMF/PDF, CDF, survival and quantiles at x."""
    frozen, discrete = make_distribution(name, **parameters)
    value = finite_float(x, "x")
    mean, variance = frozen.stats(moments="mv")
    # The Student-t mean does not exist for degrees of freedom <= 1.
    if name == "student_t" and parameters["df"] <= 1:
        mean = float("nan")
    return DistributionResult(
        name=name,
        x=value,
        mass_or_density=float(frozen.pmf(value) if discrete else frozen.pdf(value)),
        cdf=float(frozen.cdf(value)),
        survival=float(frozen.sf(value)),
        mean=float(mean),
        standard_deviation=float(np.sqrt(variance)),
        q05=float(frozen.ppf(0.05)),
        median=float(frozen.ppf(0.5)),
        q95=float(frozen.ppf(0.95)),
        discrete=discrete,
    )