"""Build and smoke-test self-contained desktop downloads on the current OS.

Run inside a clean Python environment with desktop dependencies and PyInstaller.
This script does not publish anything. GitHub Actions publishes only after every OS succeeds.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "release-assets"
NAME = "QuantStatsLab"


def project_version() -> str:
    """Obtain the actual release version from pyproject.toml (one source of truth)."""
    with (ROOT / "pyproject.toml").open("rb") as stream:
        return str(tomllib.load(stream)["project"]["version"])


def asset_filename(system: str, machine: str, version: str) -> str:
    base = f"QuantStats-Lab-v{version}"
    if system == "Darwin":
        label = "macOS-Apple-Silicon" if machine == "arm64" else "macOS-Intel"
        return f"{base}-{label}.zip"
    if system == "Windows":
        return f"{base}-Windows-x64.exe"
    if system == "Linux":
        return f"{base}-Linux-x64.tar.gz"
    raise ValueError(f"Unsupported platform: {system} ({machine})")


def run(*args: str, **kwargs: object) -> None:
    """Print and run a checked subprocess."""
    print("+", " ".join(map(str, args)), flush=True)
    subprocess.run(args, check=True, cwd=ROOT, **kwargs)


def render_windows_icon() -> Path:
    from PIL import Image

    source = ROOT / "assets" / "logo-original.png"
    dest = ROOT / "build" / "logo.ico"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        rgba = image.convert("RGBA").resize((256, 256), Image.Resampling.LANCZOS)
        rgba.save(dest, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return dest


def package_linux(folder: Path, version: str) -> None:
    """Create a portable tar.gz and GUI-installable Debian package from the same tested binary."""
    bundle = folder / NAME
    tar_path = ASSETS / asset_filename("Linux", "x86_64", version)
    with tarfile.open(tar_path, "w:gz") as archive:
        archive.add(bundle, arcname=NAME)

    staging = ROOT / "build" / "debroot"
    if staging.exists():
        shutil.rmtree(staging)
    install_dir = staging / "opt" / "quantstats-lab" / NAME
    install_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundle, install_dir, symlinks=True)

    desktop_dir = staging / "usr" / "share" / "applications"
    desktop_dir.mkdir(parents=True)
    (desktop_dir / "quantstats-lab.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=QuantStats Lab\n"
        "Comment=Local quantitative research workstation\n"
        "Exec=/opt/quantstats-lab/QuantStatsLab/QuantStatsLab\n"
        "Icon=quantstats-lab\n"
        "Terminal=false\n"
        "Categories=Education;Science;\n"
        "StartupNotify=true\n",
        encoding="utf-8",
    )
    icon_dir = staging / "usr" / "share" / "icons" / "hicolor" / "192x192" / "apps"
    icon_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "assets" / "logo-original.png", icon_dir / "quantstats-lab.png")
    control = staging / "DEBIAN"
    control.mkdir()
    (control / "control").write_text(
        f"Package: quantstats-lab\nVersion: {version}\nSection: science\n"
        "Priority: optional\nArchitecture: amd64\nMaintainer: Yuvi <noreply@github.com>\n"
        "Depends: libc6 (>= 2.35), libegl1, libgl1, libxkbcommon-x11-0, libxcb-cursor0\n"
        "Description: QuantStats Lab native quantitative research desktop application\n"
        " Local-first probability, Monte Carlo simulation, inference and risk analytics.\n",
        encoding="utf-8",
    )
    deb = ASSETS / f"QuantStats-Lab-v{version}-Linux-x64.deb"
    run("dpkg-deb", "--build", "--root-owner-group", str(staging), str(deb))


def main() -> None:
    os.chdir(ROOT)
    version = project_version()
    system, machine = platform.system(), platform.machine().lower()
    print(f"Building QuantStats Lab v{version} on {system}/{machine}, Python {platform.python_version()}")
    if system == "Darwin" and machine not in {"arm64", "x86_64"}:
        raise SystemExit(f"Unsupported macOS architecture: {machine}")
    if system == "Windows" and machine not in {"amd64", "x86_64"}:
        raise SystemExit(f"Unsupported Windows architecture: {machine}")
    if system == "Linux" and machine not in {"x86_64", "amd64"}:
        raise SystemExit(f"Unsupported Linux architecture: {machine}")

    ASSETS.mkdir(exist_ok=True)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean", "--noconfirm", "--windowed",
        "--name", NAME,
        "--add-data", f"assets/logo-original.png{os.pathsep}assets",
    ]
    if system == "Darwin":
        run(sys.executable, "scripts/make_macos_icon.py")
        cmd += ["--onedir", "--icon", "assets/logo.icns", "--osx-bundle-identifier", "io.github.yuvsta1.quantstatslab"]
    elif system == "Windows":
        cmd += ["--onefile", "--icon", str(render_windows_icon())]
    else:
        cmd += ["--onedir"]

    cmd.append("scripts/desktop_entry.py")
    run(*cmd)

    if system == "Darwin":
        binary = ROOT / "dist" / f"{NAME}.app" / "Contents" / "MacOS" / NAME
    elif system == "Windows":
        binary = ROOT / "dist" / f"{NAME}.exe"
    else:
        binary = ROOT / "dist" / NAME / NAME
    if not binary.is_file():
        raise FileNotFoundError(f"PyInstaller did not create executable: {binary}")

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["QT_OPENGL"] = "software"
    print("+ launch packaged executable --smoke-test", flush=True)
    subprocess.run([str(binary), "--smoke-test"], env=env, cwd=ROOT, check=True, timeout=120)

    if system == "Darwin":
        from_app = ROOT / "dist" / f"{NAME}.app"
        to_app = ROOT / "dist" / "QuantStats Lab.app"
        from_app.rename(to_app)
        plist = to_app / "Contents" / "Info.plist"
        if not plist.is_file():
            raise FileNotFoundError(f"Missing macOS bundle metadata: {plist}")
        run("plutil", "-lint", str(plist))
        run("ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(to_app),
            str(ASSETS / asset_filename(system, machine, version)))
    elif system == "Windows":
        shutil.copy2(binary, ASSETS / asset_filename(system, machine, version))
    else:
        package_linux(ROOT / "dist", version)

    for item in sorted(ASSETS.iterdir()):
        if item.is_file():
            print(f"READY: {item.name} ({item.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
