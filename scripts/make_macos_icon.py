"""Render the branded SVG as a retina macOS iconset and invoke Apple's iconutil."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage


def main() -> None:
    if sys.platform != "darwin":
        raise SystemExit("macOS iconutil is required for generating an .icns file")
    root = Path(__file__).resolve().parents[1]
    source = root / "assets" / "logo-original.png"
    iconset = root / "build" / "QuantStatsLab.iconset"
    iconset.mkdir(parents=True, exist_ok=True)
    original = QImage(str(source))
    if original.isNull():
        raise SystemExit(f"Cannot load original PNG icon: {source}")

    for logical in (16, 32, 128, 256, 512):
        for density, suffix in ((1, ""), (2, "@2x")):
            pixel_size = logical * density
            image = original.scaled(
                pixel_size, pixel_size, Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            filename = iconset / f"icon_{logical}x{logical}{suffix}.png"
            if not image.save(str(filename)):
                raise SystemExit(f"Cannot save icon: {filename}")

    output = root / "assets" / "logo.icns"
    subprocess.run(["iconutil", "-c", "icns", "-o", str(output), str(iconset)], check=True)
    print(f"Created {output}")


if __name__ == "__main__":
    main()
