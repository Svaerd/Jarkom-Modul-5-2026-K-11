#!/bin/bash
set -euo pipefail

# ============================================================
# Pen-Pen (10.69.3.194) - Modul 5 K-11
#   Soal 8  : responder TCP 80 "Welcome to Pen-Pen"
#   Soal 14 : kontrol akses berbasis WAKTU (Pilot vs Staf)
#   Soal 17 : listener TCP 9000 (penampung paket hasil pengalihan di Fuyutsuki)
#   Soal 20 : idempoten (aman dijalankan berulang)
# ============================================================

# ---------- Variabel jendela waktu (Soal 14) ----------
# CATATAN: modul `-m time` di kernel memakai UTC.
#   WIB = UTC + 7  ->  jam WIB dikurangi 7 jam.
#   08.00-16.00 WIB = 01:00-09:00 UTC
#   17.00-23.00 WIB = 10:00-16:00 UTC
PILOT_START="01:00"   # 08.00 WIB
PILOT_STOP="09:00"    # 16.00 WIB
PILOT_DAYS="Mon,Tue,Wed,Thu,Fri"
STAF_START="10:00"    # 17.00 WIB
STAF_STOP="16:00"     # 23.00 WIB

# Grup pengguna
PILOT_IPS="10.69.4.66 10.69.4.67 10.69.4.68 10.69.3.130"   # Unit-01, Unit-02, Unit-00, Sachiel
STAF_IPS="10.69.4.74 10.69.4.75"                            # Lilith, Adam

if ! dpkg -s iptables netcat-traditional >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iptables netcat-traditional
fi

# ---------- Layanan Pen-Pen (Soal 8 + Soal 17) ----------
stop_loop() {
  local pidfile="$1" port="$2"
  if [ -f "$pidfile" ]; then
    local oldpid; oldpid=$(cat "$pidfile" 2>/dev/null || true)
    [ -n "$oldpid" ] && kill "$oldpid" 2>/dev/null || true
  fi
  pkill -f "nc.traditional -n -l -p ${port}\b" 2>/dev/null || true
}

# Soal 8: HTTP sederhana
stop_loop "/run/pen-pen-80.pid" "80"
( while true; do nc.traditional -n -l -p 80 -c 'echo "Welcome to $(hostname)"'; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/pen-pen-80.pid"

# Soal 17: penampung paket hasil DNAT dari Fuyutsuki
stop_loop "/run/pen-pen-9000.pid" "9000"
( while true; do nc.traditional -n -k -l -p 9000 >> /var/log/pen-pen-9000.log 2>&1; done ) </dev/null >/dev/null 2>&1 &
echo $! > "/run/pen-pen-9000.pid"

sleep 0.3

# ---------- Kontrol akses berbasis waktu (Soal 14) ----------
add_rule() {
  local chain="$1"; shift
  iptables -C "$chain" "$@" 2>/dev/null || iptables -A "$chain" "$@"
}

add_rule INPUT -i lo -j ACCEPT
add_rule INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Pilot: hanya pada hari kerja, 08.00-16.00 WIB
for ip in $PILOT_IPS; do
  add_rule INPUT -s "$ip" -p tcp --dport 80 \
    -m time --timestart "$PILOT_START" --timestop "$PILOT_STOP" --weekdays "$PILOT_DAYS" \
    -j ACCEPT
done

# Staf Geofront: setiap hari, 17.00-23.00 WIB
for ip in $STAF_IPS; do
  add_rule INPUT -s "$ip" -p tcp --dport 80 \
    -m time --timestart "$STAF_START" --timestop "$STAF_STOP" \
    -j ACCEPT
done

# Di luar jendela waktu / node lain: tolak seketika (TCP RST, bukan timeout)
add_rule INPUT -p tcp --dport 80 -j REJECT --reject-with tcp-reset

# Soal 17: jalur MASQUERADE dari Fuyutsuki masuk sebagai 10.69.4.169 -> harus diterima
add_rule INPUT -s 10.69.4.169 -p tcp --dport 9000 -j ACCEPT

# Soal 17: klien lain -> masukan yang dipertimbangkan (hapus bila ingin 9000 tertutup)
add_rule INPUT -p tcp --dport 9000 -j ACCEPT

iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
