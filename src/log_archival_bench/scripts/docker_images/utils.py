"""Util functions for docker image scripts."""

import os


def get_container_name(image_name: str) -> str:
    """
    :param image_name:
    :return: The full docker image container name with repo and tag.
    """
    user = os.getenv("USER", "clp-user")
    return f"log-archival-bench-{image_name}-ubuntu-jammy:dev-{user}"
