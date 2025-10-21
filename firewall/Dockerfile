FROM ubuntu:22.04

RUN apt update && apt install -y \
    iptables iproute2 tcpdump python3 python3-pip nano curl iputils-ping && apt clean

WORKDIR /app
COPY ./app /app
COPY ./db /db
RUN pip install rich

CMD ["bash"]
