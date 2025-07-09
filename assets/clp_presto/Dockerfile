# FROM ghcr.io/y-scope/clp/clp-core-dependencies-x86-ubuntu-jammy:main
FROM presto/prestissimo-dependency:ubuntu-22.04
# FROM presto/prestissimo-dependency:latest
# FROM prestodb/presto-native-dependency:latest

# Install necessary packages
RUN apt-get update;

# Install necessary packages (alphabetized)
RUN apt-get install -y \
    bash \
    build-essential \
    ca-certificates \
    curl \
    gdb \
    git \
    lsb-release \
    maven \
    netcat \
    openjdk-11-jdk \
    openssh-server \
    python3 \
    python3-pip \
    rsync \
    software-properties-common \
    sudo \
    tmux \
    unzip \
    vim \
    wget \
    zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

# RUN apt-get install -y \
#     tmux \
#     vim \
#     libsnappy-dev \
#     libdouble-conversion-dev \
#     libre2-dev \
#     libgflags-dev \
#     libboost-all-dev;

# Install Task
RUN cd /usr/local && sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d;

RUN pip3 install pyarrow;

WORKDIR /home
RUN git clone https://github.com/anlowee/presto.git;
WORKDIR /home/presto
RUN git checkout xwei/benchmark-test;
WORKDIR /home/presto/presto-native-execution
RUN mkdir build;
RUN rm -rf velox;
RUN git clone https://github.com/anlowee/velox.git;
WORKDIR /home/presto/presto-native-execution/velox
RUN git checkout xwei/benchmark-test;

WORKDIR /home/presto
RUN ./mvnw clean install -DskipTests -pl -presto-docs -T1C;

WORKDIR /home/presto/presto-native-execution/build
RUN cmake .. && make -j$(nproc) presto_server;

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

RUN apt-get install -y \
    mariadb-client \
    net-tools;
