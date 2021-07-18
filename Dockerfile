from ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN mkdir /switchbot_client
RUN apt-get update && apt-get install -y bluez python3
RUN apt-get install -y python3-pexpect

COPY main.py /switchbot_client

CMD python3 /switchbot_client/main.py
