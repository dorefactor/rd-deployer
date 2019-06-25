FROM ubuntu:18.04

WORKDIR /opt/apps/rd-deployer

ENV RD_API_URL=
ENV RABBITMQ_USER=
ENV RABBITMQ_PASSWORD=

RUN apt-get update -y \
    && apt-get install -y \
        vim \
        net-tools \
        iputils-ping \
        python3 \
        python3-setuptools \
        python3-pip \
        sshpass \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3 10 \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists \
    && rm -rf /var/cache/apt/archives \
    && pip3 install \
        ansible

RUN useradd -m rd-deployer \
  && chown -R rd-deployer /opt/apps/rd-deployer

COPY --chown=rd-deployer ./deployer deployer
COPY --chown=rd-deployer ./playbooks playbooks
COPY --chown=rd-deployer ./roles roles

RUN pip3 install -r deployer/requirements.txt

USER rd-deployer

CMD ["python3", "deployer/rabbitmq_listener.py"]
