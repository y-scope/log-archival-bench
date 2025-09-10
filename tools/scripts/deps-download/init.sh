#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
project_root_dir="$script_dir/../../../"
download_dep_script="$script_dir/download-dep.py"

readonly YSCOPE_DEV_UTILS_COMMIT_SHA="3ff7d055c01b7b2b94b9288e0fdc33a5c937a64e"
python3 "${download_dep_script}" \
    "https://github.com/y-scope/yscope-dev-utils/archive/${YSCOPE_DEV_UTILS_COMMIT_SHA}.zip" \
    "yscope-dev-utils-${YSCOPE_DEV_UTILS_COMMIT_SHA}" \
    "${project_root_dir}/tools/yscope-dev-utils" \
    --extract
