"""Shared helpers for Docker image scripts."""

import os


def get_image_name(engine_name: str) -> str:
    """
    :param engine_name: The service engine inside the Docker image.
    :return: The Docker image name.
    """
    user = os.getenv("USER", "clp-user")
    return f"log-archival-bench-{engine_name}-ubuntu-jammy:dev-{user}"
