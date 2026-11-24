#!/bin/bash
set -euo pipefail

# Konfigurasi layanan Magi-Casper (Modul 5 K-11)
if ! dpkg -s iptables netcat-traditional >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iptables netcat-traditional
fi

stop_loop() {
  local pidfile="$1" port="$2"
  if [ -f "$pidfile" ]; then
    local oldpid; oldpid=$(cat "$pidfile" 2>/dev/null || true)
    [ -n "$oldpid" ] && kill "$oldpid" 2>/dev/null || true
  fi
  pkill -f "nc.traditional -n -l -p ${port}\b" 2>/dev/null || true
}

stop_loop "/run/magi-casper-5000.pid" "5000"
( while true; do nc.traditional -n -l -p 5000 >> /var/log/magi-5000.log 2>&1; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/magi-casper-5000.pid"
sleep 0.3
