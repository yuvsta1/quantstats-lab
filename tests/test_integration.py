"""Public-API end-to-end integration and regression coverage."""

import numpy as np
import pytest

import quantstats_lab as lab


def test_documented_usage_pipeline_and_determinism():
    rng = np.random.default_rng(2026)
    synthetic = rng.normal(0.0002, 0.01, 504)
    ci = lab.bootstrap_mean_interval(synthetic, seed=2026)
    risk = lab.historical_var_es(synthetic)
    metrics = lab.performance_metrics(synthetic)
    results = lab.geometric_brownian_motion(100, 0.06, 0.2, paths=100, steps=252, seed=2026)
    assert ci.lower <= ci.estimate <= ci.upper
    assert risk.expected_shortfall >= risk.value_at_risk
    assert metrics.maximum_drawdown >= 0
    assert results.paths.shape == (100, 253)
    assert np.array_equal(
        results.paths,
        lab.geometric_brownian_motion(100, 0.06, 0.2, paths=100, steps=252, seed=2026).paths,
    )


def test_public_api_exported():
    for symbol in lab.__all__:
        assert getattr(lab, symbol) is not None


def test_seed_and_input_validation():
    with pytest.raises(ValueError):
        lab.bootstrap_mean_interval([0.1, 0.2], seed=True)
    with pytest.raises(ValueError):
        lab.evaluate_distribution("normal", float("nan"), mean=0, std=1)