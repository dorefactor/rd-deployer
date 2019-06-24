FROM ubuntu:18.04

USER root

RUN apt-get update -y \
    && apt-get install -y \
        vim \
        net-tools \
        iputils-ping \
        iproute2

RUN apt-get update && apt-get install -y \
      apt-transport-https \
      ca-certificates \
      software-properties-common \
      unzip \
      wget \
      curl \
      python3 \
      python3-setuptools \
      python3-pip \
      sshpass \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3 10 \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install \
      ansible

# RUN useradd -m drone \
#     && mkdir -p /home/drone/cache

# USER drone

# WORKDIR /home/drone

# VOLUME [ "/home/drone/cache" ]
