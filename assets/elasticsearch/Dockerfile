FROM ghcr.io/y-scope/clp/clp-core-dependencies-x86-ubuntu-jammy:main

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    gpg;

RUN curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch \
    | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg]" \
    "https://artifacts.elastic.co/packages/8.x/apt stable main" \
    | tee /etc/apt/sources.list.d/elastic-8.x.list;

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    elasticsearch=8.6.2 \
    libcurl4 \
    libcurl4-openssl-dev \
    python3-pip \
    python3-venv \
    tmux \
    vim;

RUN pip3 install elasticsearch==8.6.2 requests;
