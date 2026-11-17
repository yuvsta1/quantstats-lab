import numpy as np
import pytest
from scipy import stats

from quantstats_lab import (
    benjamini_hochberg,
    bootstrap_mean_interval,
    one_sample_ttest,
    t_mean_interval,
    welch_ttest,
)


def test_student_interval_matches_scipy_independently():
    data = np.array([-1.0, 2.2, 3.0, 4.8, 0.3, -0.2])
    result = t_mean_interval(data, 0.95)
    reference = stats.t.interval(0.95, len(data) - 1, loc=data.mean(), scale=stats.sem(data))
    assert [result.lower, result.upper] == pytest.approx(reference, abs=1e-13)
    assert result.estimate == pytest.approx(data.mean())


def test_bootstrap_seed_reproducibility_and_interval_contains_mean_for_constant():
    data = [2.0, 2.0, 2.0, 2.0]
    first = bootstrap_mean_interval(data, resamples=1000, seed=22)
    second = bootstrap_mean_interval(data, resamples=1000, seed=22)
    assert first == second
    assert first.lower == first.upper == first.estimate == 2


def test_bootstrap_matches_naive_reference_with_single_batch():
    data = np.array([0.0, 1.0, 2.0, 10.0])
    rng = np.random.default_rng(101)
    means = rng.choice(data, size=(1000, 4), replace=True).mean(axis=1)
    result = bootstrap_mean_interval(data, resamples=1000, seed=101)
    assert [result.lower, result.upper] == pytest.approx(np.quantile(means, [0.025, 0.975]))


def test_bootstrap_batch_reproducibility():
    data = np.arange(3000, dtype=float)
    assert bootstrap_mean_interval(data, resamples=200, seed=9) == bootstrap_mean_interval(data, resamples=200, seed=9)


def test_one_sample_ttest_scipy():
    values = [0.1, -0.02, 0.04, 0.02, 0.1]
    result = one_sample_ttest(values, 0.01)
    reference = stats.ttest_1samp(values, 0.01)
    assert result.statistic == pytest.approx(reference.statistic)
    assert result.p_value == pytest.approx(reference.pvalue)


def test_welch_scipy():
    left = [1, 2, 4, 5, 7, 9]
    right = [1, 2, 3, 4]
    result = welch_ttest(left, right)
    reference = stats.ttest_ind(left, right, equal_var=False)
    assert result.statistic == pytest.approx(reference.statistic)
    assert result.p_value == pytest.approx(reference.pvalue)
    assert result.degrees_of_freedom == pytest.approx(reference.df)


@pytest.mark.parametrize(("data", "null", "expected_p"), [([1, 1, 1], 1, 1), ([1, 1, 1], 2, 0)])
def test_one_sample_constant(data, null, expected_p):
    assert one_sample_ttest(data, null).p_value == expected_p


def test_welch_constant_cases():
    assert welch_ttest([1, 1, 1], [1, 1, 1]).p_value == 1
    assert welch_ttest([1, 1, 1], [2, 2, 2]).p_value == 0


def test_bh_adjustment_known_example():
    p = [0.04, 0.001, 0.03, 0.04, 0.8]
    actual = benjamini_hochberg(p)
    assert actual == pytest.approx([0.05, 0.005, 0.05, 0.05, 0.8])
    assert np.all(actual >= p)
    assert np.all(actual <= 1)


def test_bh_one_p_value():
    assert benjamini_hochberg([0.25]).tolist() == [0.25]


@pytest.mark.parametrize("data", [[], [1], [1, np.nan], [1, np.inf], [[1, 2], [3, 4]]])
def test_invalid_samples(data):
    with pytest.raises(ValueError):
        t_mean_interval(data)


@pytest.mark.parametrize("confidence", [0, 1, -0.1, np.nan, 2])
def test_invalid_confidence(confidence):
    with pytest.raises(ValueError):
        t_mean_interval([0, 1], confidence)


@pytest.mark.parametrize("bad", [[-0.1], [1.001], [np.nan], []])
def test_invalid_multiple_testing_pvalues(bad):
    with pytest.raises(ValueError):
        benjamini_hochberg(bad)


def test_invalid_resampling_count():
    with pytest.raises(ValueError):
        bootstrap_mean_interval([1, 2], resamples=50)