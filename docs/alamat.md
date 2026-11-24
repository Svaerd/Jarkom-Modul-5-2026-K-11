# Peta Alamat IP K-11 (`10.69.0.0/21`)

## Tabel VLSM Lengkap (17 LAN + 16 Link)

| ID | Jenis | Segmen | Network | Prefix | Gateway | Broadcast | Usable Range | IP Terpakai | Sisa |
|---|---|---|---|---|---|---|---:|---:|---:|
| `L1` | LAN | Switch-Quarters | `10.69.0.0` | `/23` | `10.69.0.1` | `10.69.1.255` | `10.69.0.1 - 10.69.1.254` | 501 | 9 |
| `L2` | LAN | Switch-Comm | `10.69.2.0` | `/24` | `10.69.2.1` | `10.69.2.255` | `10.69.2.1 - 10.69.2.254` | 201 | 53 |
| `L3` | LAN | Switch-Hangar | `10.69.3.0` | `/25` | `10.69.3.1` | `10.69.3.127` | `10.69.3.1 - 10.69.3.126` | 101 | 25 |
| `L4` | LAN | Switch-Bunker | `10.69.3.128` | `/26` | `10.69.3.129` | `10.69.3.191` | `10.69.3.129 - 10.69.3.190` | 56 | 6 |
| `L5` | LAN | Switch-Medic | `10.69.3.192` | `/27` | `10.69.3.193` | `10.69.3.223` | `10.69.3.193 - 10.69.3.222` | 27 | 3 |
| `L6` | LAN | Switch-Relay | `10.69.3.224` | `/27` | `10.69.3.225` | `10.69.3.255` | `10.69.3.225 - 10.69.3.254` | 26 | 4 |
| `L7` | LAN | Switch-Garden | `10.69.4.0` | `/27` | `10.69.4.1` | `10.69.4.31` | `10.69.4.1 - 10.69.4.30` | 15 | 15 |
| `L8` | LAN | Switch-Dock | `10.69.4.32` | `/28` | `10.69.4.33` | `10.69.4.47` | `10.69.4.33 - 10.69.4.46` | 13 | 1 |
| `L9` | LAN | Switch-Lab **[Jalur Dummy-Plug -> Armisael]** | `10.69.4.48` | `/29` | `10.69.4.49` | `10.69.4.55` | `10.69.4.49 - 10.69.4.54` | 6 | 0 |
| `L10` | LAN | Switch-Terminal | `10.69.4.56` | `/29` | `10.69.4.57` | `10.69.4.63` | `10.69.4.57 - 10.69.4.62` | 4 | 2 |
| `L11` | LAN | Switch-Cage | `10.69.4.64` | `/29` | `10.69.4.65` | `10.69.4.71` | `10.69.4.65 - 10.69.4.70` | 4 | 2 |
| `L12` | LAN | Switch-Dogma | `10.69.4.72` | `/29` | `10.69.4.73` | `10.69.4.79` | `10.69.4.73 - 10.69.4.78` | 3 | 3 |
| `L13` | LAN | Switch-Monolith **[Jalur Dummy-Plug -> Armisael]** | `10.69.4.80` | `/29` | `10.69.4.81` | `10.69.4.87` | `10.69.4.81 - 10.69.4.86` | 3 | 3 |
| `L14` | LAN | Switch-Radar | `10.69.4.88` | `/29` | `10.69.4.89` | `10.69.4.95` | `10.69.4.89 - 10.69.4.94` | 5 | 1 |
| `L15` | LAN | Switch-Archive | `10.69.4.96` | `/30` | `10.69.4.97` | `10.69.4.99` | `10.69.4.97 - 10.69.4.98` | 2 | 0 |
| `L16` | LAN | Switch-Intel | `10.69.4.100` | `/30` | `10.69.4.101` | `10.69.4.103` | `10.69.4.101 - 10.69.4.102` | 2 | 0 |
| `L17` | LAN | Switch-Cmd | `10.69.4.104` | `/30` | `10.69.4.105` | `10.69.4.107` | `10.69.4.105 - 10.69.4.106` | 2 | 0 |
| `K1` | Link | Gendo-Yui | `10.69.4.108` | `/30` | `10.69.4.109` | `10.69.4.111` | `10.69.4.109 - 10.69.4.110` | 2 | 0 |
| `K2` | Link | Asuka-Kensuke | `10.69.4.112` | `/30` | `10.69.4.113` | `10.69.4.115` | `10.69.4.113 - 10.69.4.114` | 2 | 0 |
| `K3` | Link | Asuka-Ritsuko **[Jalur Dummy-Plug -> Armisael]** | `10.69.4.116` | `/30` | `10.69.4.117` | `10.69.4.119` | `10.69.4.117 - 10.69.4.118` | 2 | 0 |
| `K4` | Link | Fuyutsuki-Maya | `10.69.4.120` | `/30` | `10.69.4.121` | `10.69.4.123` | `10.69.4.121 - 10.69.4.122` | 2 | 0 |
| `K5` | Link | Fuyutsuki-Toji | `10.69.4.124` | `/30` | `10.69.4.125` | `10.69.4.127` | `10.69.4.125 - 10.69.4.126` | 2 | 0 |
| `K6` | Link | Yui-Rei | `10.69.4.128` | `/30` | `10.69.4.129` | `10.69.4.131` | `10.69.4.129 - 10.69.4.130` | 2 | 0 |
| `K7` | Link | Yui-Shinji | `10.69.4.132` | `/30` | `10.69.4.133` | `10.69.4.135` | `10.69.4.133 - 10.69.4.134` | 2 | 0 |
| `K8` | Link | Yui-Mari | `10.69.4.136` | `/30` | `10.69.4.137` | `10.69.4.139` | `10.69.4.137 - 10.69.4.138` | 2 | 0 |
| `K9` | Link | Hikari-Kaworu | `10.69.4.140` | `/30` | `10.69.4.141` | `10.69.4.143` | `10.69.4.141 - 10.69.4.142` | 2 | 0 |
| `K10` | Link | Shigeru-Makoto | `10.69.4.144` | `/30` | `10.69.4.145` | `10.69.4.147` | `10.69.4.145 - 10.69.4.146` | 2 | 0 |
| `K11` | Link | Gendo-Hikari | `10.69.4.148` | `/30` | `10.69.4.149` | `10.69.4.151` | `10.69.4.149 - 10.69.4.150` | 2 | 0 |
| `K12` | Link | Gendo-Asuka **[Jalur Dummy-Plug -> Armisael]** | `10.69.4.152` | `/30` | `10.69.4.153` | `10.69.4.155` | `10.69.4.153 - 10.69.4.154` | 2 | 0 |
| `K13` | Link | Gendo-Kaji | `10.69.4.156` | `/30` | `10.69.4.157` | `10.69.4.159` | `10.69.4.157 - 10.69.4.158` | 2 | 0 |
| `K14` | Link | Gendo-Misato | `10.69.4.160` | `/30` | `10.69.4.161` | `10.69.4.163` | `10.69.4.161 - 10.69.4.162` | 2 | 0 |
| `K15` | Link | Gendo-Shigeru **[Jalur Dummy-Plug -> Armisael]** | `10.69.4.164` | `/30` | `10.69.4.165` | `10.69.4.167` | `10.69.4.165 - 10.69.4.166` | 2 | 0 |
| `K16` | Link | Gendo-Fuyutsuki | `10.69.4.168` | `/30` | `10.69.4.169` | `10.69.4.171` | `10.69.4.169 - 10.69.4.170` | 2 | 0 |

**Blok bebas (852 alamat):** `10.69.4.172/30` (4), `10.69.4.176/28` (16), `10.69.4.192/26` (64), `10.69.5.0/24` (256), `10.69.6.0/23` (512).

## Alamat IP 25 Host Container

> Catatan `Switch-Medic`: urutan IP mengikuti penomoran eksplisit Tabel Host (`1. Pen-Pen`, `2. Medic-Bay`), yang pada `topo_5.png` menempatkan `Medic-Bay` sedikit lebih kiri secara koordinat gambar.

| Host | Subnet | Switch | Router | IP/Prefix | Gateway | Image | Kategori | Port Layanan |
|---|---|---|---|---|---|---|---|---|
| `Quarters` | `L1` | Switch-Quarters | Rei | `10.69.0.2/23` | `10.69.0.1` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Comm-Net` | `L2` | Switch-Comm | Hikari | `10.69.2.2/24` | `10.69.2.1` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Hangar-Crew` | `L3` | Switch-Hangar | Yui | `10.69.3.2/25` | `10.69.3.1` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Sachiel` | `L4` | Switch-Bunker | Kensuke | `10.69.3.130/26` | `10.69.3.129` | `ardhptr21/alpinet:latest` | Pilot | - |
| `Pen-Pen` | `L5` | Switch-Medic | Maya | `10.69.3.194/27` | `10.69.3.193` | `ardhptr21/debinet:latest` | Lainnya | TCP 80 |
| `Medic-Bay` | `L5` | Switch-Medic | Maya | `10.69.3.195/27` | `10.69.3.193` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Relay-Node` | `L6` | Switch-Relay | Kaworu | `10.69.3.226/27` | `10.69.3.225` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Garden-Staff` | `L7` | Switch-Garden | Shinji | `10.69.4.2/27` | `10.69.4.1` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Dock-Crew` | `L8` | Switch-Dock | Mari | `10.69.4.34/28` | `10.69.4.33` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Entry-Plug` | `L9` | Switch-Lab | Ritsuko | `10.69.4.50/29` | `10.69.4.49` | `ardhptr21/alpinet:latest` | Terduga Dummy System | - |
| `Dummy-Plug` | `L9` | Switch-Lab | Ritsuko | `10.69.4.51/29` | `10.69.4.49` | `ardhptr21/alpinet:latest` | Terduga Dummy System | - |
| `Magi-Casper` | `L10` | Switch-Terminal | Fuyutsuki | `10.69.4.58/29` | `10.69.4.57` | `ardhptr21/debinet:latest` | Perangkat MAGI | TCP 5000 |
| `Magi-Balthasar` | `L10` | Switch-Terminal | Fuyutsuki | `10.69.4.59/29` | `10.69.4.57` | `ardhptr21/debinet:latest` | Perangkat MAGI | TCP 5000, TCP 5001 |
| `Magi-Melchior` | `L10` | Switch-Terminal | Fuyutsuki | `10.69.4.60/29` | `10.69.4.57` | `ardhptr21/debinet:latest` | Perangkat MAGI | TCP 5000 |
| `Unit-01` | `L11` | Switch-Cage | Misato | `10.69.4.66/29` | `10.69.4.65` | `ardhptr21/alpinet:latest` | Pilot | - |
| `Unit-02` | `L11` | Switch-Cage | Misato | `10.69.4.67/29` | `10.69.4.65` | `ardhptr21/alpinet:latest` | Pilot | - |
| `Unit-00` | `L11` | Switch-Cage | Misato | `10.69.4.68/29` | `10.69.4.65` | `ardhptr21/alpinet:latest` | Pilot | - |
| `Lilith` | `L12` | Switch-Dogma | Toji | `10.69.4.74/29` | `10.69.4.73` | `ardhptr21/alpinet:latest` | Staf Geofront | - |
| `Adam` | `L12` | Switch-Dogma | Toji | `10.69.4.75/29` | `10.69.4.73` | `ardhptr21/alpinet:latest` | Staf Geofront | - |
| `Zeruel` | `L13` | Switch-Monolith | Shigeru | `10.69.4.82/29` | `10.69.4.81` | `ardhptr21/debinet:latest` | Lainnya (Zona Sensitif) | - |
| `Armisael` | `L13` | Switch-Monolith | Shigeru | `10.69.4.83/29` | `10.69.4.81` | `ardhptr21/alpinet:latest` | Lainnya (Zona Sensitif) | - |
| `Radar-Array` | `L14` | Switch-Radar | Makoto | `10.69.4.90/29` | `10.69.4.89` | `ardhptr21/alpinet:latest` | Lainnya (Zona Sensitif) | - |
| `Archive-Vault` | `L15` | Switch-Archive | Asuka | `10.69.4.98/30` | `10.69.4.97` | `ardhptr21/alpinet:latest` | Lainnya | - |
| `Spy` | `L16` | Switch-Intel | Kaji | `10.69.4.102/30` | `10.69.4.101` | `ardhptr21/alpinet:latest` | Terduga Dummy System | - |
| `Tokyo3-Core` | `L17` | Switch-Cmd | Gendo | `10.69.4.106/30` | `10.69.4.105` | `ardhptr21/debinet:latest` | Lainnya | TCP 80, TCP 8080 |

## Pemetaan Interface 17 Router

| Router | Interface | Lawan | IP/Prefix | Subnet |
|---|---|---|---|---|
| `Gendo` | `eth0` | NAT1 | `DHCP (NAT1)` | `NAT1` |
|  | `eth1` | Switch-Cmd | `10.69.4.105/30` | `L17` |
|  | `eth2` | Yui | `10.69.4.109/30` | `K1` |
|  | `eth3` | Hikari | `10.69.4.149/30` | `K11` |
|  | `eth4` | Asuka | `10.69.4.153/30` | `K12` |
|  | `eth5` | Kaji | `10.69.4.157/30` | `K13` |
|  | `eth6` | Misato | `10.69.4.161/30` | `K14` |
|  | `eth7` | Shigeru | `10.69.4.165/30` | `K15` |
|  | `eth8` | Fuyutsuki | `10.69.4.169/30` | `K16` |
| `Yui` | `eth0` | Gendo | `10.69.4.110/30` | `K1` |
|  | `eth1` | Switch-Hangar | `10.69.3.1/25` | `L3` |
|  | `eth2` | Rei | `10.69.4.129/30` | `K6` |
|  | `eth3` | Shinji | `10.69.4.133/30` | `K7` |
|  | `eth4` | Mari | `10.69.4.137/30` | `K8` |
| `Hikari` | `eth0` | Gendo | `10.69.4.150/30` | `K11` |
|  | `eth1` | Switch-Comm | `10.69.2.1/24` | `L2` |
|  | `eth2` | Kaworu | `10.69.4.141/30` | `K9` |
| `Asuka` | `eth0` | Gendo | `10.69.4.154/30` | `K12` |
|  | `eth1` | Switch-Archive | `10.69.4.97/30` | `L15` |
|  | `eth2` | Kensuke | `10.69.4.113/30` | `K2` |
|  | `eth3` | Ritsuko | `10.69.4.117/30` | `K3` |
| `Kaji` | `eth0` | Gendo | `10.69.4.158/30` | `K13` |
|  | `eth1` | Switch-Intel | `10.69.4.101/30` | `L16` |
| `Misato` | `eth0` | Gendo | `10.69.4.162/30` | `K14` |
|  | `eth1` | Switch-Cage | `10.69.4.65/29` | `L11` |
| `Shigeru` | `eth0` | Gendo | `10.69.4.166/30` | `K15` |
|  | `eth1` | Switch-Monolith | `10.69.4.81/29` | `L13` |
|  | `eth2` | Makoto | `10.69.4.145/30` | `K10` |
| `Fuyutsuki` | `eth0` | Gendo | `10.69.4.170/30` | `K16` |
|  | `eth1` | Switch-Terminal | `10.69.4.57/29` | `L10` |
|  | `eth2` | Maya | `10.69.4.121/30` | `K4` |
|  | `eth3` | Toji | `10.69.4.125/30` | `K5` |
| `Rei` | `eth0` | Yui | `10.69.4.130/30` | `K6` |
|  | `eth1` | Switch-Quarters | `10.69.0.1/23` | `L1` |
| `Shinji` | `eth0` | Yui | `10.69.4.134/30` | `K7` |
|  | `eth1` | Switch-Garden | `10.69.4.1/27` | `L7` |
| `Mari` | `eth0` | Yui | `10.69.4.138/30` | `K8` |
|  | `eth1` | Switch-Dock | `10.69.4.33/28` | `L8` |
| `Kaworu` | `eth0` | Hikari | `10.69.4.142/30` | `K9` |
|  | `eth1` | Switch-Relay | `10.69.3.225/27` | `L6` |
| `Kensuke` | `eth0` | Asuka | `10.69.4.114/30` | `K2` |
|  | `eth1` | Switch-Bunker | `10.69.3.129/26` | `L4` |
| `Ritsuko` | `eth0` | Asuka | `10.69.4.118/30` | `K3` |
|  | `eth1` | Switch-Lab | `10.69.4.49/29` | `L9` |
| `Makoto` | `eth0` | Shigeru | `10.69.4.146/30` | `K10` |
|  | `eth1` | Switch-Radar | `10.69.4.89/29` | `L14` |
| `Maya` | `eth0` | Fuyutsuki | `10.69.4.122/30` | `K4` |
|  | `eth1` | Switch-Medic | `10.69.3.193/27` | `L5` |
| `Toji` | `eth0` | Fuyutsuki | `10.69.4.126/30` | `K5` |
|  | `eth1` | Switch-Dogma | `10.69.4.73/29` | `L12` |
