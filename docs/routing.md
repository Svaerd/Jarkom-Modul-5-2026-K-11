# Tabel Routing Statis dan Ringkasan CIDR K-11

- `Gendo` memakai `default` via DHCP gateway dari `NAT1` (`eth0`) dan **21 rute cabang** (hasil ringkasan CIDR dari 25 subnet di bawahnya).
- Router di bawah `Gendo` memakai **1 default route** ke router induk (`eth0`) plus rute spesifik hanya untuk LAN di bawah cabangnya.
- Total: **46 rute statis internal** + **1 default route `NAT1`** = **47 entri rute**.

## Bukti Ringkasan CIDR Eksak di `Gendo`

| Cabang | Subnet Anggota | Hasil Ringkasan CIDR | Penghematan |
|---|---|---|---:|
| `Shigeru` | `L13` (`10.69.4.80/29`) + `L14` (`10.69.4.88/29`) | `10.69.4.80/28` | 2 -> 1 |
| `Asuka` | `K2` (`10.69.4.112/30`) + `K3` (`10.69.4.116/30`) | `10.69.4.112/29` | 2 -> 1 |
| `Fuyutsuki` | `K4` (`10.69.4.120/30`) + `K5` (`10.69.4.124/30`) | `10.69.4.120/29` | 2 -> 1 |
| `Yui` | `K6` (`10.69.4.128/30`) + `K7` (`10.69.4.132/30`) | `10.69.4.128/29` | 2 -> 1 |

## Rute Statis per Router

| Router | Tujuan CIDR | Next Hop | Interface | Keterangan |
|---|---|---|---|---|
| `Gendo` | `default` | `DHCP gateway (NAT1)` | `eth0` | Default route ke internet |
|  | `10.69.0.0/23` | `10.69.4.110` | `eth2` | Cabang Yui |
|  | `10.69.3.0/25` | `10.69.4.110` | `eth2` | Cabang Yui |
|  | `10.69.4.0/27` | `10.69.4.110` | `eth2` | Cabang Yui |
|  | `10.69.4.32/28` | `10.69.4.110` | `eth2` | Cabang Yui |
|  | `10.69.4.128/29` | `10.69.4.110` | `eth2` | Cabang Yui (ringkasan CIDR) |
|  | `10.69.4.136/30` | `10.69.4.110` | `eth2` | Cabang Yui |
|  | `10.69.2.0/24` | `10.69.4.150` | `eth3` | Cabang Hikari |
|  | `10.69.3.224/27` | `10.69.4.150` | `eth3` | Cabang Hikari |
|  | `10.69.4.140/30` | `10.69.4.150` | `eth3` | Cabang Hikari |
|  | `10.69.3.128/26` | `10.69.4.154` | `eth4` | Cabang Asuka |
|  | `10.69.4.48/29` | `10.69.4.154` | `eth4` | Cabang Asuka |
|  | `10.69.4.96/30` | `10.69.4.154` | `eth4` | Cabang Asuka |
|  | `10.69.4.112/29` | `10.69.4.154` | `eth4` | Cabang Asuka (ringkasan CIDR) |
|  | `10.69.4.100/30` | `10.69.4.158` | `eth5` | Cabang Kaji |
|  | `10.69.4.64/29` | `10.69.4.162` | `eth6` | Cabang Misato |
|  | `10.69.4.80/28` | `10.69.4.166` | `eth7` | Cabang Shigeru (ringkasan CIDR) |
|  | `10.69.4.144/30` | `10.69.4.166` | `eth7` | Cabang Shigeru |
|  | `10.69.3.192/27` | `10.69.4.170` | `eth8` | Cabang Fuyutsuki |
|  | `10.69.4.56/29` | `10.69.4.170` | `eth8` | Cabang Fuyutsuki |
|  | `10.69.4.72/29` | `10.69.4.170` | `eth8` | Cabang Fuyutsuki |
|  | `10.69.4.120/29` | `10.69.4.170` | `eth8` | Cabang Fuyutsuki (ringkasan CIDR) |
| `Yui` | `default` | `10.69.4.109` | `eth0` | Upstream ke Gendo |
|  | `10.69.0.0/23` | `10.69.4.130` | `eth2` | Ke LAN Rei |
|  | `10.69.4.0/27` | `10.69.4.134` | `eth3` | Ke LAN Shinji |
|  | `10.69.4.32/28` | `10.69.4.138` | `eth4` | Ke LAN Mari |
| `Hikari` | `default` | `10.69.4.149` | `eth0` | Upstream ke Gendo |
|  | `10.69.3.224/27` | `10.69.4.142` | `eth2` | Ke LAN Kaworu |
| `Asuka` | `default` | `10.69.4.153` | `eth0` | Upstream ke Gendo |
|  | `10.69.3.128/26` | `10.69.4.114` | `eth2` | Ke LAN Kensuke |
|  | `10.69.4.48/29` | `10.69.4.118` | `eth3` | Ke LAN Ritsuko |
| `Kaji` | `default` | `10.69.4.157` | `eth0` | Upstream ke Gendo |
| `Misato` | `default` | `10.69.4.161` | `eth0` | Upstream ke Gendo |
| `Shigeru` | `default` | `10.69.4.165` | `eth0` | Upstream ke Gendo |
|  | `10.69.4.88/29` | `10.69.4.146` | `eth2` | Ke LAN Makoto |
| `Fuyutsuki` | `default` | `10.69.4.169` | `eth0` | Upstream ke Gendo |
|  | `10.69.3.192/27` | `10.69.4.122` | `eth2` | Ke LAN Maya |
|  | `10.69.4.72/29` | `10.69.4.126` | `eth3` | Ke LAN Toji |
| `Rei` | `default` | `10.69.4.129` | `eth0` | Upstream ke Yui |
| `Shinji` | `default` | `10.69.4.133` | `eth0` | Upstream ke Yui |
| `Mari` | `default` | `10.69.4.137` | `eth0` | Upstream ke Yui |
| `Kaworu` | `default` | `10.69.4.141` | `eth0` | Upstream ke Hikari |
| `Kensuke` | `default` | `10.69.4.113` | `eth0` | Upstream ke Asuka |
| `Ritsuko` | `default` | `10.69.4.117` | `eth0` | Upstream ke Asuka |
| `Makoto` | `default` | `10.69.4.145` | `eth0` | Upstream ke Shigeru |
| `Maya` | `default` | `10.69.4.121` | `eth0` | Upstream ke Fuyutsuki |
| `Toji` | `default` | `10.69.4.125` | `eth0` | Upstream ke Fuyutsuki |
