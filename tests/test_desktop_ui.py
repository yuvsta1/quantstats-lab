"""Native Qt smoke tests (offscreen on CI; require the optional desktop extra)."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")
pytest.importorskip("matplotlib")

from PySide6.QtWidgets import QApplication  # noqa: E402

from quantstats_lab.desktop import MainWindow, logo_path  # noqa: E402


@pytest.fixture(scope="module")
def qtapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(qtapp):
    widget = MainWindow()
    yield widget
    widget.close()


def test_native_window_and_brand_resources(window):
    assert window.windowTitle() == "QuantStats Lab"
    assert window.navigation.count() == 6
    assert logo_path().is_file()
    assert not window.windowIcon().isNull()


@pytest.mark.parametrize("key", ["distributions", "simulation", "inference", "processes", "risk"])
def test_all_five_research_pages_calculate_without_dialog(window, key):
    window.calculate(key)
    assert key in window.exports
    assert window.pages[key].export.isEnabled()
    assert window.pages[key].summary.toPlainText()


def test_return_bootstrap_and_ar1_modes(window):
    window.sim_type.setCurrentIndex(1)
    window.sim_paths.setValue(6)
    window.sim_steps.setValue(10)
    window.calculate_simulation()
    assert len(window.exports["simulation"][1]) == 6
    window.proc_type.setCurrentIndex(1)
    window.proc_steps.setValue(8)
    window.proc_paths.setValue(4)
    window.calculate_processes()
    assert len(window.exports["processes"][1]) == 4


def test_all_distributions_and_optional_inference(window):
    for index in range(6):
        window.dist_type.setCurrentIndex(index)
        window.calculate_distributions()
        assert window.exports["distributions"][1]
    window.inf_second.setPlainText("0.2, 0.1, 0.3, 0.4")
    window.inf_pvalues.setPlainText("0.001, 0.02, 0.4")
    window.calculate_inference()
    assert "Welch" in window.pages["inference"].summary.toPlainText()
    assert "BH adjusted" in window.pages["inference"].summary.toPlainText()


def test_theme_toggle(window):
    old = window.dark
    window.toggle_theme()
    assert window.dark != old
