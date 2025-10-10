# FROM spark:python3

FROM spark:4.0.0

USER root

RUN apt-get update;

RUN apt-get install net-tools netcat;

RUN pip3 install pyspark;

ENV SPARK_LOCAL_IP="127.0.0.1"
