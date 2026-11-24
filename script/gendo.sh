#!/bin/bash
set -euo pipefail

# Konfigurasi idempoten router Gendo (Modul 5 K-11)
sysctl -w net.ipv4.ip_forward=1 >/dev/null

# Soal 3: Routing statis minimal (ringkasan CIDR)
ip route replace 10.69.0.0/23 via 10.69.4.110 dev eth2 # Cabang Yui
ip route replace 10.69.3.0/25 via 10.69.4.110 dev eth2 # Cabang Yui
ip route replace 10.69.4.0/27 via 10.69.4.110 dev eth2 # Cabang Yui
ip route replace 10.69.4.32/28 via 10.69.4.110 dev eth2 # Cabang Yui
ip route replace 10.69.4.128/29 via 10.69.4.110 dev eth2 # Cabang Yui (ringkasan CIDR)
ip route replace 10.69.4.136/30 via 10.69.4.110 dev eth2 # Cabang Yui
ip route replace 10.69.2.0/24 via 10.69.4.150 dev eth3 # Cabang Hikari
ip route replace 10.69.3.224/27 via 10.69.4.150 dev eth3 # Cabang Hikari
ip route replace 10.69.4.140/30 via 10.69.4.150 dev eth3 # Cabang Hikari
ip route replace 10.69.3.128/26 via 10.69.4.154 dev eth4 # Cabang Asuka
ip route replace 10.69.4.48/29 via 10.69.4.154 dev eth4 # Cabang Asuka
ip route replace 10.69.4.96/30 via 10.69.4.154 dev eth4 # Cabang Asuka
ip route replace 10.69.4.112/29 via 10.69.4.154 dev eth4 # Cabang Asuka (ringkasan CIDR)
ip route replace 10.69.4.100/30 via 10.69.4.158 dev eth5 # Cabang Kaji
ip route replace 10.69.4.64/29 via 10.69.4.162 dev eth6 # Cabang Misato
ip route replace 10.69.4.80/28 via 10.69.4.166 dev eth7 # Cabang Shigeru (ringkasan CIDR)
ip route replace 10.69.4.144/30 via 10.69.4.166 dev eth7 # Cabang Shigeru
ip route replace 10.69.3.192/27 via 10.69.4.170 dev eth8 # Cabang Fuyutsuki
ip route replace 10.69.4.56/29 via 10.69.4.170 dev eth8 # Cabang Fuyutsuki
ip route replace 10.69.4.72/29 via 10.69.4.170 dev eth8 # Cabang Fuyutsuki
ip route replace 10.69.4.120/29 via 10.69.4.170 dev eth8 # Cabang Fuyutsuki (ringkasan CIDR)

# Soal 4: Dynamic NAT hanya untuk prefix internal keluar lewat NAT1 (eth0)
iptables -t nat -C POSTROUTING -s 10.69.0.0/21 -o eth0 -j MASQUERADE 2>/dev/null || \
  iptables -t nat -A POSTROUTING -s 10.69.0.0/21 -o eth0 -j MASQUERADE

# Soal 5: Firewall Gendo (policy INPUT & FORWARD = DROP)
add_rule() {
  local chain="$1"; shift
  iptables -C "$chain" "$@" 2>/dev/null || iptables -A "$chain" "$@"
}

add_rule INPUT -i lo -j ACCEPT
add_rule INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
add_rule INPUT -i eth0 -p udp --sport 67 --dport 68 -j ACCEPT
add_rule INPUT -s 10.69.0.0/21 ! -i eth0 -j ACCEPT

add_rule FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
add_rule FORWARD -s 10.69.0.0/21 ! -i eth0 -o eth0 -j ACCEPT
add_rule FORWARD -s 10.69.0.0/21 -d 10.69.0.0/21 ! -i eth0 ! -o eth0 -j ACCEPT

iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
