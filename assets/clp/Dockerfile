# FROM ghcr.io/y-scope/clp/clp-core-x86-ubuntu-jammy:main

FROM ghcr.io/y-scope/clp/clp-core-x86-ubuntu-jammy@sha256:67c34b94fe1bdbf81846a20ebcf3920c5e26f8ba6ae392747a4cd36b47fc05e4
# this is commit bb8244c32b6649bc92901c2cadb6be4e3bf48607

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
