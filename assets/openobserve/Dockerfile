# This file is used for building the container, ensuring installation of the required tool and
# dependencies

# If there is any dedicated image available, you should build the benchmarking image on top of that
FROM public.ecr.aws/zinclabs/openobserve:v0.15.0-rc1

FROM ghcr.io/y-scope/clp/clp-core-dependencies-x86-ubuntu-jammy:main

COPY --from=0 /openobserve /openobserve
COPY --from=0 /lib/x86_64-linux-gnu/liblzma.so.5 /lib/x86_64-linux-gnu/liblzma.so.5
COPY --from=0 /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1

ENV ZO_ROOT_USER_EMAIL="root@clpbench.com"
ENV ZO_ROOT_USER_PASSWORD="password"

# Install necessary packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tmux \
    vim \
    python3-requests \
    netcat

