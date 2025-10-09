#!/usr/bin/env python3
"""Build a Docker image and optionally dump its configuration as JSON."""

import argparse
import subprocess
import sys
from pathlib import Path

from log_archival_bench.scripts.docker_images.utils import get_image_name
from log_archival_bench.utils.path_utils import (
    get_config_dir,
    get_package_root,
    which,
)


def main(argv: list[str]) -> int:
    """
    Build a Docker image and optionally dump its configuration as JSON.

    :param argv:
    :return: 0 on success, non-zero error code on failure.
    """
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--engine-name", required=True, help="The engine to be installed inside the Docker image."
    )
    args_parser.add_argument(
        "--dump-config-path", help="Path to the file to dump the Docker image JSON metadata."
    )

    parsed_args = args_parser.parse_args(argv[1:])
    engine_name = parsed_args.engine_name
    dump_config_path = parsed_args.dump_config_path

    image_name = get_image_name(engine_name)

    docker_file_path = get_config_dir() / "docker-images" / engine_name / "Dockerfile"
    if not docker_file_path.is_file():
        err_msg = f"Dockerfile for `{engine_name}` does not exist."
        raise RuntimeError(err_msg)

    docker_bin = which("docker")
    # fmt: off
    build_cmds = [
      docker_bin,
      "build",
      "--tag", image_name,
      str(get_package_root()),
      "--file", str(docker_file_path),
    ]
    # fmt: on
    subprocess.run(build_cmds, check=True)

    if dump_config_path is not None:
        output_path = Path(dump_config_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            dump_cmds = [
                docker_bin,
                "inspect",
                "--type=image",
                image_name,
            ]
            subprocess.run(dump_cmds, check=True, stdout=f)

    return 0


if "__main__" == __name__:
    sys.exit(main(sys.argv))
