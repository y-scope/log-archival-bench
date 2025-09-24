FROM presto/prestissimo-dependency:ubuntu-22.04-presto-0.293

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

# Install Task
RUN cd /usr/local && sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d;

RUN pip3 install pyarrow;

WORKDIR /home
RUN git clone https://github.com/y-scope/presto.git;
WORKDIR /home/presto
RUN git checkout 89ce0f3b4ec713d658f3544e75aeb92fbd3a397d;
WORKDIR /home/presto/presto-native-execution
RUN mkdir build;
RUN rm -rf velox;
RUN git clone https://github.com/y-scope/velox.git;
WORKDIR /home/presto/presto-native-execution/velox
RUN git checkout 27ee4bcaad449fd1c8b90c48787f4eaf8e92395f;

WORKDIR /home/presto
RUN ./mvnw clean install -DskipTests -pl -presto-docs -T1C;

WORKDIR /home/presto/presto-native-execution
# RUN cmake .. && make -j$(nproc) presto_server;
RUN NUM_THREADS=8 make release;

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

RUN apt-get update;

RUN apt-get install -y \
    mariadb-client \
    net-tools;
