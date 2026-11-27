#!/bin/sh
# ============================================================
# Lilith (10.69.4.74) - Modul 5 K-11  [image: alpinet]
#   Soal 19 : listener TCP 9000 sebagai tujuan uji nc dari Armisael/Zeruel.
#   Soal 20 : idempoten (aman dijalankan berulang)
# ============================================================
set -eu

PIDDIR=/run
[ -d "$PIDDIR" ] || PIDDIR=/tmp

if ! command -v nc.traditional >/dev/null 2>&1 && ! command -v nc >/dev/null 2>&1; then
  apk add --no-cache netcat-openbsd >/dev/null 2>&1 || true
fi

if command -v nc.traditional >/dev/null 2>&1; then
  NC=nc.traditional
else
  NC=nc
fi

if [ -f "$PIDDIR/lilith-9000.pid" ]; then
  kill "$(cat "$PIDDIR/lilith-9000.pid" 2>/dev/null || echo 0)" 2>/dev/null || true
fi
pkill -f " -l -p 9000" 2>/dev/null || true

( while true; do "$NC" -l -p 9000 >> /var/log/lilith-9000.log 2>&1; done ) </dev/null >/dev/null 2>&1 &
echo $! > "$PIDDIR/lilith-9000.pid"

sleep 0.3
