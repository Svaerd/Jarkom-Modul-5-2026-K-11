# HANDOFF.md — Panduan Lanjut ke Partner (Soal 13–20)

Dokumen serah-terima dari **Husam Danish (`5027251060`)** setelah menyelesaikan **Tahap 1–3 (Soal 1–12)** kepada **Hasheemi Rafsanjani (`5027251015`)** untuk melanjutkan **Babak 3 & Babak Final (Soal 13–20)**.

---

## 1. Artefak yang Diserahkan

- **Export GNS3 Project:** [K-11-MODUL-5.gns3project](K-11-MODUL-5.gns3project) (berisi seluruh `60` node, `59` kabel, `/etc/network/interfaces`, `/root/init.sh`, dan semua `/root/<nama>.sh`).
- **Cadangan script per node:** folder [script/](script/) (seluruh `17` router + `Magi-Casper`, `Magi-Balthasar`, `Magi-Melchior`, `Pen-Pen`, `Tokyo3-Core`).
- **Peta & dokumen kontrak:** [docs/alamat.md](docs/alamat.md), [docs/routing.md](docs/routing.md), [docs/hosts.csv](docs/hosts.csv), [docs/cables.csv](docs/cables.csv), [Spreadsheet_Modul_5_Komdat_Jarkom_2026_VLSM_K11.xlsx](Spreadsheet_Modul_5_Komdat_Jarkom_2026_VLSM_K11.xlsx).
- **Bukti eksekusi Babak 1 & 2:** [evidence/babak1/](evidence/babak1/) (`soal2.txt`–`soal8.txt`) dan [evidence/babak2/](evidence/babak2/) (`soal9.txt`–`soal12.txt`).

### Cara Import & Menjalankan di GNS3

1. Import [K-11-MODUL-5.gns3project](K-11-MODUL-5.gns3project) ke GNS3 server remote Group A (`10.4.89.246:3080`, user `K-11`, pass `K-11@GNS3`) atau GNS3 lokal.
2. Start node bertahap (hindari start 42 container sekaligus): `NAT1` + semua `Switch-*` → `17` router → `25` host.
3. Saat boot, setiap container otomatis mengeksekusi `/root/init.sh` (memasang `/etc/resolv.conf` `8.8.8.8` & `1.1.1.1` serta menjalankan `/root/<nama>.sh`).
4. **Peringatan GNS3 3.0.6:** Jangan gunakan endpoint `/reload` pada Docker node karena akan memutus interface `veth` uBridge. Gunakan **Stop lalu Start** bila perlu me-restart container.

---

## 2. Kondisi Terkini Jaringan (Pasca Soal 12)

- **Seluruh `17` router:** `net.ipv4.ip_forward = 1`, routing statis aktif (`4` ringkasan CIDR eksak di `Gendo`: `10.69.4.80/28`, `10.69.4.112/29`, `10.69.4.120/29`, `10.69.4.128/29`), `Shigeru` sudah bersih dari sabotase Soal 9.
- **`Gendo` ([script/gendo.sh](script/gendo.sh)):** `eth0` DHCP ke `NAT1`, `MASQUERADE` `10.69.0.0/21` keluar `eth0`, policy `INPUT` & `FORWARD` = `DROP` dengan 7 rule allow (`lo`, `ESTABLISHED,RELATED`, DHCP `67->68`, internal->Gendo, internal->internet, internal->internal), bersih dari sabotase Soal 10.
- **`Misato` ([script/misato.sh](script/misato.sh)):** tabel `nat` bersih dari rule SNAT sabotase Soal 10.
- **`Magi-Casper` (`10.69.4.58`, [script/magi-casper.sh](script/magi-casper.sh)):**
  - `iptables` & `netcat-traditional` terpasang; listener TCP `5000` aktif (`/var/log/magi-5000.log`).
  - Mode hantu + hardening aktif: `INPUT DROP`, `FORWARD DROP`, `OUTPUT ACCEPT`, izinkan `lo`, `ESTABLISHED,RELATED`, TCP `5000`, dan tolak `icmp echo-request`.
- **`Magi-Balthasar` (`10.69.4.59`):** `iptables` & `netcat-traditional` terpasang; listener TCP `5000` & `5001` aktif.
- **`Magi-Melchior` (`10.69.4.60`):** `iptables` & `netcat-traditional` terpasang; listener TCP `5000` aktif.
- **`Pen-Pen` (`10.69.3.194`):** `iptables` & `netcat-traditional` terpasang; listener TCP `80` balas `Welcome to Pen-Pen`.
- **`Tokyo3-Core` (`10.69.4.106`):** `iptables` & `netcat-traditional` terpasang; listener TCP `80` balas `Welcome to Tokyo3-Core` dan TCP `8080` balas `syifa imutz`.
- **`Zeruel` (`10.69.4.82`):** image `ardhptr21/debinet:latest`, siap untuk uji Soal 17, 18, dan 19.

---

## 3. Referensi Alamat untuk Soal 13–20

| Kategori / Peran | Node & Alamat IP | Gateway / Router |
|---|---|---|
| **Perangkat MAGI** | `Magi-Casper` (`10.69.4.58`), `Magi-Balthasar` (`10.69.4.59`), `Magi-Melchior` (`10.69.4.60`) | `Fuyutsuki` (`10.69.4.57/29`, `eth1`) |
| **Pilot** | `Unit-01` (`10.69.4.66`), `Unit-02` (`10.69.4.67`), `Unit-00` (`10.69.4.68`), `Sachiel` (`10.69.3.130`) | `Misato` (`10.69.4.65/29`), `Kensuke` (`10.69.3.129/26`) |
| **Staf Geofront** | `Lilith` (`10.69.4.74`), `Adam` (`10.69.4.75`) | `Toji` (`10.69.4.73/29`) |
| **Terduga Dummy System** | `Entry-Plug` (`10.69.4.50`), `Dummy-Plug` (`10.69.4.51`), `Spy` (`10.69.4.102`) | `Ritsuko` (`10.69.4.49/29`), `Kaji` (`10.69.4.101/30`) |
| **Layanan Soal 14–16** | `Pen-Pen` (`10.69.3.194`), `Tokyo3-Core` (`10.69.4.106`) | `Maya` (`10.69.3.193/27`), `Gendo` (`10.69.4.105/30`) |
| **Zona Sensitif** | `Zeruel` (`10.69.4.82`), `Armisael` (`10.69.4.83`), `Radar-Array` (`10.69.4.90`) | `Shigeru` (`eth1=10.69.4.81/29`), `Makoto` (`10.69.4.89/29`) |

Interface router kunci:
- **`Fuyutsuki`:** `eth0=10.69.4.170/30` (ke Gendo), `eth1=10.69.4.57/29` (Switch-Terminal), `eth2=10.69.4.121/30` (ke Maya), `eth3=10.69.4.125/30` (ke Toji).
- **`Shigeru`:** `eth0=10.69.4.166/30` (ke Gendo), `eth1=10.69.4.81/29` (Switch-Monolith), `eth2=10.69.4.145/30` (ke Makoto).

---

## 4. Catatan Teknis Soal 13–20

- **Soal 13 (`Magi-Balthasar`):** setelah izinkan `10.69.4.58` (`Casper`), `10.69.4.66`, `10.69.4.67`, `10.69.4.68`, dan `10.69.3.130` ke `--dport 5000:5001` (atau per port), tolak node lain dengan `-j REJECT --reject-with tcp-reset` agar langsung ditolak seketika (tidak timeout).
- **Soal 14 (`Pen-Pen`):** `iptables -m time` membaca **UTC** (`WIB - 7 jam`: `08.00–16.00 WIB` = `01:00–09:00 UTC`, `17.00–23.00 WIB` = `10:00–16:00 UTC`). Simpan `PILOT_START`, `PILOT_STOP`, `PILOT_DAYS`, `STAF_START`, `STAF_STOP` sebagai variabel di awal `/root/pen-pen.sh`, dan tolak pakai `-j REJECT` (`tcp-reset` / `icmp-port-unreachable`).
- **Soal 15 (`Tokyo3-Core`):** letakkan `-p icmp --icmp-type echo-request -m limit --limit 5/s ... -j ACCEPT` sebelum `-p icmp --icmp-type echo-request -j DROP` di chain `INPUT` (agar `OUTPUT` ping dari `Tokyo3-Core` tidak ikut dibatasi).
- **Soal 16 (`Tokyo3-Core`):** pasang rule `-s 10.69.4.51 -p tcp -m multiport --dports 22,23,3306 -j LOG --log-prefix "SCAN-NERV:"` lalu rule yang sama `-j REJECT --reject-with tcp-reset`.
- **Soal 17 (`Fuyutsuki`):** pasang paket `conntrack` di `Fuyutsuki` (`apt-get update && apt-get install -y conntrack`), lalu pada tabel `nat` buat `PREROUTING` `DNAT` TCP `-s 10.69.4.58 -d 10.69.4.82 -j DNAT --to-destination 10.69.3.194` **dan** `POSTROUTING` `MASQUERADE` (atau `SNAT` IP `Fuyutsuki eth2` `10.69.4.121`) khusus traffic TCP yang dialihkan itu agar balasan `Pen-Pen` pasti kembali melewati `Fuyutsuki` (sehingga conntrack mengembalikan source IP menjadi `10.69.4.82` ke `Casper`).
- **Soal 18 (`Shigeru`):** cocokkan arah datang dari `Gendo` dengan `-i eth0` pada chain `FORWARD` (bukan daftar subnet satu per satu!): izinkan `ESTABLISHED,RELATED` dan `-i eth0 -s 10.69.4.56/29 -p icmp --icmp-type echo-request -j ACCEPT`, lalu `-i eth0 -j DROP` (atau `REJECT`).
- **Soal 19 (`Armisael` `10.69.4.83`):** tidak boleh dikonfigurasi di dalam `Armisael`. Karena `Zeruel` (`10.69.4.82`) dan `Armisael` (`10.69.4.83`) berada pada `Switch-Monolith` yang sama, siapkan isolasi di sisi switch/VLAN (mis. memisahkan port `Armisael` pada `Switch-Monolith` atau ACL di luar `Armisael` bila tersedia) agar `Armisael` tidak bisa menghubungi `Zeruel` maupun `Shigeru` tanpa memblokir `Zeruel`.
- **Soal 20 (Idempotensi):** pastikan seluruh `/root/<nama>.sh` tetap idempoten (`ip route replace`, `iptables -C ... || iptables -A ...`, tanpa duplikasi jika dijalankan setelah `iptables-restore < /root/<nama>.rules` dua kali berturut-turut).
