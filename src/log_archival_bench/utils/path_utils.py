import shutil
from pathlib import Path

import log_archival_bench

_PACKAGE_ROOT = Path(log_archival_bench.__file__).parent

_BUILD_DIR = _PACKAGE_ROOT / "build"
_CONFIG_DIR = _PACKAGE_ROOT / "config"


def get_package_root() -> Path:
    return _PACKAGE_ROOT


def get_build_dir() -> Path:
    return _BUILD_DIR


def get_config_dir() -> Path:
    return _CONFIG_DIR


def which(binary_name: str) -> str:
    bin_path = shutil.which(binary_name)
    if bin_path is None:
        err_msg = f"Executable for {binary_name} is not found."
        raise RuntimeError(err_msg)
    return bin_path
