#!/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
dockerfile_dir="${script_dir}/../images/"
project_root="${script_dir}/../../../"

if [[ $# -lt 1 || $# -gt 3 ]]; then
  echo "Usage: $0 <docker-env-engine> [image-repo] [image-tag]" >&2
  exit 1
fi

engine="$1"
repo="${2:-log-archival-bench-${engine}-ubuntu-jammy}"
tag="${3:-dev}"

build_cmd=(
    docker build
    --tag "${repo}:${tag}"
    "$project_root"
    --file "${dockerfile_dir}/${engine}/Dockerfile"
)

if command -v git >/dev/null && git -C "$script_dir" rev-parse --is-inside-work-tree >/dev/null ;
then
    build_cmd+=(
        --label "org.opencontainers.image.revision=$(git -C "$script_dir" rev-parse HEAD)"
        --label "org.opencontainers.image.source=$(git -C "$script_dir" remote get-url origin)"
    )
fi

"${build_cmd[@]}"
