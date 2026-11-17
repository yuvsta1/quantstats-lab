import numpy as np
import pytest

from quantstats_lab import bootstrap_returns, geometric_brownian_motion


def test_gbm_deterministic_zero_volatility():
    result = geometric_brownian_motion(100, 0.08, 0, steps=252, paths=12)
    assert result.paths.shape == (12, 253)
    assert result.paths[:, -1] == pytest.approx(np.full(12, 100 * np.exp(0.08)))
    assert np.all(result.paths[:, 0] == 100)


def test_gbm_expectation_analytical_benchmark():
    result = geometric_brownian_motion(100, 0.06, 0.2, steps=252, paths=8000, seed=7)
    expected = 100 * np.exp(0.06)
    assert abs(result.terminal_mean - expected) / expected < 0.018
    assert result.terminal_p05 < result.terminal_median < result.terminal_p95


def test_gbm_seed_and_independent_runs():
    args = dict(initial=100, annual_drift=0.03, annual_volatility=0.2, steps=10, paths=5)
    a = geometric_brownian_motion(**args, seed=4)
    b = geometric_brownian_motion(**args, seed=4)
    c = geometric_brownian_motion(**args, seed=5)
    assert np.array_equal(a.paths, b.paths)
    assert not np.array_equal(a.paths, c.paths)


def test_bootstrap_comes_only_from_observed_return_values():
    result = bootstrap_returns([-0.1, 0.0, 0.2], steps=20, paths=20, seed=10)
    realised = result.paths[:, 1:] / result.paths[:, :-1] - 1
    for value in realised.ravel():
        assert np.min(np.abs(np.array([-0.1, 0.0, 0.2]) - value)) < 1e-10
    assert result.paths.shape == (20, 21)


def test_bootstrap_single_total_loss_is_absorbing():
    res = bootstrap_returns([-1.0, 0.1], steps=10, paths=10, seed=1)
    assert np.all(np.diff(res.paths, axis=1)[res.paths[:, :-1] == 0] == 0)


@pytest.mark.parametrize(
    "changes",
    [
        {"initial": 0},
        {"annual_volatility": -1},
        {"paths": 0},
        {"steps": 0},
        {"paths": 20000, "steps": 1000},
        {"seed": -1},
        {"annual_drift": np.inf},
    ],
)
def test_gbm_invalid_inputs(changes):
    kwargs = dict(initial=100, annual_drift=0.03, annual_volatility=0.2, steps=5, paths=5)
    kwargs.update(changes)
    with pytest.raises(ValueError):
        geometric_brownian_motion(**kwargs)


def test_bootstrap_refuses_invalid_returns():
    with pytest.raises(ValueError):
        bootstrap_returns([0.1, -1.1])