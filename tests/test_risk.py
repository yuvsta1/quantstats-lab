import numpy as np
import pytest

from quantstats_lab import drawdown_series, historical_var_es, performance_metrics


def test_var_es_known_losses_with_fractional_tail():
    returns = [-0.4, -0.2, -0.1, 0.0, 0.1]
    output = historical_var_es(returns, confidence=0.7)
    assert output.value_at_risk == pytest.approx(0.18)
    # 1.5 worst losses: (0.4 + 0.5*0.2) / 1.5
    assert output.expected_shortfall == pytest.approx(1 / 3)
    assert output.expected_shortfall >= output.value_at_risk


def test_losses_positive_or_zero():
    risk = historical_var_es([0.1, 0.2, 0.05])
    assert risk.value_at_risk == 0
    assert risk.expected_shortfall == 0


def test_drawdown_includes_initial_peak():
    output = drawdown_series([-0.1, 0.2, -0.5, 0.1])
    expected_wealth = np.array([1, 0.9, 1.08, 0.54, 0.594])
    expected_peak = np.maximum.accumulate(expected_wealth)
    assert output == pytest.approx(expected_wealth / expected_peak - 1)


def test_drawdown_total_loss():
    assert drawdown_series([0.1, -1.0, 0.1])[-1] == -1


def test_performance_returns_volatility_sharpe_reference():
    r = np.array([0.01, -0.02, 0.03, 0.02, -0.01])
    output = performance_metrics(r, periods_per_year=12, annual_risk_free_rate=0.03)
    excess = r - ((1.03) ** (1 / 12) - 1)
    assert output.total_return == pytest.approx(np.prod(1 + r) - 1)
    assert output.annualised_return == pytest.approx(np.prod(1 + r) ** (12 / len(r)) - 1)
    assert output.annualised_volatility == pytest.approx(np.std(r, ddof=1) * np.sqrt(12))
    assert output.annualised_sharpe == pytest.approx(np.mean(excess) / np.std(excess, ddof=1) * np.sqrt(12))


def test_zero_volatility_sharpe_undefined():
    output = performance_metrics([0.01, 0.01, 0.01])
    assert output.annualised_sharpe is None
    assert output.maximum_drawdown == 0


@pytest.mark.parametrize("invalid", [[0.1], [0.1, np.nan], [0.1, -1.1], [[0.1, 0.1]], []])
def test_invalid_simple_returns(invalid):
    with pytest.raises(ValueError):
        historical_var_es(invalid)


def test_invalid_frequency():
    with pytest.raises(ValueError):
        performance_metrics([0.1, -0.2], periods_per_year=0)


def test_invalid_risk_free_rate():
    with pytest.raises(ValueError):
        performance_metrics([0.1, -0.2], annual_risk_free_rate=-1)


def test_invariance_of_risk_to_order_except_drawdown():
    a = [0.03, -0.06, 0.02, 0.01]
    b = list(reversed(a))
    assert historical_var_es(a) == historical_var_es(b)


def test_small_compounded_returns_keep_precision():
    r = np.array([1e-13, 2e-13, -1e-13, 3e-13])
    output = performance_metrics(r, periods_per_year=12)
    assert output.total_return == pytest.approx(float(np.expm1(np.log1p(r).sum())), rel=1e-12)


def test_total_loss_returns_minus_one_after_compounding():
    metrics = performance_metrics([0.1, -1.0, 0.2])
    assert metrics.total_return == -1.0
    assert metrics.annualised_return == -1.0
    assert metrics.maximum_drawdown == 1.0


def test_compound_overflow_rejected_instead_of_reporting_infinite_return():
    with pytest.raises(ValueError, match="overflowed"):
        performance_metrics([1e200, 1e200], periods_per_year=252)