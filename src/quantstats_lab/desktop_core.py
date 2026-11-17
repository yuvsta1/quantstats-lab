"""Pure input/output helpers for the local desktop interface.

No GUI imports: these functions remain independently testable.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from .validation import observations, simple_returns

MAX_CSV_BYTES = 5_000_000
MAX_CSV_ROWS = 100_000


def parse_observations(text: str, minimum: int = 2) -> NDArray[np.float64]:
    """Parse comma/newline/semicolon separated real numbers; never drop malformed values."""
    tokens = [part.strip() for part in text.replace("\n", ",").replace(";", ",").split(",")]
    if not tokens or any(not token for token in tokens):
        raise ValueError("Enter numbers separated by commas, with no empty entries")
    try:
        values = [float(token) for token in tokens]
    except ValueError as exc:
        raise ValueError("Each observation must be a numeric value") from exc
    return observations(values, minimum=minimum)


def read_return_columns(path: str | Path) -> dict[str, NDArray[np.float64]]:
    """Load valid numeric CSV columns without silently cleaning invalid observations.

    The user chooses a numeric column containing decimal simple returns, not prices.
    No network requests or upload is performed.
    """
    path = Path(path)
    if not path.is_file():
        raise ValueError("The selected CSV file does not exist")
    if path.stat().st_size > MAX_CSV_BYTES:
        raise ValueError("CSV exceeds the 5 MB limit")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError("CSV must have unique column headers")
            columns: dict[str, list[str]] = {name: [] for name in reader.fieldnames}
            count = 0
            for record in reader:
                count += 1
                if count > MAX_CSV_ROWS:
                    raise ValueError("CSV exceeds the 100,000-row limit")
                if None in record:
                    raise ValueError("CSV contains extra fields in a row")
                for name in columns:
                    value = record[name]
                    columns[name].append("" if value is None else value.strip())
    except (UnicodeError, csv.Error) as exc:
        raise ValueError("The CSV could not be decoded or parsed") from exc

    numeric: dict[str, NDArray[np.float64]] = {}
    for name, values in columns.items():
        if len(values) < 2 or any(not value for value in values):
            continue
        try:
            result = simple_returns([float(item) for item in values])
        except (ValueError, OverflowError, TypeError):
            continue
        if all(math.isfinite(float(item)) for item in result):
            numeric[name] = result
    if not numeric:
        raise ValueError(
            "No valid numeric return columns found. Supply at least two finite decimal simple returns; "
            "missing or invalid values are not automatically removed."
        )
    return numeric


def write_csv(path: str | Path, headings: list[str], rows: list[list[object]]) -> None:
    """Write numeric research output as UTF-8 CSV to a user-selected local path."""
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headings)
        writer.writerows(rows)
