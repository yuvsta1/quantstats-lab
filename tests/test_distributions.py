import numpy as np
import pytest
from scipy import stats

from quantstats_lab import evaluate_distribution, make_distribution


@pytest.mark.parametrize(
    ("kind", "params", "x", "reference"),
    [
        ("normal", {"mean": 1.2, "std": 2.5}, 0.4, stats.norm(1.2, 2.5)),
        ("student_t", {"df": 5, "loc": 0.2, "scale": 1.4}, 0.7, stats.t(5, 0.2, 1.4)),
        ("binomial", {"n": 20, "p": 0.3}, 5, stats.binom(20, 0.3)),
        ("poisson", {"rate": 3.5}, 4, stats.poisson(3.5)),
        ("exponential", {"scale": 2}, 1.5, stats.expon(scale=2)),
        ("lognormal", {"shape": 0.7, "scale": 2}, 1.5, stats.lognorm(s=0.7, scale=2)),
    ],
)
def test_reference_distributions(kind, params, x, reference):
    actual = evaluate_distribution(kind, x, **params)
    expected_pdf = reference.pmf(x) if actual.discrete else reference.pdf(x)
    assert actual.mass_or_density == pytest.approx(expected_pdf, rel=1e-12)
    assert actual.cdf == pytest.approx(reference.cdf(x), rel=1e-12)
    assert actual.survival == pytest.approx(reference.sf(x), rel=1e-12)
    assert actual.q05 == pytest.approx(reference.ppf(0.05))
    assert actual.median == pytest.approx(reference.ppf(0.5))
    assert actual.q95 == pytest.approx(reference.ppf(0.95))
    assert actual.cdf + actual.survival == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("kind", "params"),
    [
        ("normal", {"mean": 0, "std": 0}),
        ("normal", {"mean": np.nan, "std": 1}),
        ("normal", {"mean": 0, "std": np.inf}),
        ("student_t", {"df": 0, "loc": 0, "scale": 1}),
        ("binomial", {"n": -1, "p": 0.5}),
        ("binomial", {"n": 2.5, "p": 0.5}),
        ("binomial", {"n": 2, "p": 1.1}),
        ("poisson", {"rate": 0}),
        ("exponential", {"scale": -1}),
        ("lognormal", {"shape": 0, "scale": 1}),
    ],
)
def test_invalid_distribution_parameters(kind, params):
    with pytest.raises(ValueError):
        make_distribution(kind, **params)


def test_rejects_unknown_parameter_names():
    with pytest.raises(ValueError):
        make_distribution("normal", mean=0, std=1, typo=2)
    with pytest.raises(ValueError):
        make_distribution("unknown", scale=1)


def test_discrete_off_support():
    result = evaluate_distribution("binomial", 3.5, n=5, p=0.5)
    assert result.mass_or_density == 0


def test_t_distribution_undefined_moments():
    actual = evaluate_distribution("student_t", 1, df=0.5, loc=0, scale=1)
    assert np.isnan(actual.mean)