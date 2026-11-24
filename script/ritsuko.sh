#!/bin/bash
set -euo pipefail

# Konfigurasi idempoten router Ritsuko (Modul 5 K-11)
sysctl -w net.ipv4.ip_forward=1 >/dev/null

# Soal 3: Routing statis minimal (ringkasan CIDR)
ip route replace default via 10.69.4.117 dev eth0 # Upstream ke Asuka
