#!/bin/bash
set -euo pipefail

# ============================================================
# Zeruel (10.69.4.82) - Modul 5 K-11
#   Soal 17 : listener TCP 9000 sebagai JEBAKAN PEMBANDING.
#             Listener ini harus TETAP KOSONG: seluruh koneksi TCP dari
#             Magi-Casper ke 10.69.4.82:9000 dibelokkan oleh Fuyutsuki
#             (DNAT) ke Pen-Pen, sehingga tidak ada paket yang sampai ke sini.
#   Soal 20 : idempoten (aman dijalankan berulang)
# ============================================================

if ! command -v nc.traditional >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq netcat-traditional
fi

stop_loop() {
  local pidfile="$1" port="$2"
  if [ -f "$pidfile" ]; then
    local oldpid; oldpid=$(cat "$pidfile" 2>/dev/null || true)
    [ -n "$oldpid" ] && kill "$oldpid" 2>/dev/null || true
  fi
  pkill -f "nc.traditional -n -k -l -p ${port}\b" 2>/dev/null || true
}

stop_loop "/run/zeruel-9000.pid" "9000"
( while true; do nc.traditional -n -k -l -p 9000 >> /var/log/zeruel-9000.log 2>&1; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/zeruel-9000.pid"

sleep 0.3
