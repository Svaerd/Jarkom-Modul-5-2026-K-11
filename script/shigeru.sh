#!/bin/bash
set -euo pipefail

# Konfigurasi idempoten router Shigeru (Modul 5 K-11)
sysctl -w net.ipv4.ip_forward=1 >/dev/null

# Soal 3: Routing statis minimal (ringkasan CIDR)
ip route replace default via 10.69.4.165 dev eth0 # Upstream ke Gendo
ip route replace 10.69.4.88/29 via 10.69.4.146 dev eth2 # Ke LAN Makoto
