#!/usr/bin/env python3
"""Builds the specified docker container image, with optional image config dumping."""

import argparse
import subprocess
import sys
from pathlib import Path

from log_archival_bench.scripts.docker_images.utils import get_container_name
from log_archival_bench.utils.path_utils import (
    get_config_dir,
    get_package_root,
    which,
)


def main(argv: list[str]) -> int:
    """
    Builds the specified docker container image, with optional image config dumping.

    :param argv:
    :return: 0 on success, and error code on failure.
    """
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--image-name", required=True, help="Name of the docker image to build."
    )
    args_parser.add_argument(
        "--dump-config-path", help="Path to dump the docker image json info file."
    )

    parsed_args = args_parser.parse_args(argv[1:])
    image_name = parsed_args.image_name
    dump_config_path = parsed_args.dump_config_path

    docker_file_path = get_config_dir() / "docker-images" / image_name / "Dockerfile"
    if not docker_file_path.is_file():
        err_msg = f"Dockerfile for `{image_name}` does not exist."
        raise RuntimeError(err_msg)

    docker_bin = which("docker")
    # fmt: off
    build_cmds = [
      docker_bin,
      "build",
      "--tag", get_container_name(image_name),
      str(get_package_root()),
      "--file", str(docker_file_path),
    ]
    # fmt: on
    subprocess.run(build_cmds, check=True)

    if dump_config_path is not None:
        p = Path(dump_config_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            dump_cmds = [
                docker_bin,
                "inspect",
                "--type=image",
                get_container_name(image_name),
            ]
            subprocess.run(dump_cmds, check=True, stdout=f)
    return 0


if "__main__" == __name__:
    sys.exit(main(sys.argv))
