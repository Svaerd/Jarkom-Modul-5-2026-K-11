#!/bin/bash
set -euo pipefail

# Konfigurasi idempoten router Yui (Modul 5 K-11)
sysctl -w net.ipv4.ip_forward=1 >/dev/null

# Soal 3: Routing statis minimal (ringkasan CIDR)
ip route replace default via 10.69.4.109 dev eth0 # Upstream ke Gendo
ip route replace 10.69.0.0/23 via 10.69.4.130 dev eth2 # Ke LAN Rei
ip route replace 10.69.4.0/27 via 10.69.4.134 dev eth3 # Ke LAN Shinji
ip route replace 10.69.4.32/28 via 10.69.4.138 dev eth4 # Ke LAN Mari
