from ubuntu:20.04

RUN mkdir /switchbot_client
RUN apt-get update && apt-get install -y bluez python3

COPY main.py /switchbot_client

CMD ["python3" "/switchbot_client/main.py"]
