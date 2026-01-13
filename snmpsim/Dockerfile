FROM python:3.9

# Tworzymy użytkownika i grupę snmpsim oraz katalog na dane
RUN groupadd -r snmpsim && useradd -ms /bin/bash -g snmpsim snmpsim \
    && mkdir -p /usr/local/share/snmpsim/data

# Instalujemy wymagane pakiety
RUN apt update && apt install -y \
    snmp \
    net-tools \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Instalujemy SNMP Simulator
RUN pip install snmpsim

# Zmieniamy właściciela katalogu /usr/local/share/snmpsim
RUN chown -R snmpsim:snmpsim /usr/local/share/snmpsim

# Przełączamy się na użytkownika snmpsim
USER snmpsim

# Przenosimy się do katalogu danych
WORKDIR /usr/local/share/snmpsim/data

ENV SNMPSIM_COMMUNITY=public

# Uruchamiamy SNMP Simulator jako użytkownik snmpsim
CMD ["snmpsim-command-responder", "--agent-udpv4-endpoint=0.0.0.0:16100", "--data-dir=/usr/local/share/snmpsim/data", "--v2c-arch", "public@test"]
