FROM python:latest

RUN ["apt", "update"]
RUN ["apt", "install", "-y", "iproute2"]
RUN ["apt", "install", "-y", "tcpdump"]
RUN ["apt", "install", "-y", "iptables"]
RUN ["apt", "install", "-y", "vim"]
RUN ["apt", "install", "-y", "libpcap-dev"]
RUN ["pip", "install", "--pre", "scapy[basic]"]

WORKDIR /app
COPY ./load-balancer.py .

ENTRYPOINT sleep infinity