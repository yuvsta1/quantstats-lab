"""The release filenames and metadata must remain internally consistent."""

from quantstats_lab import __version__
from scripts.build_desktop_release import asset_filename, project_version


def test_version_matches_package():
    assert project_version() == __version__


def test_download_names_for_all_supported_platforms():
    version = project_version()
    assert asset_filename("Windows", "amd64", version) == f"QuantStats-Lab-v{version}-Windows-x64.exe"
    assert asset_filename("Darwin", "arm64", version) == f"QuantStats-Lab-v{version}-macOS-Apple-Silicon.zip"
    assert asset_filename("Darwin", "x86_64", version) == f"QuantStats-Lab-v{version}-macOS-Intel.zip"
    assert asset_filename("Linux", "x86_64", version) == f"QuantStats-Lab-v{version}-Linux-x64.tar.gz"
