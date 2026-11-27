#!/bin/bash
# ============================================================
# /root/drill.sh - Uji kebakaran Geofront (Soal 20)
# Modul 5 K-11 | dipakai DI DALAM node (console GNS3)
#
# Pemakaian:
#   /root/drill.sh <nama> [rute_yang_dihapus ...]
#
# Contoh:
#   /root/drill.sh fuyutsuki default 10.69.3.192/27 10.69.4.72/29
#   /root/drill.sh shigeru   default 10.69.4.88/29
#   /root/drill.sh tokyo3-core
#
# Urutan kerja:
#   1) SAVE   : iptables-save -> /root/<nama>.rules  (+ snapshot rute)
#   2) FLUSH  : kosongkan filter/nat/mangle/raw, policy ACCEPT sementara
#   3) HAPUS  : rute yang disebut di argumen
#   4) RESTORE: iptables-restore  (TANPA --noflush => idempoten)
#   5) RUTE   : /root/<nama>.sh
#   6) ULANG  : langkah 4-5 dijalankan KEDUA kali
#   7) BUKTI  : bandingkan jumlah baris sebelum vs pemulihan #1 vs #2
#
# AMAN: console GNS3 bersifat out-of-band (docker exec), jadi memflush
# iptables TIDAK akan mengunci akses console Anda.
# ============================================================
set -uo pipefail

NAME="${1:?pakai: /root/drill.sh <nama> [rute ...]}"
shift || true
DEL_ROUTES=("$@")

RULES="/root/${NAME}.rules"
SNAP="/root/${NAME}.snap"

# ---------- prasyarat ----------
if ! command -v iptables-save >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iptables
fi
if [ ! -f "/root/${NAME}.sh" ]; then
  echo "FATAL: /root/${NAME}.sh tidak ada. Batal, tidak ada yang diubah."
  exit 1
fi

count_filter() { iptables -S 2>/dev/null | wc -l; }
count_nat()    { iptables -t nat -S 2>/dev/null | wc -l; }
count_route()  { ip route show | wc -l; }

echo "=== [0] KONDISI AWAL ($NAME) ==="
echo "filter=$(count_filter)  nat=$(count_nat)  route=$(count_route)"

# ---------- 1) SAVE ----------
iptables-save > "$RULES"
if [ ! -s "$RULES" ]; then
  echo "FATAL: $RULES kosong/gagal dibuat. Batal flush demi keamanan."
  exit 1
fi
iptables -S            > "${SNAP}.filter.0"
iptables -t nat -S     > "${SNAP}.nat.0"
ip route show          > "${SNAP}.route.0"
echo "=== [1] SAVED: $RULES ($(wc -l < "$RULES") baris) ==="
echo "    snapshot: ${SNAP}.filter.0 ${SNAP}.nat.0 ${SNAP}.route.0"

# ---------- 2) FLUSH semua tabel ----------
for t in filter nat mangle raw; do
  iptables -t "$t" -F 2>/dev/null || true
  iptables -t "$t" -X 2>/dev/null || true
done
for c in INPUT FORWARD OUTPUT; do iptables -P "$c" ACCEPT; done
echo "=== [2] FLUSHED: filter=$(count_filter) nat=$(count_nat) ==="

# ---------- 3) HAPUS rute yang kita tambahkan ----------
for r in "${DEL_ROUTES[@]:-}"; do
  [ -z "$r" ] && continue
  while ip route del "$r" 2>/dev/null; do :; done
  echo "    hapus rute: $r"
done
echo "=== [3] ROUTE setelah dihapus: $(count_route) ==="

# ---------- 4-5) PEMULIHAN #1 ----------
iptables-restore < "$RULES"
bash "/root/${NAME}.sh" >/dev/null 2>&1
iptables -S        > "${SNAP}.filter.1"
iptables -t nat -S > "${SNAP}.nat.1"
ip route show      > "${SNAP}.route.1"
echo "=== [4] PULIH #1: filter=$(count_filter) nat=$(count_nat) route=$(count_route) ==="

# ---------- 6) PEMULIHAN #2 (idempotensi) ----------
iptables-restore < "$RULES"
bash "/root/${NAME}.sh" >/dev/null 2>&1
iptables -S        > "${SNAP}.filter.2"
iptables -t nat -S > "${SNAP}.nat.2"
ip route show      > "${SNAP}.route.2"
echo "=== [5] PULIH #2: filter=$(count_filter) nat=$(count_nat) route=$(count_route) ==="

# ---------- 7) BUKTI ----------
echo
echo "=== [6] BUKTI IDEMPOTENSI ==="
rc=0
for pair in "filter" "nat" "route"; do
  a=$(wc -l < "${SNAP}.${pair}.1")
  b=$(wc -l < "${SNAP}.${pair}.2")
  if [ "$a" = "$b" ]; then
    echo "  [OK]   ${pair}: pulih#1=${a} pulih#2=${b}  (sama)"
  else
    echo "  [FAIL] ${pair}: pulih#1=${a} pulih#2=${b}  (BEDA!)"
    rc=1
  fi
  if diff -q "${SNAP}.${pair}.1" "${SNAP}.${pair}.2" >/dev/null 2>&1; then
    echo "         isi identik baris-per-baris"
  else
    echo "         isi BERBEDA -> lihat: diff ${SNAP}.${pair}.1 ${SNAP}.${pair}.2"
    rc=1
  fi
done

echo
echo "=== [7] BANDING AWAL vs PULIH#2 ==="
for pair in filter nat route; do
  a=$(wc -l < "${SNAP}.${pair}.0")
  b=$(wc -l < "${SNAP}.${pair}.2")
  [ "$a" = "$b" ] && echo "  [OK]   ${pair}: awal=${a} akhir=${b}" || echo "  [INFO] ${pair}: awal=${a} akhir=${b}"
done

echo
if [ "$rc" = "0" ]; then
  echo "HASIL: IDEMPOTEN — aman untuk Soal 20."
else
  echo "HASIL: ADA PERBEDAAN — periksa file snapshot di ${SNAP}.*"
fi
exit "$rc"
