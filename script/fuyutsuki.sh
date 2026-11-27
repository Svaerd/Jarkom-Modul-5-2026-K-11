#!/bin/bash
set -euo pipefail

# ============================================================
# Fuyutsuki (gateway Switch-Terminal) - Modul 5 K-11
#   Soal 3  : routing statis minimal
#   Soal 17 : DNAT "sihir hitam" Casper -> Zeruel(9000) dialihkan ke Pen-Pen(9000),
#             plus MASQUERADE agar balasan Pen-Pen terlihat datang dari Zeruel
#   Soal 20 : idempoten (aman dijalankan berulang)
# ============================================================

# ---------- Alamat yang terlibat (Soal 17) ----------
CASPER_IP="10.69.4.58"    # Magi-Casper (Switch-Terminal, L10)
ZERUEL_IP="10.69.4.82"    # tujuan palsu (tidak pernah menerima paket)
PENPEN_IP="10.69.3.194"   # tujuan sebenarnya
MAGIC_PORT="9000"         # port yang dialihkan (ping tidak tersentuh)

sysctl -w net.ipv4.ip_forward=1 >/dev/null

# ---------- Soal 3: Routing statis minimal ----------
ip route replace default via 10.69.4.169 dev eth0   # Upstream ke Gendo
ip route replace 10.69.3.192/27 via 10.69.4.122 dev eth2   # Ke LAN Maya
ip route replace 10.69.4.72/29 via 10.69.4.126 dev eth3    # Ke LAN Toji

# ---------- Soal 17: DNAT + MASQUERADE ----------
# place_rule: hapus duplikat lalu tambahkan (idempoten)
place_rule() {
  local table="$1" chain="$2"; shift 2
  while iptables -t "$table" -C "$chain" "$@" 2>/dev/null; do
    iptables -t "$table" -D "$chain" "$@" 2>/dev/null || break
  done
  iptables -t "$table" -A "$chain" "$@"
}

# 1) DNAT: tujuan diubah dari Zeruel:9000 -> Pen-Pen:9000
place_rule nat PREROUTING -s "$CASPER_IP" -p tcp -d "$ZERUEL_IP" --dport "$MAGIC_PORT" \
  -j DNAT --to-destination "${PENPEN_IP}:${MAGIC_PORT}"

# 2) MASQUERADE: source diubah ke IP Fuyutsuki di jalur ke Pen-Pen,
#    sehingga Pen-Pen mengira pengirimnya Fuyutsuki dan Casper melihat
#    balasan datang dari Zeruel (DNAT otomatis membalik alamat tujuan).
place_rule nat POSTROUTING -s "$CASPER_IP" -d "$PENPEN_IP" -p tcp --dport "$MAGIC_PORT" \
  -j MASQUERADE

# Jaring pengaman rute balik (opsional; normalnya rute default sudah cukup)
ip route replace "$CASPER_IP/32" via 10.69.4.170 dev eth0 2>/dev/null || true
