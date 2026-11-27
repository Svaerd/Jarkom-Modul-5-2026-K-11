#!/bin/bash
set -euo pipefail

# ============================================================
# Tokyo3-Core (10.69.4.106) - Modul 5 K-11
#   Soal 8  : responder TCP 80 "Welcome to Tokyo3-Core" & TCP 8080 "syifa imutz"
#   Soal 15 : rate limit ICMP echo-request maksimal 5/detik, sisanya dibuang
#   Soal 16 : LOG prefix "SCAN-NERV:" + REJECT seketika untuk scan Dummy-Plug
#             (10.69.4.51) ke port 22, 23, 3306
#   Soal 20 : idempoten (aman dijalankan berulang)
# ============================================================

# ---------- Parameter (Soal 15 & 16) ----------
ICMP_RATE="5/sec"
ICMP_BURST="5"
SCANNER_IP="10.69.4.51"          # Dummy-Plug (Switch-Lab, di bawah Ritsuko)
SCAN_PORTS="22,23,3306"
SCAN_PREFIX="SCAN-NERV: "

if ! dpkg -s iptables netcat-traditional >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iptables netcat-traditional
fi

# ---------- Layanan Tokyo3-Core (Soal 8) ----------
stop_loop() {
  local pidfile="$1" port="$2"
  if [ -f "$pidfile" ]; then
    local oldpid; oldpid=$(cat "$pidfile" 2>/dev/null || true)
    [ -n "$oldpid" ] && kill "$oldpid" 2>/dev/null || true
  fi
  pkill -f "nc.traditional -n -l -p ${port}\b" 2>/dev/null || true
}

stop_loop "/run/tokyo3-core-80.pid" "80"
( while true; do nc.traditional -n -l -p 80 -c 'echo "Welcome to $(hostname)"'; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/tokyo3-core-80.pid"

stop_loop "/run/tokyo3-core-8080.pid" "8080"
( while true; do nc.traditional -n -l -p 8080 -c 'echo "syifa imutz"'; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/tokyo3-core-8080.pid"

sleep 0.3

# ---------- Firewall (Soal 15 + Soal 16) ----------
# place_rule: pastikan rule ADA di POSISI tertentu (hapus duplikat, lalu insert).
# Ini wajib karena urutan menentukan hasil.
place_rule() {
  local pos="$1" chain="$2"; shift 2
  while iptables -C "$chain" "$@" 2>/dev/null; do
    iptables -D "$chain" "$@" 2>/dev/null || break
  done
  iptables -I "$chain" "$pos" "$@"
}

# Log kernel sering di-rate-limit; matikan agar SETIAP percobaan tercatat.
sysctl -w kernel.printk_ratelimit=0 >/dev/null 2>&1 || true

# URUTAN FINAL chain INPUT:
#  1 lo
#  2 icmp type 8 limit ACCEPT   (Soal 15)
#  3 icmp type 8 DROP           (Soal 15)
#  4 SCAN-NERV LOG              (Soal 16)  <- harus SEBELUM reject
#  5 SCAN-NERV REJECT           (Soal 16)
#  6 conntrack ESTABLISHED,RELATED
#  7 tcp 80,8080 ACCEPT
#
# Rule ICMP (Soal 15) tetap di atas conntrack: conntrack menandai echo-request
# lanjutan sebagai ESTABLISHED sehingga rate limit tidak akan pernah dievaluasi.
# Rule SCAN-NERV juga di atas conntrack supaya setiap percobaan baru pasti
# tercatat, bukan lolos sebagai ESTABLISHED.
place_rule 1 INPUT -i lo -j ACCEPT
place_rule 2 INPUT -p icmp -m icmp --icmp-type 8 \
  -m limit --limit "$ICMP_RATE" --limit-burst "$ICMP_BURST" -j ACCEPT
place_rule 3 INPUT -p icmp -m icmp --icmp-type 8 -j DROP
place_rule 4 INPUT -s "$SCANNER_IP" -p tcp -m multiport --dports "$SCAN_PORTS" \
  -j LOG --log-prefix "$SCAN_PREFIX" --log-level 4
place_rule 5 INPUT -s "$SCANNER_IP" -p tcp -m multiport --dports "$SCAN_PORTS" \
  -j REJECT --reject-with tcp-reset
place_rule 6 INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
place_rule 7 INPUT -p tcp -m multiport --dports 80,8080 -j ACCEPT

iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
