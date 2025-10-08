# This file is used for building the container, ensuring installation of the required tool and
# dependencies

# If there is any dedicated image available, you should build the benchmarking image on top of that
FROM ubuntu@sha256:1ec65b2719518e27d4d25f104d93f9fac60dc437f81452302406825c46fcc9cb

# Install necessary packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-downgrades \
    tmux \
    vim \
    gzip=1.10-4ubuntu4.1

