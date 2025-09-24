# TODO: use the latest version until the clp core deps images are properly tagged with versions.
FROM ghcr.io/y-scope/clp/clp-core-x86-ubuntu-jammy:main

FROM ghcr.io/y-scope/clp/clp-core-dependencies-x86-ubuntu-jammy:main

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    htop \
    jq \
    python3-venv \
    rsync \
    sqlite3 \
    tmux \
    vim

COPY --from=0 /clp/clp-s /clp/clp-s
