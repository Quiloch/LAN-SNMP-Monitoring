FROM python:3.10 

# Zainstalowanie iputils, inaczej "ping" nie był obsługiwany przez Docker
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

# Wymagane było dodanie reguł iptables przed uruchomieniem aplikacji
# w innym wypadku generowało błędy/nie uzyskiwalo połączenia
CMD iptables -A INPUT -p udp --dport 161 -j ACCEPT && \
    iptables -A INPUT -p udp --sport 161 -j ACCEPT && \
    iptables -A INPUT -p udp --dport 5000 -j ACCEPT && \
    iptables -A INPUT -p udp --sport 5000 -j ACCEPT && \
    python app.py
