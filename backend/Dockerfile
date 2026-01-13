FROM python:3.10 

RUN apt update && apt install -y \
    iputils-ping \
    snmp \
    net-tools \
    netcat-traditional \
    iptables \
    && rm -rf /var/lib/apt/lists/*  

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Dodanie reguł iptables przed uruchomieniem aplikacji
CMD iptables -A INPUT -p udp --dport 161 -j ACCEPT && \
    iptables -A INPUT -p udp --sport 161 -j ACCEPT && \
    iptables -A INPUT -p udp --dport 5000 -j ACCEPT && \
    iptables -A INPUT -p udp --sport 5000 -j ACCEPT && \
    python app.py
