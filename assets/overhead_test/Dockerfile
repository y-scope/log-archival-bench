# This file is used for building the container, ensuring installation of the required tool and
# dependencies

# If there is any dedicated image available, you should build the benchmarking image on top of that
FROM ubuntu:jammy

# Install necessary packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tmux \
    vim

