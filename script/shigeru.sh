#!/bin/bash
set -euo pipefail

# ============================================================
# Shigeru (gateway Zona Sensitif) - Modul 5 K-11
#   Soal 3  : routing statis minimal
#   Soal 18 : gerbang zona sensitif (Monolith + Radar)
#             - node DI DALAM zona boleh memulai koneksi ke mana saja
#             - node DI LUAR zona tidak boleh memulai koneksi ke dalam
#             - pengecualian: ICMP echo-request dari subnet Terminal (L10)
#             - blokir berbasis ARAH DATANG (-i eth0), bukan daftar subnet
#   Soal 19 : isolasi total Armisael (10.69.4.83) di sisi L3
#             - semua trafik dari/ke Armisael dibuang
#             - dipasang SEBELUM conntrack agar sesi lama ikut mati
#             - LAPISAN KEDUA: isolasi utama ada di Switch-Monolith (VLAN)
#   Soal 20 : idempoten (aman dijalankan berulang)
# ============================================================

# ---------- Interface (Soal 18) ----------
# eth0 = 10.69.4.166/30  -> ke Gendo        (SISI LUAR, semua trafik non-zona)
# eth1 = 10.69.4.81/29   -> Switch-Monolith (DALAM zona: Zeruel, Armisael)
# eth2 = 10.69.4.145/30  -> ke Makoto       (DALAM zona: Switch-Radar, Radar-Array)
OUTSIDE_IF="eth0"
TERMINAL_NET="10.69.4.56/29"   # L10 Switch-Terminal: Casper .58, Balthasar .59, Melchior .60

# ---------- Armisael (Soal 19) ----------
TRAITOR_IP="10.69.4.83"

sysctl -w net.ipv4.ip_forward=1 >/dev/null

# ---------- Soal 3: Routing statis minimal ----------
ip route replace default via 10.69.4.165 dev eth0          # Upstream ke Gendo
ip route replace 10.69.4.88/29 via 10.69.4.146 dev eth2    # Ke LAN Makoto (Switch-Radar)

# ---------- Soal 18 + 19: Firewall FORWARD ----------
# place_rule: hapus duplikat lalu insert di POSISI tetap.
place_rule() {
  local pos="$1" chain="$2"; shift 2
  while iptables -C "$chain" "$@" 2>/dev/null; do
    iptables -D "$chain" "$@" 2>/dev/null || break
  done
  iptables -I "$chain" "$pos" "$@"
}

# URUTAN FINAL chain FORWARD:
#  1 -s 10.69.4.83 DROP          (Soal 19: Armisael keluar)
#  2 -d 10.69.4.83 DROP          (Soal 19: Armisael masuk)
#  3 conntrack ESTABLISHED,RELATED ACCEPT   (Soal 18: balasan zona)
#  4 -i eth1 ACCEPT              (Soal 18: zona Monolith keluar)
#  5 -i eth2 ACCEPT              (Soal 18: zona Radar keluar)
#  6 -i eth0 -s 10.69.4.56/29 icmp 8 ACCEPT (Soal 18: pengecualian Terminal)
#  7 -i eth0 DROP                (Soal 18: semua luar, otomatis)

# Soal 19 - dua rule paling atas: Armisael tidak boleh bicara dengan siapa pun.
# Diletakkan SEBELUM conntrack supaya koneksi yang sudah terbentuk pun ikut mati.
place_rule 1 FORWARD -s "$TRAITOR_IP" -j DROP
place_rule 2 FORWARD -d "$TRAITOR_IP" -j DROP

# Soal 18 - gerbang zona sensitif
place_rule 3 FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
place_rule 4 FORWARD -i eth1 -j ACCEPT
place_rule 5 FORWARD -i eth2 -j ACCEPT
place_rule 6 FORWARD -i "$OUTSIDE_IF" -s "$TERMINAL_NET" \
  -p icmp --icmp-type echo-request -j ACCEPT
place_rule 7 FORWARD -i "$OUTSIDE_IF" -j DROP

iptables -P FORWARD DROP
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
