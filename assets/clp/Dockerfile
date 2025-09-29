# TODO: use properly tagged image version
FROM ghcr.io/y-scope/clp/clp-core-x86-ubuntu-jammy@sha256:e82b958b43289f2e6553057e5649f56740fa7183d299c0fcb9adc55068ae2bf2 \
    AS clp-core

FROM ghcr.io/y-scope/clp/clp-core-dependencies-x86-ubuntu-jammy@sha256:49c0edf1cdd8e92bae2f46509d7e0032da7ae405f4afc58ae3e3abfe7c448e34 \
    AS clp-deps-core

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    htop \
    jq \
    python3-venv \
    rsync \
    sqlite3 \
    tmux \
    vim

COPY --from=clp-core /clp/clp-s /clp/clp-s
