# AGENTS.md

Konteks teknis pengerjaan **Praktikum Modul 5 — Operation Geofront** (Komunikasi Data & Jaringan Komputer 2026), kelompok **K-11**.

- Anggota: Hasheemi Rafsanjani (`5027251015`), Husam Danish (`5027251060`).
- Branch aktif saat ini: `husam`.

## Pembagian Tugas

- **Husam (Tahap 1–3, Soal 1–12, selesai):**
  - **Tahap 1 (Soal 1, selesai):** VLSM, spreadsheet `.xlsx`, pohon IP (`vlsm-tree.png`), pemetaan kabel/interface/routing, `README.md` Soal 1.
  - **Tahap 2 (Babak 1, Soal 2–8, selesai):** Build topologi 60 node di local GNS3 (`K-11-MODUL-5`), deploy IP/static routing/NAT/firewall Gendo (`/root/gendo.sh`), IP permanen 25 non-router, layanan `nc` MAGI + `Pen-Pen` + `Tokyo3-Core`, bukti di `evidence/babak1/`, update `README.md` + `Attachments/`.
  - **Tahap 3 (Babak 2, Soal 9–12 + Handoff, selesai):** Eksekusi & diagnosa sabotase (`break_routing.sh`, `break_nat.sh`, `break_fw.sh`) secara buta, mode hantu + hardening `Magi-Casper`, export `K-11-MODUL-5.gns3project`, bukti di `evidence/babak2/`, update `README.md` & tulis `HANDOFF.md` ke partner.
- **Partner (Soal 13–20):** Babak 3 (Mengamankan MAGI dan Zona Sensitif) dan Babak Final (Uji Kebakaran Geofront) — lihat [HANDOFF.md](HANDOFF.md).

## Lingkungan GNS3

- **Local `gns3server`:** `127.0.0.1:3080` (GNS3 `3.0.6`, auth `K-11` / `K-11@GNS3`), `NAT1` memakai interface `virbr0` (pastikan `libvirtd` / default network aktif sebelum start `gns3server` di Tahap 2).
- **Project:** `K-11-MODUL-5` (dibuat di Tahap 2), diekspor ke `.gns3project` setelah selesai Tahap 3 agar partner dapat import / upload ke remote Group A (`10.4.89.246:3080`).
- **Total Node (60):** `17` router + `17` Ethernet switch + `25` host container + `1` `NAT1` (`59` link di `docs/cables.csv`).

### Pembagian Docker Image Wajib

- `ardhptr21/debinet:latest` (**23 container**): semua **17 router** + **6 host** (`Magi-Casper`, `Magi-Balthasar`, `Magi-Melchior`, `Pen-Pen`, `Tokyo3-Core`, `Zeruel`).
- `ardhptr21/alpinet:latest` (**19 container**): seluruh 19 host end-device lainnya.

## Kontrak Alamat IP & Routing (`10.69.0.0/21`)

- Generator sumber tunggal kebenaran: `tools/generate_vlsm.py`.
- Keluaran tervalidasi: `docs/addresses.csv`, `docs/hosts.csv`, `docs/cables.csv`, `docs/alamat.md`, `docs/routing.md`, `docs/images/vlsm-tree.png`, dan `Spreadsheet_Modul_5_Komdat_Jarkom_2026_VLSM_K11.xlsx`.
- Ringkasan alokasi: `1.196` alamat dipakai untuk `17 LAN + 16 link /30` (`33` subnet), `852` alamat bebas dalam 5 blok.
- **Aturan khusus yang telah disepakati:**
  - `Switch-Garden` memakai `/27` (`14 host + 1 gateway = 15`, melebihi batas `/28` yaitu 14).
  - `Switch-Medic` memakai urutan Tabel Host (`1. Pen-Pen = 10.69.3.194`, `2. Medic-Bay = 10.69.3.195`).
  - Penamaan router pusat memakai `Gendo` (sesuai teks soal, Tabel Host, dan `gendo.sh`; `topo_5.png` dan tabel peran menulis `Gendou`).
  - Interface router: `eth0` selalu ke upstream (`NAT1` pada `Gendo`, router induk pada 16 router lain); `eth1` selalu ke LAN `Switch-*` miliknya; `eth2+` ke router anak sesuai urutan di `docs/alamat.md` dan `docs/cables.csv`.
  - Ringkasan CIDR eksak di `Gendo`: `10.69.4.80/28` (Shigeru LAN), `10.69.4.112/29` (Asuka links), `10.69.4.120/29` (Fuyutsuki links), `10.69.4.128/29` (Yui-Rei & Yui-Shinji). Total `21` rute cabang + `1` default di `Gendo`, `47` rute di seluruh jaringan.

## Konvensi Script & Aturan Sabotase

- Semua script konfigurasi node diletakkan di `/root/<nama>.sh` di dalam container **dan** dicadangkan di repo (`script/`).
- Semua script `/root/<nama>.sh` harus **idempoten** (`ip addr replace`, `ip route replace`, cek `iptables -C ... || iptables -A/I ...`, atau struktur restore yang aman dijalankan berulang) agar kompatibel dengan **Soal 20** (pemulihan 2x berturut-turut tanpa duplikasi rule/rute).
- **Aturan Sabotase (Soal 9, 10, 12):** Script asisten berikut **DILARANG dibaca/dibuka isinya** sebelum atau saat dieksekusi — unduh langsung di dalam container target dan jalankan, lalu diagnosa murni dari gejala (`ip route`, `sysctl`, `iptables`, `ping`, `nc`):
  - Soal 9 (`Shigeru`): `https://drive.google.com/file/d/1ub7LjL2BdZdVq6n_AbuqcO416Z8QJGVs/view?usp=sharing` (`break_routing.sh`)
  - Soal 10 (`Misato` & `Gendo`): `https://drive.google.com/file/d/1oX7r9BmMPumqrIb71Vbk43Y6CQEOvDRJ/view?usp=sharing` (`break_nat.sh`)
  - Soal 12 (`Magi-Casper`): `https://drive.google.com/file/d/1Yb5kX1NKafOGDTbAE7WMYHZkQgpWLTvZ/view?usp=sharing` (`break_fw.sh`)
