"""Optional Streamlit AppTest smoke test; executes in CI with the [app] extra."""

from pathlib import Path

import pytest

streamlit = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402


def test_streamlit_initial_render_does_not_raise():
    path = Path(__file__).resolve().parents[1] / "src" / "quantstats_lab" / "app.py"
    app = AppTest.from_file(str(path), default_timeout=30).run()
    assert not app.exception, f"Streamlit raised: {app.exception}"
    assert app.title[0].value == "QuantStats Lab"