#!/bin/bash
set -euo pipefail

# Konfigurasi idempoten router Asuka (Modul 5 K-11)
sysctl -w net.ipv4.ip_forward=1 >/dev/null

# Soal 3: Routing statis minimal (ringkasan CIDR)
ip route replace default via 10.69.4.153 dev eth0 # Upstream ke Gendo
ip route replace 10.69.3.128/26 via 10.69.4.114 dev eth2 # Ke LAN Kensuke
ip route replace 10.69.4.48/29 via 10.69.4.118 dev eth3 # Ke LAN Ritsuko
