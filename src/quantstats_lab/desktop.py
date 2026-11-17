"""Native PySide6 research workstation; all numerical work stays in the public API.

Run with: python -m quantstats_lab.desktop
No browser, web server, remote services, or market-data connection is used.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStyleFactory,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import (
    __version__,
    autoregressive_one,
    benjamini_hochberg,
    bootstrap_mean_interval,
    bootstrap_returns,
    drawdown_series,
    evaluate_distribution,
    geometric_brownian_motion,
    historical_var_es,
    make_distribution,
    one_sample_ttest,
    ornstein_uhlenbeck,
    performance_metrics,
    t_mean_interval,
    welch_ttest,
)
from .desktop_core import parse_observations, read_return_columns, write_csv
from .desktop_theme import apply_palette, colours

matplotlib.use("QtAgg")

ACKNOWLEDGEMENT = (
    "Created by Yuvi with the assistance of AI (OpenAI ChatGPT) "
    "for software development, testing, and documentation."
)
TEAL = "#45C7C1"
NAVY = "#06172D"


def logo_path() -> Path:
    """Find the branded SVG in source checkout or PyInstaller's frozen data directory."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets" / "logo-original.png"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2] / "assets" / "logo-original.png"


def logo_pixmap(size: int) -> QPixmap:
    """Load the user's actual supplied brand artwork, preserving its proportions."""
    pixmap = QPixmap(str(logo_path()))
    return pixmap.scaled(
        size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
    )


class CompactDoubleSpinBox(QDoubleSpinBox):
    """Show significant decimal digits without five trailing zeros or tiny spin arrows."""

    def textFromValue(self, value: float) -> str:
        text = f"{value:.5f}".rstrip("0").rstrip(".")
        return "0" if text in {"", "-0"} else text


def add_field(form: QFormLayout, label: str, widget: QWidget) -> None:
    form.addRow(label, widget)
    field_label = form.labelForField(widget)
    if field_label is not None:
        field_label.setObjectName("fieldLabel")


def number(form: QFormLayout, label: str, value: float, minimum: float = -1e9, maximum: float = 1e9) -> QDoubleSpinBox:
    widget = CompactDoubleSpinBox()
    widget.setRange(minimum, maximum)
    widget.setDecimals(5)
    widget.setSingleStep(0.05)
    widget.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
    widget.setAlignment(Qt.AlignmentFlag.AlignRight)
    widget.setMinimumHeight(30)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    widget.setValue(value)
    add_field(form, label, widget)
    return widget


def whole(form: QFormLayout, label: str, value: int, minimum: int = 1, maximum: int = 10000) -> QSpinBox:
    widget = QSpinBox()
    widget.setRange(minimum, maximum)
    widget.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
    widget.setAlignment(Qt.AlignmentFlag.AlignRight)
    widget.setMinimumHeight(30)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    widget.setValue(value)
    add_field(form, label, widget)
    return widget


def choice(form: QFormLayout, label: str, options: list[str]) -> QComboBox:
    widget = QComboBox()
    widget.addItems(options)
    widget.setMinimumHeight(30)
    widget.setMaxVisibleItems(8)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    add_field(form, label, widget)
    return widget


def lines(form: QFormLayout, label: str, value: str, height: int = 62) -> QPlainTextEdit:
    widget = QPlainTextEdit()
    widget.setPlainText(value)
    widget.setFixedHeight(height)
    add_field(form, label, widget)
    return widget

class Chart(QWidget):
    """Integrated chart surface with quiet text actions instead of an oversized icon strip."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("plotPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(4)

        self.figure = Figure(figsize=(8, 5), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.hide()

        tools = QHBoxLayout()
        tools.setContentsMargins(2, 0, 2, 2)
        tools.setSpacing(2)
        caption = QLabel("VISUALISATION")
        caption.setObjectName("eyebrow")
        tools.addWidget(caption)
        tools.addStretch(1)
        for title, tooltip, callback in (
            ("Reset", "Reset chart axes", self.toolbar.home),
            ("Pan", "Drag the plot to pan", self.toolbar.pan),
            ("Zoom", "Drag over a region to zoom", self.toolbar.zoom),
            ("Save PNG", "Save the chart as an image", self.toolbar.save_figure),
        ):
            action = QToolButton()
            action.setObjectName("plotTool")
            action.setText(title)
            action.setToolTip(tooltip)
            action.clicked.connect(callback)
            tools.addWidget(action)
        layout.addLayout(tools)
        layout.addWidget(self.canvas, 1)
        self.ax = self.figure.add_subplot(111)
        self.dark = True
        self.restyle()

    def restyle(self) -> None:
        c = colours(self.dark)
        fg, bg = c["text"], c["chart"]
        self.figure.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)
        self.ax.tick_params(colors=c["muted"], labelsize=9, width=0.7)
        self.ax.xaxis.label.set_color(c["muted"])
        self.ax.yaxis.label.set_color(c["muted"])
        self.ax.title.set_color(fg)
        for spine in self.ax.spines.values():
            spine.set_color(c["border"])
        self.ax.grid(visible=False, axis="x")
        self.ax.grid(visible=True, axis="y", alpha=0.38, color=c["grid"], linewidth=0.7)
        legend = self.ax.get_legend()
        if legend is not None:
            legend.get_frame().set_facecolor(bg)
            legend.get_frame().set_edgecolor(c["border"])
            for text in legend.get_texts():
                text.set_color(fg)
        self.canvas.draw_idle()

    def clear(self, title: str, xlabel: str, ylabel: str) -> None:
        self.ax.clear()
        self.ax.set_title(title, loc="left", fontsize=11, pad=10, fontweight="semibold")
        self.ax.set_xlabel(xlabel, fontsize=9)
        self.ax.set_ylabel(ylabel, fontsize=9)

    def finish(self) -> None:
        self.restyle()

    def fan(self, paths: np.ndarray, title: str) -> None:
        self.clear(title, "Step", "Simulated value")
        axis = np.arange(paths.shape[1])
        low, med, high = np.quantile(paths, [0.05, 0.50, 0.95], axis=0)
        self.ax.fill_between(axis, low, high, color=TEAL, alpha=0.18, label="5–95% band")
        for path in paths[: min(12, len(paths))]:
            self.ax.plot(axis, path, color="#829FB0", alpha=0.17, linewidth=0.8)
        self.ax.plot(axis, med, color=TEAL, linewidth=2.3, label="Median")
        self.ax.legend(loc="best", frameon=False, fontsize=9)
        self.finish()


class ResearchPage(QWidget):
    """Compact research controls with a scrolling parameter area beside the output."""

    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 15, 18, 18)
        outer.setSpacing(5)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        outer.addWidget(heading)
        desc = QLabel(subtitle)
        desc.setWordWrap(True)
        desc.setObjectName("subtitle")
        outer.addWidget(desc)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setHandleWidth(8)
        controls = QFrame()
        controls.setObjectName("controlPanel")
        controls.setMinimumWidth(294)
        controls.setMaximumWidth(384)
        control_layout = QVBoxLayout(controls)
        control_layout.setContentsMargins(14, 12, 14, 12)
        control_layout.setSpacing(8)

        group = QGroupBox("RESEARCH PARAMETERS")
        self.form = QFormLayout(group)
        self.form.setHorizontalSpacing(10)
        self.form.setVerticalSpacing(8)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        scroller = QScrollArea()
        scroller.setFrameShape(QFrame.Shape.NoFrame)
        scroller.setWidgetResizable(True)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroller.setWidget(group)
        control_layout.addWidget(scroller, 1)

        self.run = QPushButton("Run analysis")
        self.run.setObjectName("primaryButton")
        self.run.setToolTip("Calculate the model with the current parameters")
        control_layout.addWidget(self.run)

        summary_label = QLabel("RESEARCH OUTPUT")
        summary_label.setObjectName("eyebrow")
        control_layout.addWidget(summary_label)
        self.summary = QPlainTextEdit()
        self.summary.setObjectName("summary")
        self.summary.setReadOnly(True)
        self.summary.setFixedHeight(115)
        self.summary.setPlainText("Use Run analysis to refresh this model.")
        control_layout.addWidget(self.summary)

        self.export = QPushButton("Export CSV…")
        self.export.setToolTip("Save results to a CSV file")
        self.export.setEnabled(False)
        control_layout.addWidget(self.export)

        self.chart = Chart()
        self.chart.setMinimumWidth(370)
        split.addWidget(controls)
        split.addWidget(self.chart)
        split.setSizes([330, 820])
        split.setStretchFactor(1, 2)
        outer.addWidget(split, 1)

class MainWindow(QMainWindow):
    LABELS = ["Distributions", "Monte Carlo", "Statistical inference", "Stochastic processes", "Risk analytics", "About"]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QuantStats Lab")
        self.setWindowIcon(QIcon(logo_pixmap(256)))
        self.resize(1190, 735)
        self.setMinimumSize(930, 610)
        app = QApplication.instance()
        if app is not None:
            app.setStyle(QStyleFactory.create("Fusion"))
        self.dark = True
        self.exports: dict[str, tuple[list[str], list[list[object]]]] = {}
        self.returns = np.random.default_rng(42).normal(0.0003, 0.012, size=504)
        self.returns_label = "Synthetic demonstration returns (not market data)"
        root = QWidget()
        root.setObjectName("centralRoot")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(184)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(11, 14, 11, 12)
        side_layout.setSpacing(5)
        brand = QLabel()
        brand.setPixmap(logo_pixmap(56))
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(brand)
        name = QLabel("QUANTSTATS LAB")
        name.setObjectName("brandName")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(name)
        tagline = QLabel("QUANT RESEARCH WORKSTATION")
        tagline.setObjectName("brandTagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(tagline)
        side_layout.addSpacing(18)
        self.navigation = QListWidget()
        self.navigation.addItems(self.LABELS)
        self.navigation.setObjectName("navigation")
        self.navigation.setSpacing(1)
        side_layout.addWidget(self.navigation, 1)
        seed_label = QLabel("REPRODUCIBLE SEED")
        seed_label.setObjectName("sidebarCaption")
        side_layout.addWidget(seed_label)
        self.seed = QSpinBox()
        self.seed.setRange(0, 2_147_483_647)
        self.seed.setValue(42)
        self.seed.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.seed.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.seed.setMinimumHeight(30)
        side_layout.addWidget(self.seed)
        side_layout.addSpacing(9)
        self.theme_switch = QPushButton("Switch to light mode")
        self.theme_switch.clicked.connect(self.toggle_theme)
        side_layout.addWidget(self.theme_switch)
        status = QLabel("OFFLINE-READY  ·  NO ACCOUNT")
        status.setObjectName("sidebarCaption")
        side_layout.addWidget(status)
        layout.addWidget(sidebar)
        self.stack = QStackedWidget()
        self.stack.setObjectName("workPages")
        layout.addWidget(self.stack, 1)
        self.pages: dict[str, ResearchPage] = {}
        self._distributions()
        self._monte_carlo()
        self._inference()
        self._processes()
        self._risk()
        self._about()
        self.navigation.currentRowChanged.connect(self.show_page)
        self.apply_theme()
        self.navigation.setCurrentRow(0)

    def show_page(self, index: int) -> None:
        """Render a useful default chart when a research page first opens."""
        self.stack.setCurrentIndex(index)
        keys = ("distributions", "simulation", "inference", "processes", "risk")
        if 0 <= index < len(keys) and keys[index] not in self.exports:
            self.calculate(keys[index])

    def add_page(self, key: str, title: str, subtitle: str) -> ResearchPage:
        page = ResearchPage(title, subtitle)
        page.run.clicked.connect(lambda: self.calculate(key))
        page.export.clicked.connect(lambda: self.export_results(key))
        self.stack.addWidget(page)
        self.pages[key] = page
        return page

    def _distributions(self) -> None:
        page = self.add_page(
            "distributions",
            "Probability distributions",
            "Inspect PDFs/PMFs, cumulative probabilities, moments and tail quantiles.",
        )
        self.dist_type = choice(page.form, "Distribution", [
            "normal", "student_t", "binomial", "poisson", "exponential", "lognormal",
        ])
        self.dist_parameters = QStackedWidget()
        self.dist_parameters.setObjectName("parameterStack")
        specs = [
            [("mean", 0.0, -1e6, 1e6), ("std", 1.0, 0.0001, 1e6)],
            [("df", 5.0, 0.0001, 1e6), ("loc", 0.0, -1e6, 1e6), ("scale", 1.0, 0.0001, 1e6)],
            [("n", 20, 0, 100000), ("p", 0.5, 0, 1)],
            [("rate", 5.0, 0.0001, 1e6)],
            [("scale", 1.0, 0.0001, 1e6)],
            [("shape", 0.5, 0.0001, 1e6), ("scale", 1.0, 0.0001, 1e6)],
        ]
        self.dist_inputs: list[dict[str, QDoubleSpinBox | QSpinBox]] = []
        for i, fields in enumerate(specs):
            panel = QWidget()
            panel.setObjectName("parameterPanel")
            form = QFormLayout(panel)
            form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            form.setHorizontalSpacing(10)
            form.setVerticalSpacing(7)
            mapping = {}
            for field, default, minimum, maximum in fields:
                if i == 2 and field == "n":
                    mapping[field] = whole(form, "Trials n", default, minimum=0, maximum=maximum)
                else:
                    mapping[field] = number(form, field.replace("_", " ").title(), default, minimum, maximum)
            self.dist_parameters.addWidget(panel)
            self.dist_inputs.append(mapping)
        page.form.addRow(self.dist_parameters)
        self.dist_type.currentIndexChanged.connect(self.dist_parameters.setCurrentIndex)
        self.dist_x = number(page.form, "Evaluate at x", 0.0)

    def _monte_carlo(self) -> None:
        page = self.add_page(
            "simulation",
            "Monte Carlo laboratory",
            "Seeded scenario fans. GBM assumptions are not calibrated investment forecasts.",
        )
        self.sim_type = choice(page.form, "Model", ["Geometric Brownian motion", "IID return bootstrap"])
        self.sim_initial = number(page.form, "Initial value", 100.0, 0.0001)
        self.sim_drift = number(page.form, "Annual drift (decimal)", 0.06)
        self.sim_volatility = number(page.form, "Annual volatility (decimal)", 0.20, 0)
        self.sim_steps = whole(page.form, "Steps", 252, 1, 2520)
        self.sim_paths = whole(page.form, "Paths", 500, 1, 20000)
        self.sim_observations = lines(page.form, "Bootstrap returns (decimals)", "0.012, -0.009, 0.003, 0.004")
        self.sim_type.currentIndexChanged.connect(lambda _index: self.update_simulation_fields())
        self.update_simulation_fields()

    def update_simulation_fields(self) -> None:
        """Display only the parameters used by the currently selected model."""
        form = self.pages["simulation"].form
        bootstrap = self.sim_type.currentIndex() == 1
        form.setRowVisible(self.sim_drift, not bootstrap)
        form.setRowVisible(self.sim_volatility, not bootstrap)
        form.setRowVisible(self.sim_observations, bootstrap)

    def _inference(self) -> None:
        page = self.add_page(
            "inference",
            "Statistical inference",
            "Student-t mean intervals, IID bootstrap, hypothesis tests, Welch and BH correction.",
        )
        self.inf_values = lines(page.form, "Sample A", "0.2, 0.4, -0.1, 0.8, 0.5, 0.0, 0.3, 0.2")
        self.inf_conf = number(page.form, "Confidence", 0.95, 0.001, 0.999)
        self.inf_resamples = whole(page.form, "Bootstrap resamples", 3000, 100, 100000)
        self.inf_null = number(page.form, "Null mean", 0.0)
        self.inf_second = lines(page.form, "Sample B for Welch (optional)", "")
        self.inf_pvalues = lines(page.form, "p-values for BH (optional)", "")

    def _processes(self) -> None:
        page = self.add_page(
            "processes",
            "Stochastic processes",
            "Exact Ornstein–Uhlenbeck transitions or stationary discrete AR(1) processes.",
        )
        self.proc_type = choice(page.form, "Process", ["Ornstein–Uhlenbeck", "AR(1)"])
        self.proc_initial = number(page.form, "Initial state", 1.0)
        self.proc_mean = number(page.form, "Long-run mean", 0.0)
        self.proc_theta = number(page.form, "OU mean reversion", 3.0, 0.0001)
        self.proc_phi = number(page.form, "AR coefficient φ", 0.85, -0.999, 0.999)
        self.proc_vol = number(page.form, "Volatility / innovation std", 0.6, 0)
        self.proc_steps = whole(page.form, "Steps", 252, 1, 2520)
        self.proc_paths = whole(page.form, "Paths", 100, 1, 20000)
        self.proc_type.currentIndexChanged.connect(lambda _index: self.update_process_fields())
        self.update_process_fields()

    def update_process_fields(self) -> None:
        form = self.pages["processes"].form
        is_ou = self.proc_type.currentIndex() == 0
        form.setRowVisible(self.proc_theta, is_ou)
        form.setRowVisible(self.proc_phi, not is_ou)

    def _risk(self) -> None:
        page = self.add_page(
            "risk",
            "Historical risk analytics",
            "Returns must be decimal simple returns (0.01 = 1%), not prices.",
        )
        self.risk_source = QLabel(self.returns_label)
        self.risk_source.setWordWrap(True)
        page.form.addRow("Data source", self.risk_source)
        import_button = QPushButton("Import local CSV…")
        import_button.clicked.connect(self.import_csv)
        page.form.addRow(import_button)
        demo_button = QPushButton("Use synthetic sample")
        demo_button.clicked.connect(self.use_demo)
        page.form.addRow(demo_button)
        self.risk_conf = number(page.form, "Tail confidence", 0.95, 0.001, 0.999)
        self.risk_frequency = choice(page.form, "Periods per year", ["252", "365", "52", "12"])

    def _about(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(42, 32, 42, 32)
        logo = QLabel()
        logo.setPixmap(logo_pixmap(148))
        layout.addWidget(logo)
        title = QLabel("QuantStats Lab")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        info = QLabel(
            "A local-first, open-source research workbench for reproducible statistics, "
            "simulation, inference and descriptive risk analytics.\n\n"
            "Quantitative outputs are educational and model-based, not trading signals, "
            "investment advice or guaranteed forecasts.\n\n"
            f"MIT License · Version {__version__}\n\n" + ACKNOWLEDGEMENT
        )
        info.setWordWrap(True)
        info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(info)
        update_button = QPushButton("See latest downloadable version on GitHub")
        update_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/yuvsta1/quantstats-lab/releases/latest"))
        )
        layout.addWidget(update_button)
        layout.addStretch(1)
        self.stack.addWidget(page)

    def calculate(self, key: str) -> None:
        """One UI boundary for validation and nonfatal errors."""
        try:
            getattr(self, f"calculate_{key}")()
        except (ValueError, OverflowError, OSError, TypeError, MemoryError) as exc:
            QMessageBox.warning(self, "Check the research inputs", str(exc))

    def report(self, key: str, summary: str, columns: list[str], rows: list[list[object]]) -> None:
        self.pages[key].summary.setPlainText(summary)
        self.exports[key] = (columns, rows)
        self.pages[key].export.setEnabled(True)

    def calculate_distributions(self) -> None:
        kind = self.dist_type.currentText()
        params = {name: control.value() for name, control in self.dist_inputs[self.dist_type.currentIndex()].items()}
        result = evaluate_distribution(kind, self.dist_x.value(), **params)
        frozen, discrete = make_distribution(kind, **params)
        low, high = float(frozen.ppf(0.001)), float(frozen.ppf(0.999))
        if not (np.isfinite(low) and np.isfinite(high)) or high <= low:
            raise ValueError("Distribution quantile range is not finite; reduce extreme parameters")
        chart = self.pages["distributions"].chart
        chart.clear("Probability mass" if discrete else "Probability density", "Value", "PMF" if discrete else "PDF")
        if discrete:
            start, end = max(0, int(np.floor(low))), int(np.ceil(high))
            xx = np.unique(np.linspace(start, end, min(201, end - start + 1)).astype(int))
            yy = frozen.pmf(xx)
            chart.ax.bar(xx, yy, color=TEAL, width=0.8)
        else:
            xx = np.linspace(low, high, 400)
            yy = frozen.pdf(xx)
            chart.ax.plot(xx, yy, color=TEAL, linewidth=2.6)
        chart.ax.axvline(result.x, color="#EAAD64", linestyle="--", alpha=0.85)
        chart.finish()
        summary = (
            f"PDF / PMF: {result.mass_or_density:.6g}\n"
            f"CDF: {result.cdf:.6g}   Survival: {result.survival:.6g}\n"
            f"Mean: {result.mean:.6g}   SD: {result.standard_deviation:.6g}\n"
            f"5% / 50% / 95%: {result.q05:.5g} / {result.median:.5g} / {result.q95:.5g}"
        )
        self.report("distributions", summary, ["x", "mass_or_density"], [[float(x), float(y)] for x, y in zip(xx, yy, strict=True)])

    def calculate_simulation(self) -> None:
        initial = self.sim_initial.value()
        steps, paths = self.sim_steps.value(), self.sim_paths.value()
        if self.sim_type.currentIndex() == 0:
            output = geometric_brownian_motion(
                initial, self.sim_drift.value(), self.sim_volatility.value(),
                steps=steps, paths=paths, seed=self.seed.value(),
            )
            label = "Geometric Brownian motion"
        else:
            source = parse_observations(self.sim_observations.toPlainText())
            output = bootstrap_returns(source, initial=initial, steps=steps, paths=paths, seed=self.seed.value())
            label = "IID bootstrap (historical resampling)"
        self.pages["simulation"].chart.fan(output.paths, label)
        self.report(
            "simulation",
            f"Terminal mean: {output.terminal_mean:.4f}\n"
            f"Terminal median: {output.terminal_median:.4f}\n"
            f"5–95% terminal: {output.terminal_p05:.4f} to {output.terminal_p95:.4f}\n"
            "Simulated outcomes are not forecasts.",
            ["simulation_id", "terminal_value"],
            [[i + 1, float(value)] for i, value in enumerate(output.paths[:, -1])],
        )

    def calculate_inference(self) -> None:
        data = parse_observations(self.inf_values.toPlainText())
        conf = self.inf_conf.value()
        t_int = t_mean_interval(data, confidence=conf)
        boot = bootstrap_mean_interval(
            data, confidence=conf, resamples=self.inf_resamples.value(), seed=self.seed.value(),
        )
        test = one_sample_ttest(data, null_mean=self.inf_null.value())
        desc = (
            f"Student-t CI: [{t_int.lower:.5g}, {t_int.upper:.5g}]\n"
            f"IID bootstrap CI: [{boot.lower:.5g}, {boot.upper:.5g}]\n"
            f"One-sample t: {test.statistic:.5g}   p = {test.p_value:.5g}"
        )
        rows: list[list[object]] = [
            ["student-t", t_int.estimate, t_int.lower, t_int.upper],
            ["IID bootstrap", boot.estimate, boot.lower, boot.upper],
        ]
        second = self.inf_second.toPlainText().strip()
        if second:
            welch = welch_ttest(data.tolist(), parse_observations(second).tolist())
            desc += f"\nWelch t: {welch.statistic:.5g}   p = {welch.p_value:.5g}"
        pvalues = self.inf_pvalues.toPlainText().strip()
        if pvalues:
            raw = parse_observations(pvalues, minimum=1)
            adj = benjamini_hochberg(raw)
            desc += "\nBH adjusted p-values: " + ", ".join(f"{item:.4g}" for item in adj)
        chart = self.pages["inference"].chart
        chart.clear("Mean confidence intervals", "Sample mean", "Method")
        mean = t_int.estimate
        chart.ax.errorbar(
            [mean, mean], [1, 0],
            xerr=[[mean - t_int.lower, mean - boot.lower], [t_int.upper - mean, boot.upper - mean]],
            fmt="o", capsize=7, color=TEAL,
        )
        chart.ax.set_yticks([0, 1], ["IID bootstrap", "Student-t"])
        chart.ax.axvline(self.inf_null.value(), linestyle="--", color="#EAAD64", label="Null mean")
        chart.ax.legend(frameon=False)
        chart.finish()
        self.report("inference", desc + "\nIID assumptions apply; results are not probabilities of the null.", ["method", "mean", "low", "high"], rows)

    def calculate_processes(self) -> None:
        params = {
            "initial": self.proc_initial.value(),
            "long_run_mean": self.proc_mean.value(),
            "steps": self.proc_steps.value(),
            "paths": self.proc_paths.value(),
            "seed": self.seed.value(),
        }
        if self.proc_type.currentIndex() == 0:
            simulations = ornstein_uhlenbeck(
                **params, mean_reversion=self.proc_theta.value(), volatility=self.proc_vol.value(),
            )
            name = "Ornstein–Uhlenbeck"
        else:
            simulations = autoregressive_one(
                **params, phi=self.proc_phi.value(), innovation_std=self.proc_vol.value(),
            )
            name = "AR(1)"
        self.pages["processes"].chart.fan(simulations, name)
        self.report(
            "processes",
            f"{name}\nFinal median: {np.median(simulations[:, -1]):.5g}\n"
            f"Final std: {np.std(simulations[:, -1]):.5g}\n"
            "Models a state process, not necessarily a security price.",
            ["path", "terminal_value"],
            [[i + 1, float(v)] for i, v in enumerate(simulations[:, -1])],
        )

    def calculate_risk(self) -> None:
        risk = historical_var_es(self.returns, confidence=self.risk_conf.value())
        perf = performance_metrics(self.returns, periods_per_year=int(self.risk_frequency.currentText()))
        chart = self.pages["risk"].chart
        series = drawdown_series(self.returns)
        chart.clear("Underwater chart", "Observation", "Drawdown")
        chart.ax.fill_between(np.arange(len(series)), series, 0, color=TEAL, alpha=0.37)
        chart.ax.plot(series, color=TEAL, linewidth=1.7)
        chart.finish()
        sharpe = "Undefined" if perf.annualised_sharpe is None else f"{perf.annualised_sharpe:.4f}"
        self.report(
            "risk",
            f"{self.returns_label}\n"
            f"VaR: {risk.value_at_risk:.2%}   ES: {risk.expected_shortfall:.2%}\n"
            f"Max drawdown: {perf.maximum_drawdown:.2%}\n"
            f"Annualised return: {perf.annualised_return:.2%}\n"
            f"Annualised volatility: {perf.annualised_volatility:.2%}   Sharpe: {sharpe}\n"
            "Descriptive historical metrics, not tail-risk forecasts.",
            ["VaR", "ES", "max_drawdown", "annualised_return", "annualised_volatility", "Sharpe"],
            [[risk.value_at_risk, risk.expected_shortfall, perf.maximum_drawdown,
              perf.annualised_return, perf.annualised_volatility, perf.annualised_sharpe]],
        )

    def import_csv(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Open local decimal returns CSV", "", "CSV files (*.csv)")
        if not filename:
            return
        try:
            columns = read_return_columns(filename)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Invalid CSV", str(exc))
            return
        if len(columns) > 1:
            name, ok = QInputDialog.getItem(self, "Choose return series", "Numeric simple-return column", list(columns), 0, False)
            if not ok:
                return
        else:
            name = next(iter(columns))
        self.returns = columns[name]
        self.returns_label = f"{Path(filename).name}: {name} ({len(self.returns)} observations)"
        self.risk_source.setText(self.returns_label)
        self.calculate("risk")

    def use_demo(self) -> None:
        self.returns = np.random.default_rng(self.seed.value()).normal(0.0003, 0.012, size=504)
        self.returns_label = "Synthetic demonstration returns (not market data)"
        self.risk_source.setText(self.returns_label)
        self.calculate("risk")

    def export_results(self, key: str) -> None:
        if key not in self.exports:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save research results", f"quantstats_{key}.csv", "CSV files (*.csv)")
        if not filename:
            return
        try:
            headings, rows = self.exports[key]
            write_csv(filename, headings, rows)
        except OSError as exc:
            QMessageBox.warning(self, "Unable to export", str(exc))

    def toggle_theme(self) -> None:
        self.dark = not self.dark
        self.theme_switch.setText("Switch to light mode" if self.dark else "Switch to dark mode")
        self.apply_theme()

    def apply_theme(self) -> None:
        """Apply a whole-window palette, including popups and embedded plots."""
        apply_palette(self, self.dark)
        for page in self.pages.values():
            page.chart.dark = self.dark
            page.chart.restyle()


def main() -> int:
    smoke = "--smoke-test" in sys.argv
    app = QApplication.instance() or QApplication([] if smoke else sys.argv)
    app.setApplicationName("QuantStats Lab")
    window = MainWindow()
    window.show()
    if smoke:
        QTimer.singleShot(750, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
