import numpy as np
import pytest

from quantstats_lab import autoregressive_one, ornstein_uhlenbeck


def test_ou_deterministic_solution():
    result = ornstein_uhlenbeck(10, 2, 3, 0, steps=252, paths=5)
    expected = 2 + (10 - 2) * np.exp(-3)
    assert result[:, -1] == pytest.approx(np.full(5, expected))
    assert np.all(result[:, 0] == 10)


def test_ou_stationary_moments_rough_monte_carlo_check():
    result = ornstein_uhlenbeck(0, 0, 2, 0.5, steps=252, paths=4000, seed=44)
    assert abs(result[:, -1].mean()) < 0.04
    theoretical_var = 0.5**2 * (1 - np.exp(-4)) / 4
    assert np.var(result[:, -1]) == pytest.approx(theoretical_var, rel=0.09)


def test_ar1_deterministic_recursion():
    result = autoregressive_one(10, 2, 0.5, 0, steps=4, paths=2)
    assert result[0] == pytest.approx([10, 6, 4, 3, 2.5])


def test_ar1_seed_reproducible():
    a = autoregressive_one(0, 0, 0.6, 1, steps=10, paths=10, seed=99)
    b = autoregressive_one(0, 0, 0.6, 1, steps=10, paths=10, seed=99)
    assert np.array_equal(a, b)


@pytest.mark.parametrize("kwargs", [{"mean_reversion": 0}, {"volatility": -1}, {"dt": 0}, {"paths": 0}])
def test_ou_invalid(kwargs):
    inputs = dict(initial=1, long_run_mean=0, mean_reversion=1, volatility=1)
    inputs.update(kwargs)
    with pytest.raises(ValueError):
        ornstein_uhlenbeck(**inputs)


@pytest.mark.parametrize("phi", [-1, 1, 1.2, -2])
def test_ar1_rejects_nonstationary_coefficient(phi):
    with pytest.raises(ValueError):
        autoregressive_one(0, 0, phi, 1)