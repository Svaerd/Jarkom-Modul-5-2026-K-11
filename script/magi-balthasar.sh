#!/bin/bash
set -euo pipefail

# ============================================================
# Magi-Balthasar (10.69.4.59) - Modul 5 K-11
#   Soal 7  : listener TCP 5000 & 5001
#   Soal 13 : whitelist akses layanan MAGI + tolak node lain (tcp-reset)
#   Soal 20 : idempoten (aman dijalankan berulang)
# ============================================================

if ! dpkg -s iptables netcat-traditional >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iptables netcat-traditional
fi

# ---------- Layanan MAGI (Soal 7) ----------
stop_loop() {
  local pidfile="$1" port="$2"
  if [ -f "$pidfile" ]; then
    local oldpid; oldpid=$(cat "$pidfile" 2>/dev/null || true)
    [ -n "$oldpid" ] && kill "$oldpid" 2>/dev/null || true
  fi
  pkill -f "nc.traditional -n -l -p ${port}\b" 2>/dev/null || true
}

stop_loop "/run/magi-balthasar-5000.pid" "5000"
( while true; do nc.traditional -n -l -p 5000 >> /var/log/magi-5000.log 2>&1; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/magi-balthasar-5000.pid"

stop_loop "/run/magi-balthasar-5001.pid" "5001"
( while true; do nc.traditional -n -l -p 5001 >> /var/log/magi-5001.log 2>&1; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/magi-balthasar-5001.pid"

sleep 0.3

# ---------- Firewall whitelist (Soal 13) ----------
add_rule() {
  local chain="$1"; shift
  iptables -C "$chain" "$@" 2>/dev/null || iptables -A "$chain" "$@"
}

# loopback + balasan koneksi yang sudah established (agar ping keluar & apt tetap jalan)
add_rule INPUT -i lo -j ACCEPT
add_rule INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Hanya 5 node ini yang boleh menghubungi layanan MAGI (TCP 5000 & 5001):
#   Magi-Casper 10.69.4.58, Unit-01 10.69.4.66, Unit-02 10.69.4.67,
#   Unit-00 10.69.4.68, Sachiel 10.69.3.130
for src in 10.69.4.58 10.69.4.66 10.69.4.67 10.69.4.68 10.69.3.130; do
  add_rule INPUT -s "$src" -p tcp -m multiport --dports 5000,5001 -j ACCEPT
done

# Node lain ditolak SEKETIKA dengan TCP RST (bukan timeout)
add_rule INPUT -p tcp -m multiport --dports 5000,5001 -j REJECT --reject-with tcp-reset

# Default tolak semua yang tidak diizinkan
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
