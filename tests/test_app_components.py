"""Test web-app calculations/figures without needing a browser server."""

import importlib
import io
import sys
from unittest.mock import MagicMock

import numpy as np
import pytest

pytest.importorskip("plotly")
pytest.importorskip("pandas")


def _load_app(monkeypatch):
    if "streamlit" not in sys.modules:
        try:
            import streamlit  # noqa: F401
        except ImportError:
            monkeypatch.setitem(sys.modules, "streamlit", MagicMock())
    return importlib.import_module("quantstats_lab.app")


def test_simulation_plot_returns_plotly_figure(monkeypatch):
    mod = _load_app(monkeypatch)
    values = np.array([[100, 110, 120], [100, 90, 80], [100, 100, 100]])
    fig = mod.plot_simulation(values, "Test")
    assert fig.layout.title.text == "Test"
    assert len(fig.data) == 6  # 3 confidence traces + 3 sampled paths
    assert fig.data[2].name == "Median path"


def test_demo_returns_reproducible(monkeypatch):
    mod = _load_app(monkeypatch)
    assert np.array_equal(mod.demo_returns(42), mod.demo_returns(42))
    assert not np.array_equal(mod.demo_returns(42), mod.demo_returns(43))


def test_csv_parser_valid_file(monkeypatch):
    mod = _load_app(monkeypatch)
    monkeypatch.setattr(mod.st, "selectbox", lambda _label, columns: columns[0])
    uploaded = MagicMock()
    uploaded.getvalue.return_value = b"return,label\n0.02,a\n-0.01,b\n0.005,c\n"
    values, col = mod.parse_csv_returns(uploaded)
    assert col == "return"
    assert values.tolist() == pytest.approx([0.02, -0.01, 0.005])


@pytest.mark.parametrize("data", [b"", b"name\na\nb\n", b"a\n1\n\n2\n"])
def test_csv_parser_rejects_bad_data(monkeypatch, data):
    mod = _load_app(monkeypatch)
    monkeypatch.setattr(mod.st, "selectbox", lambda _label, columns: columns[0])
    uploaded = MagicMock()
    uploaded.getvalue.return_value = data
    if data == b"a\n1\n\n2\n":
        # pandas skips blank lines by design; this is a valid 2-point numeric CSV
        values, _ = mod.parse_csv_returns(uploaded)
        assert values.tolist() == [1, 2]
    else:
        with pytest.raises(ValueError):
            mod.parse_csv_returns(uploaded)


def test_csv_parser_size_limit(monkeypatch):
    mod = _load_app(monkeypatch)
    uploaded = MagicMock()
    uploaded.getvalue.return_value = b"a" * 5_000_001
    with pytest.raises(ValueError, match="5 MB"):
        mod.parse_csv_returns(uploaded)


def test_csv_parser_reads_csv_without_external_network(monkeypatch):
    mod = _load_app(monkeypatch)
    monkeypatch.setattr(mod.st, "selectbox", lambda _label, columns: columns[0])
    uploaded = MagicMock()
    uploaded.getvalue.return_value = io.BytesIO(b"r\n0.01\n0.02\n").getvalue()
    values, _ = mod.parse_csv_returns(uploaded)
    assert values.shape == (2,)