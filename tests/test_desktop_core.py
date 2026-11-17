"""Non-GUI verification of offline desktop file import and research inputs."""

import csv

import numpy as np
import pytest

from quantstats_lab.desktop_core import parse_observations, read_return_columns, write_csv


def test_parse_observations_multiple_separators():
    np.testing.assert_allclose(parse_observations("1, 2\n-3;4"), [1.0, 2.0, -3.0, 4.0])


@pytest.mark.parametrize("text", ["1,,2", "", "NaN,1", "1,inf", "1,abc", "2"])
def test_parse_observations_rejects_invalid_values(text):
    with pytest.raises(ValueError):
        parse_observations(text)


def test_parse_observations_single_value_when_explicitly_allowed():
    np.testing.assert_array_equal(parse_observations("0.03", minimum=1), [0.03])


def test_import_return_columns_no_data_loss(tmp_path):
    path = tmp_path / "returns.csv"
    path.write_text("date,return,another\n2026-01-01,0.01,0.03\n2026-01-02,-0.02,0.00\n", encoding="utf-8")
    columns = read_return_columns(path)
    assert list(columns) == ["return", "another"]
    np.testing.assert_allclose(columns["return"], [0.01, -0.02])


@pytest.mark.parametrize("content", [
    "return\n0.02\n",
    "return\n0.01\n\n",
    "return\n0.01\nnope\n",
    "return\n0.01\n-1.5\n",
    "return\n0.01\ninf\n",
    "return\n0.01\nnan\n",
    "r,r\n0.01,0.02\n0.02,0.03\n",
])
def test_import_rejects_invalid_column(tmp_path, content):
    path = tmp_path / "invalid.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        read_return_columns(path)


def test_csv_byte_limit(tmp_path):
    path = tmp_path / "huge.csv"
    with path.open("wb") as handle:
        handle.truncate(5_000_001)
    with pytest.raises(ValueError, match="5 MB"):
        read_return_columns(path)


def test_csv_export_round_trip(tmp_path):
    path = tmp_path / "export.csv"
    write_csv(path, ["scenario", "terminal"], [[1, 100.2], [2, 94.5]])
    with path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.reader(handle)) == [
            ["scenario", "terminal"], ["1", "100.2"], ["2", "94.5"],
        ]
