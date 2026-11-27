#!/bin/sh
# ============================================================
# Armisael (10.69.4.83) - Modul 5 K-11  [image: alpinet]
#   Soal 19 : HANYA menyalakan listener TCP 9000 untuk keperluan UJI.
#
#   PENTING: isolasi TIDAK dipasang di dalam node ini, sesuai perintah soal
#   ("isolasi tidak boleh dikerjakan di dalam Armisael, karena pengkhianat
#   tidak bisa dipercaya"). Isolasi dilakukan di luar:
#     - L2 : Switch-Monolith, port Armisael dipindah ke VLAN terpisah
#     - L3 : Shigeru, rule FORWARD -s/-d 10.69.4.83 -j DROP
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

# hentikan listener lama (idempoten)
if [ -f "$PIDDIR/armisael-9000.pid" ]; then
  kill "$(cat "$PIDDIR/armisael-9000.pid" 2>/dev/null || echo 0)" 2>/dev/null || true
fi
pkill -f " -l -p 9000" 2>/dev/null || true

( while true; do "$NC" -l -p 9000 >> /var/log/armisael-9000.log 2>&1; done ) </dev/null >/dev/null 2>&1 &
echo $! > "$PIDDIR/armisael-9000.pid"

sleep 0.3
