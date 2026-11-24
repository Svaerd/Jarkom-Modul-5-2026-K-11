#!/bin/bash
set -euo pipefail

# Konfigurasi layanan Pen-Pen (Modul 5 K-11)
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

stop_loop "/run/pen-pen-80.pid" "80"
( while true; do nc.traditional -n -l -p 80 -c 'echo "Welcome to $(hostname)"'; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/pen-pen-80.pid"
sleep 0.3
