#!/bin/bash
set -euo pipefail

# Konfigurasi idempoten router Fuyutsuki (Modul 5 K-11)
sysctl -w net.ipv4.ip_forward=1 >/dev/null

# Soal 3: Routing statis minimal (ringkasan CIDR)
ip route replace default via 10.69.4.169 dev eth0 # Upstream ke Gendo
ip route replace 10.69.3.192/27 via 10.69.4.122 dev eth2 # Ke LAN Maya
ip route replace 10.69.4.72/29 via 10.69.4.126 dev eth3 # Ke LAN Toji
