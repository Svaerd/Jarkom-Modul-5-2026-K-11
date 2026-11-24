#!/usr/bin/env python3
"""Single-source-of-truth VLSM, topology wiring, and static routing generator for K-11 Modul 5."""

from __future__ import annotations

import csv
import ipaddress
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
IMAGES = DOCS / "images"
SCRATCH_WORKBOOK = Path("/tmp/vlsm-workbook.json")

PARENT_CIDR = "10.69.0.0/21"
DEBINET_IMG = "ardhptr21/debinet:latest"
ALPINET_IMG = "ardhptr21/alpinet:latest"

# (id, switch, router, branch, prefix_len, [(host_name, vlsm_count, category, image, ports), ...])
LANS = [
    ("L1", "Switch-Quarters", "Rei", "Yui", 23, [("Quarters", 500, "Lainnya", ALPINET_IMG, [])]),
    ("L2", "Switch-Comm", "Hikari", "Hikari", 24, [("Comm-Net", 200, "Lainnya", ALPINET_IMG, [])]),
    ("L3", "Switch-Hangar", "Yui", "Yui", 25, [("Hangar-Crew", 100, "Lainnya", ALPINET_IMG, [])]),
    ("L4", "Switch-Bunker", "Kensuke", "Asuka", 26, [("Sachiel", 55, "Pilot", ALPINET_IMG, [])]),
    (
        "L5",
        "Switch-Medic",
        "Maya",
        "Fuyutsuki",
        27,
        [
            ("Pen-Pen", 1, "Lainnya", DEBINET_IMG, ["TCP 80"]),
            ("Medic-Bay", 25, "Lainnya", ALPINET_IMG, []),
        ],
    ),
    ("L6", "Switch-Relay", "Kaworu", "Hikari", 27, [("Relay-Node", 25, "Lainnya", ALPINET_IMG, [])]),
    ("L7", "Switch-Garden", "Shinji", "Yui", 27, [("Garden-Staff", 14, "Lainnya", ALPINET_IMG, [])]),
    ("L8", "Switch-Dock", "Mari", "Yui", 28, [("Dock-Crew", 12, "Lainnya", ALPINET_IMG, [])]),
    (
        "L9",
        "Switch-Lab",
        "Ritsuko",
        "Asuka",
        29,
        [
            ("Entry-Plug", 3, "Terduga Dummy System", ALPINET_IMG, []),
            ("Dummy-Plug", 2, "Terduga Dummy System", ALPINET_IMG, []),
        ],
    ),
    (
        "L10",
        "Switch-Terminal",
        "Fuyutsuki",
        "Fuyutsuki",
        29,
        [
            ("Magi-Casper", 1, "Perangkat MAGI", DEBINET_IMG, ["TCP 5000"]),
            ("Magi-Balthasar", 1, "Perangkat MAGI", DEBINET_IMG, ["TCP 5000", "TCP 5001"]),
            ("Magi-Melchior", 1, "Perangkat MAGI", DEBINET_IMG, ["TCP 5000"]),
        ],
    ),
    (
        "L11",
        "Switch-Cage",
        "Misato",
        "Misato",
        29,
        [
            ("Unit-01", 1, "Pilot", ALPINET_IMG, []),
            ("Unit-02", 1, "Pilot", ALPINET_IMG, []),
            ("Unit-00", 1, "Pilot", ALPINET_IMG, []),
        ],
    ),
    (
        "L12",
        "Switch-Dogma",
        "Toji",
        "Fuyutsuki",
        29,
        [
            ("Lilith", 1, "Staf Geofront", ALPINET_IMG, []),
            ("Adam", 1, "Staf Geofront", ALPINET_IMG, []),
        ],
    ),
    (
        "L13",
        "Switch-Monolith",
        "Shigeru",
        "Shigeru",
        29,
        [
            ("Zeruel", 1, "Lainnya (Zona Sensitif)", DEBINET_IMG, []),
            ("Armisael", 1, "Lainnya (Zona Sensitif)", ALPINET_IMG, []),
        ],
    ),
    ("L14", "Switch-Radar", "Makoto", "Shigeru", 29, [("Radar-Array", 4, "Lainnya (Zona Sensitif)", ALPINET_IMG, [])]),
    ("L15", "Switch-Archive", "Asuka", "Asuka", 30, [("Archive-Vault", 1, "Lainnya", ALPINET_IMG, [])]),
    ("L16", "Switch-Intel", "Kaji", "Kaji", 30, [("Spy", 1, "Terduga Dummy System", ALPINET_IMG, [])]),
    ("L17", "Switch-Cmd", "Gendo", "Gendo", 30, [("Tokyo3-Core", 1, "Lainnya", DEBINET_IMG, ["TCP 80", "TCP 8080"])]),
]

# (id, name, parent_router, child_router, gendo_branch)
# Ordered branch-aligned so sibling /30 child links sit on /29 boundaries for exact CIDR summarization.
LINKS = [
    ("K1", "Gendo-Yui", "Gendo", "Yui", "Yui"),
    ("K2", "Asuka-Kensuke", "Asuka", "Kensuke", "Asuka"),
    ("K3", "Asuka-Ritsuko", "Asuka", "Ritsuko", "Asuka"),
    ("K4", "Fuyutsuki-Maya", "Fuyutsuki", "Maya", "Fuyutsuki"),
    ("K5", "Fuyutsuki-Toji", "Fuyutsuki", "Toji", "Fuyutsuki"),
    ("K6", "Yui-Rei", "Yui", "Rei", "Yui"),
    ("K7", "Yui-Shinji", "Yui", "Shinji", "Yui"),
    ("K8", "Yui-Mari", "Yui", "Mari", "Yui"),
    ("K9", "Hikari-Kaworu", "Hikari", "Kaworu", "Hikari"),
    ("K10", "Shigeru-Makoto", "Shigeru", "Makoto", "Shigeru"),
    ("K11", "Gendo-Hikari", "Gendo", "Hikari", "Hikari"),
    ("K12", "Gendo-Asuka", "Gendo", "Asuka", "Asuka"),
    ("K13", "Gendo-Kaji", "Gendo", "Kaji", "Kaji"),
    ("K14", "Gendo-Misato", "Gendo", "Misato", "Misato"),
    ("K15", "Gendo-Shigeru", "Gendo", "Shigeru", "Shigeru"),
    ("K16", "Gendo-Fuyutsuki", "Gendo", "Fuyutsuki", "Fuyutsuki"),
]

# Explicit child router ordering per parent router -> determines eth2, eth3, ... interfaces.
ROUTER_CHILDREN = {
    "Gendo": ["Yui", "Hikari", "Asuka", "Kaji", "Misato", "Shigeru", "Fuyutsuki"],
    "Yui": ["Rei", "Shinji", "Mari"],
    "Hikari": ["Kaworu"],
    "Asuka": ["Kensuke", "Ritsuko"],
    "Shigeru": ["Makoto"],
    "Fuyutsuki": ["Maya", "Toji"],
}

CIRCLED_PATH_IDS = {"L9", "K3", "K12", "K15", "L13"}


def allocate_vlsm():
    """Allocate all 17 LANs + 16 links sequentially from 10.69.0.0/21 and validate invariants."""
    parent = ipaddress.IPv4Network(PARENT_CIDR)
    cursor = int(parent.network_address)
    subnets = []
    hosts = []
    seen_ips = set()

    for sid, switch, router, branch, pfx, host_defs in LANS:
        need = sum(cnt for _, cnt, _, _, _ in host_defs) + 1
        size = 1 << (32 - pfx)
        usable = size - 2
        assert cursor % size == 0, f"Alignment error on {sid}"
        assert need <= usable and need > (size // 2) - 2, f"Non-minimal prefix /{pfx} for {sid} (need={need})"

        net = ipaddress.IPv4Network((cursor, pfx))
        gw = net.network_address + 1
        bcast = net.broadcast_address
        assert str(gw) not in seen_ips
        seen_ips.add(str(gw))

        host_names = []
        for idx, (hname, vcnt, cat, img, ports) in enumerate(host_defs, start=2):
            hip = net.network_address + idx
            assert hip < bcast
            assert str(hip) not in seen_ips
            seen_ips.add(str(hip))
            host_names.append(f"{hname}={vcnt}")
            hosts.append({
                "host": hname,
                "subnet_id": sid,
                "switch": switch,
                "router": router,
                "vlsm_hosts": vcnt,
                "ip": str(hip),
                "prefix": pfx,
                "cidr": f"{hip}/{pfx}",
                "gateway": str(gw),
                "image": img,
                "category": cat,
                "ports": ", ".join(ports) if ports else "-",
            })

        subnets.append({
            "id": sid,
            "kind": "LAN",
            "name": switch,
            "detail": f"{router} > {switch} > {', '.join(host_names)}",
            "router": router,
            "parent_router": "",
            "branch": branch,
            "network": str(net.network_address),
            "prefix": pfx,
            "cidr": str(net),
            "netmask": str(net.netmask),
            "gateway": str(gw),
            "broadcast": str(bcast),
            "usable_range": f"{net.network_address + 1} - {bcast - 1}",
            "usable_count": usable,
            "used": need,
            "remaining": usable - need,
            "block_size": size,
            "net_obj": net,
        })
        cursor += size

    for sid, lname, r_parent, r_child, branch in LINKS:
        size = 4
        pfx = 30
        assert cursor % size == 0, f"Alignment error on {sid}"
        net = ipaddress.IPv4Network((cursor, pfx))
        ip_p = net.network_address + 1
        ip_c = net.network_address + 2
        bcast = net.broadcast_address
        for ip in (ip_p, ip_c):
            assert str(ip) not in seen_ips
            seen_ips.add(str(ip))

        subnets.append({
            "id": sid,
            "kind": "Link",
            "name": lname,
            "detail": f"{r_parent} <-> {r_child}",
            "router": r_child,
            "parent_router": r_parent,
            "branch": branch,
            "network": str(net.network_address),
            "prefix": pfx,
            "cidr": str(net),
            "netmask": str(net.netmask),
            "gateway": str(ip_p),
            "broadcast": str(bcast),
            "usable_range": f"{ip_p} - {ip_c}",
            "usable_count": 2,
            "used": 2,
            "remaining": 0,
            "block_size": size,
            "net_obj": net,
        })
        cursor += size

    allocated_addrs = cursor - int(parent.network_address)
    assert allocated_addrs == 1196, f"Expected 1196 allocated, got {allocated_addrs}"
    assert len(subnets) == 33
    assert len(hosts) == 25

    free_blocks = [parent]
    for sub in subnets:
        nxt = []
        for blk in free_blocks:
            if blk.overlaps(sub["net_obj"]):
                nxt.extend(blk.address_exclude(sub["net_obj"]))
            else:
                nxt.append(blk)
        free_blocks = nxt
    free_blocks.sort()
    free_addrs = sum(b.num_addresses for b in free_blocks)
    assert free_addrs == 852 and allocated_addrs + free_addrs == parent.num_addresses
    return parent, subnets, hosts, free_blocks


def build_wiring_and_routes(subnets, hosts):
    """Assign deterministic router ethX interfaces, 59 GNS3 cables, and minimal static routes."""
    lan_by_router = {s["router"]: s for s in subnets if s["kind"] == "LAN"}
    link_by_pair = {(s["parent_router"], s["router"]): s for s in subnets if s["kind"] == "Link"}
    routers_all = ["Gendo"] + [r for kids in ROUTER_CHILDREN.values() for r in kids]
    assert len(routers_all) == 17

    parent_of = {}
    for p, kids in ROUTER_CHILDREN.items():
        for k in kids:
            parent_of[k] = p

    router_ifaces = defaultdict(list)
    cables = []

    # 1. Gendo eth0 <-> NAT1
    router_ifaces["Gendo"].append({
        "iface": "eth0",
        "peer": "NAT1",
        "ip": "DHCP",
        "prefix": "-",
        "cidr": "DHCP (NAT1)",
        "subnet_id": "NAT1",
    })
    cables.append({
        "link_no": 1,
        "type": "NAT",
        "subnet_id": "NAT1",
        "a_node": "NAT1",
        "a_iface": "nat0",
        "a_ip": "DHCP-GW",
        "b_node": "Gendo",
        "b_iface": "eth0",
        "b_ip": "DHCP",
    })

    # 2. All 16 router-to-router links
    for p_router, kids in ROUTER_CHILDREN.items():
        for idx, c_router in enumerate(kids, start=2):
            sub = link_by_pair[(p_router, c_router)]
            p_ip = str(sub["net_obj"].network_address + 1)
            c_ip = str(sub["net_obj"].network_address + 2)
            p_iface = f"eth{idx}"
            c_iface = "eth0"
            router_ifaces[p_router].append({
                "iface": p_iface,
                "peer": c_router,
                "ip": p_ip,
                "prefix": 30,
                "cidr": f"{p_ip}/30",
                "subnet_id": sub["id"],
            })
            router_ifaces[c_router].append({
                "iface": c_iface,
                "peer": p_router,
                "ip": c_ip,
                "prefix": 30,
                "cidr": f"{c_ip}/30",
                "subnet_id": sub["id"],
            })
            cables.append({
                "link_no": len(cables) + 1,
                "type": "Router-Router",
                "subnet_id": sub["id"],
                "a_node": p_router,
                "a_iface": p_iface,
                "a_ip": f"{p_ip}/30",
                "b_node": c_router,
                "b_iface": c_iface,
                "b_ip": f"{c_ip}/30",
            })

    # 3. All 17 router-to-switch LAN links (always eth1 on router)
    for r in routers_all:
        sub = lan_by_router[r]
        gw = sub["gateway"]
        pfx = sub["prefix"]
        router_ifaces[r].append({
            "iface": "eth1",
            "peer": sub["name"],
            "ip": gw,
            "prefix": pfx,
            "cidr": f"{gw}/{pfx}",
            "subnet_id": sub["id"],
        })
        cables.append({
            "link_no": len(cables) + 1,
            "type": "Router-Switch",
            "subnet_id": sub["id"],
            "a_node": r,
            "a_iface": "eth1",
            "a_ip": f"{gw}/{pfx}",
            "b_node": sub["name"],
            "b_iface": "port0",
            "b_ip": "-",
        })

    # 4. All 25 switch-to-host links (always eth0 on host)
    switch_port_counter = defaultdict(int)
    for h in hosts:
        switch_port_counter[h["switch"]] += 1
        sw_port = f"port{switch_port_counter[h['switch']]}"
        cables.append({
            "link_no": len(cables) + 1,
            "type": "Switch-Host",
            "subnet_id": h["subnet_id"],
            "a_node": h["switch"],
            "a_iface": sw_port,
            "a_ip": "-",
            "b_node": h["host"],
            "b_iface": "eth0",
            "b_ip": h["cidr"],
        })

    assert len(cables) == 59, f"Expected 59 cables, got {len(cables)}"

    for r in router_ifaces:
        router_ifaces[r].sort(key=lambda item: int(item["iface"].replace("eth", "")))

    # Build minimal static routes with exact CIDR summarization
    routes = defaultdict(list)

    def subtree_routers(node):
        res = []
        for ch in ROUTER_CHILDREN.get(node, []):
            res.append(ch)
            res.extend(subtree_routers(ch))
        return res

    # Gendo default via NAT1 + summarized branch routes
    routes["Gendo"].append(("default", "DHCP gateway (NAT1)", "eth0", "Default route ke internet"))
    gendo_branch_count = 0
    for idx, child in enumerate(ROUTER_CHILDREN["Gendo"], start=2):
        link_sub = link_by_pair[("Gendo", child)]
        nh = str(link_sub["net_obj"].network_address + 2)
        nets = [lan_by_router[child]["net_obj"]]
        for desc in subtree_routers(child):
            nets.append(lan_by_router[desc]["net_obj"])
            nets.append(link_by_pair[(parent_of[desc], desc)]["net_obj"])
        collapsed = list(ipaddress.collapse_addresses(nets))
        raw_set = set(nets)
        for net in collapsed:
            note_tag = " (ringkasan CIDR)" if net not in raw_set else ""
            routes["Gendo"].append((str(net), nh, f"eth{idx}", f"Cabang {child}{note_tag}"))
            gendo_branch_count += 1
    assert gendo_branch_count == 21, f"Expected 21 branch routes on Gendo, got {gendo_branch_count}"

    # Intermediate & leaf routers
    for r in routers_all:
        if r == "Gendo":
            continue
        p = parent_of[r]
        up_link = link_by_pair[(p, r)]
        up_nh = str(up_link["net_obj"].network_address + 1)
        routes[r].append(("default", up_nh, "eth0", f"Upstream ke {p}"))
        for idx, child in enumerate(ROUTER_CHILDREN.get(r, []), start=2):
            c_link = link_by_pair[(r, child)]
            c_nh = str(c_link["net_obj"].network_address + 2)
            nets = [lan_by_router[child]["net_obj"]]
            for desc in subtree_routers(child):
                nets.append(lan_by_router[desc]["net_obj"])
                nets.append(link_by_pair[(parent_of[desc], desc)]["net_obj"])
            for net in ipaddress.collapse_addresses(nets):
                routes[r].append((str(net), c_nh, f"eth{idx}", f"Ke LAN {child}"))

    total_routes = sum(len(v) for v in routes.values())
    assert total_routes == 47, f"Expected 47 total routes (incl Gendo default), got {total_routes}"
    return router_ifaces, cables, routes


def write_csv_files(subnets, hosts, cables):
    with (DOCS / "addresses.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "kind", "name", "router", "branch", "network", "prefix", "cidr", "netmask", "gateway", "broadcast", "usable_range", "usable_count", "used", "remaining", "circled_path"])
        for s in subnets:
            w.writerow([
                s["id"], s["kind"], s["name"], s["router"], s["branch"],
                s["network"], f"/{s['prefix']}", s["cidr"], s["netmask"],
                s["gateway"], s["broadcast"], s["usable_range"], s["usable_count"],
                s["used"], s["remaining"], "YES" if s["id"] in CIRCLED_PATH_IDS else "NO",
            ])

    with (DOCS / "hosts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["host", "subnet_id", "switch", "router", "vlsm_hosts", "ip", "prefix", "cidr", "gateway", "image", "category", "ports"])
        for h in hosts:
            w.writerow([h[k] for k in ["host", "subnet_id", "switch", "router", "vlsm_hosts", "ip", "prefix", "cidr", "gateway", "image", "category", "ports"]])

    with (DOCS / "cables.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["link_no", "type", "subnet_id", "a_node", "a_iface", "a_ip", "b_node", "b_iface", "b_ip"])
        for c in cables:
            w.writerow([c[k] for k in ["link_no", "type", "subnet_id", "a_node", "a_iface", "a_ip", "b_node", "b_iface", "b_ip"]])


def write_dot_tree(parent, subnets, free_blocks):
    """Build exact binary prefix split tree in Graphviz DOT, circling Dummy-Plug -> Armisael path."""
    leaf_map = {}
    for s in subnets:
        leaf_map[s["net_obj"]] = ("SUBNET", s)
    for b in free_blocks:
        leaf_map[b] = ("FREE", b)

    lines = [
        "digraph VLSM {",
        'graph [rankdir=LR, ordering=out, bgcolor="white", pad=0.35, nodesep=0.14, ranksep=0.55,',
        '       fontname="DejaVu Sans", fontsize=16, labelloc=t,',
        '       label="K-11 | Pohon Pembagian IP VLSM | 10.69.0.0/21\\n'
        '33 subnet (17 LAN + 16 link): 1.196 alamat terpakai | 5 blok bebas: 852 alamat\\n'
        'Merah (oval tebal) = jalur Dummy-Plug ke Armisael (L9 -> K3 -> K12 -> K15 -> L13)"];',
        'node [shape=box, fontname="DejaVu Sans", fontsize=10, margin="0.10,0.06", color="#48534f", fontcolor="#18241e"];',
        'edge [arrowhead=none, color="#67736c", penwidth=1.2];',
    ]

    def walk(net):
        nid = str(net)
        if net in leaf_map:
            kind, payload = leaf_map[net]
            if kind == "FREE":
                lines.append(
                    f'"{nid}" [label="BEBAS | {nid}\\n{payload.num_addresses} alamat", '
                    f'style="filled,dashed", fillcolor="#f2f3f4", color="#8c9690"];'
                )
            elif payload["id"] in CIRCLED_PATH_IDS:
                tag = "LAN" if payload["kind"] == "LAN" else "LINK"
                lines.append(
                    f'"{nid}" [label="{payload["id"]} ({tag}) | {payload["name"]}\\n'
                    f'{nid} | {payload["used"]}/{payload["usable_count"]} usable", '
                    f'shape=oval, style="filled,bold", fillcolor="#fde8e8", color="#c62828", '
                    f'fontcolor="#7f1d1d", penwidth=3.2, margin="0.16,0.10"];'
                )
            elif payload["kind"] == "LAN":
                lines.append(
                    f'"{nid}" [label="{payload["id"]} | {payload["name"]}\\n'
                    f'{nid} | {payload["used"]}/{payload["usable_count"]} usable", '
                    f'style=filled, fillcolor="#e2f2e9", color="#21623d"];'
                )
            else:
                lines.append(
                    f'"{nid}" [label="{payload["id"]} | {payload["name"]}\\n'
                    f'{nid} | 2/2 usable", '
                    f'style=filled, fillcolor="#e3eefc", color="#1d4ed8"];'
                )
            return

        lines.append(f'"{nid}" [label="{nid}", style=filled, fillcolor="#fafafa"];')
        left, right = list(net.subnets(prefixlen_diff=1))
        for child in (left, right):
            lines.append(f'"{nid}" -> "{child}";')
            walk(child)

    walk(parent)

    lines.extend([
        "subgraph cluster_legend {",
        '  label="Keterangan"; fontname="DejaVu Sans"; fontsize=11; color="#cbd5e1"; style=rounded;',
        '  leg_lan [label="LAN (17)", style=filled, fillcolor="#e2f2e9", color="#21623d"];',
        '  leg_lnk [label="Link Router (/30, 16)", style=filled, fillcolor="#e3eefc", color="#1d4ed8"];',
        '  leg_path [label="Jalur Dummy-Plug -> Armisael", shape=oval, style="filled,bold", fillcolor="#fde8e8", color="#c62828", penwidth=3.2];',
        '  leg_free [label="Blok Bebas (852 alamat)", style="filled,dashed", fillcolor="#f2f3f4", color="#8c9690"];',
        '  leg_lan -> leg_lnk -> leg_path -> leg_free [style=invis];',
        "}",
        "}",
    ])
    (IMAGES / "vlsm-tree.dot").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_markdown_docs(subnets, hosts, router_ifaces, routes, free_blocks):
    # docs/alamat.md
    alamat = [
        "# Peta Alamat IP K-11 (`10.69.0.0/21`)",
        "",
        "## Tabel VLSM Lengkap (17 LAN + 16 Link)",
        "",
        "| ID | Jenis | Segmen | Network | Prefix | Gateway | Broadcast | Usable Range | IP Terpakai | Sisa |",
        "|---|---|---|---|---|---|---|---:|---:|---:|",
    ]
    for s in subnets:
        mark = " **[Jalur Dummy-Plug -> Armisael]**" if s["id"] in CIRCLED_PATH_IDS else ""
        alamat.append(
            f"| `{s['id']}` | {s['kind']} | {s['name']}{mark} | `{s['network']}` | `/{s['prefix']}` | `{s['gateway']}` | `{s['broadcast']}` | `{s['usable_range']}` | {s['used']} | {s['remaining']} |"
        )
    alamat.extend([
        "",
        "**Blok bebas (852 alamat):** " + ", ".join(f"`{b}` ({b.num_addresses})" for b in free_blocks) + ".",
        "",
        "## Alamat IP 25 Host Container",
        "",
        "> Catatan `Switch-Medic`: urutan IP mengikuti penomoran eksplisit Tabel Host (`1. Pen-Pen`, `2. Medic-Bay`), yang pada `topo_5.png` menempatkan `Medic-Bay` sedikit lebih kiri secara koordinat gambar.",
        "",
        "| Host | Subnet | Switch | Router | IP/Prefix | Gateway | Image | Kategori | Port Layanan |",
        "|---|---|---|---|---|---|---|---|---|",
    ])
    for h in hosts:
        alamat.append(
            f"| `{h['host']}` | `{h['subnet_id']}` | {h['switch']} | {h['router']} | `{h['cidr']}` | `{h['gateway']}` | `{h['image']}` | {h['category']} | {h['ports']} |"
        )

    alamat.extend([
        "",
        "## Pemetaan Interface 17 Router",
        "",
        "| Router | Interface | Lawan | IP/Prefix | Subnet |",
        "|---|---|---|---|---|",
    ])
    for r, ifaces in router_ifaces.items():
        for idx, it in enumerate(ifaces):
            r_col = f"`{r}`" if idx == 0 else ""
            alamat.append(f"| {r_col} | `{it['iface']}` | {it['peer']} | `{it['cidr']}` | `{it['subnet_id']}` |")

    (DOCS / "alamat.md").write_text("\n".join(alamat) + "\n", encoding="utf-8")

    # docs/routing.md
    routing = [
        "# Tabel Routing Statis dan Ringkasan CIDR K-11",
        "",
        "- `Gendo` memakai `default` via DHCP gateway dari `NAT1` (`eth0`) dan **21 rute cabang** (hasil ringkasan CIDR dari 25 subnet di bawahnya).",
        "- Router di bawah `Gendo` memakai **1 default route** ke router induk (`eth0`) plus rute spesifik hanya untuk LAN di bawah cabangnya.",
        "- Total: **46 rute statis internal** + **1 default route `NAT1`** = **47 entri rute**.",
        "",
        "## Bukti Ringkasan CIDR Eksak di `Gendo`",
        "",
        "| Cabang | Subnet Anggota | Hasil Ringkasan CIDR | Penghematan |",
        "|---|---|---|---:|",
        "| `Shigeru` | `L13` (`10.69.4.80/29`) + `L14` (`10.69.4.88/29`) | `10.69.4.80/28` | 2 -> 1 |",
        "| `Asuka` | `K2` (`10.69.4.112/30`) + `K3` (`10.69.4.116/30`) | `10.69.4.112/29` | 2 -> 1 |",
        "| `Fuyutsuki` | `K4` (`10.69.4.120/30`) + `K5` (`10.69.4.124/30`) | `10.69.4.120/29` | 2 -> 1 |",
        "| `Yui` | `K6` (`10.69.4.128/30`) + `K7` (`10.69.4.132/30`) | `10.69.4.128/29` | 2 -> 1 |",
        "",
        "## Rute Statis per Router",
        "",
        "| Router | Tujuan CIDR | Next Hop | Interface | Keterangan |",
        "|---|---|---|---|---|",
    ]
    for r, rlist in routes.items():
        for idx, (dst, nh, iface, note) in enumerate(rlist):
            r_col = f"`{r}`" if idx == 0 else ""
            routing.append(f"| {r_col} | `{dst}` | `{nh}` | `{iface}` | {note} |")

    (DOCS / "routing.md").write_text("\n".join(routing) + "\n", encoding="utf-8")


def write_workbook_json(subnets, hosts, router_ifaces, routes, free_blocks):
    rute_rows = [["ID Subnet", "Jenis", "Rute / Segmen", "Jumlah IP", "Prefix", "Netmask"]]
    for s in subnets:
        rute_rows.append([s["id"], s["kind"], s["detail"], s["used"], f"/{s['prefix']}", s["netmask"]])
    total_usable = sum(s["usable_count"] for s in subnets)
    total_used = sum(s["used"] for s in subnets)
    total_rem = sum(s["remaining"] for s in subnets)
    total_blk = sum(s["block_size"] for s in subnets)
    rute_rows.append(["Total Kebutuhan IP", "-", "17 LAN + 16 Link (total blok 1.196 dari 2.048)", total_used, "/21", "255.255.248.0"])

    vlsm_rows = [[
        "ID", "Jenis", "Segmen", "Network", "Prefix", "Netmask", "Gateway",
        "Broadcast", "Range Usable", "Kapasitas Usable", "IP Terpakai", "Sisa", "Ukuran Blok", "Jalur Dummy-Plug -> Armisael"
    ]]
    for s in subnets:
        vlsm_rows.append([
            s["id"], s["kind"], s["name"], s["network"], f"/{s['prefix']}", s["netmask"],
            s["gateway"], s["broadcast"], s["usable_range"], s["usable_count"],
            s["used"], s["remaining"], s["block_size"], "YA" if s["id"] in CIRCLED_PATH_IDS else "-",
        ])
    vlsm_rows.append(["TOTAL", "-", "33 Subnet Terpakai", "10.69.0.0", "/21", "255.255.248.0", "-", "-", "-", total_usable, total_used, total_rem, total_blk, "5 Subnet Jalur"])
    for idx, blk in enumerate(free_blocks, start=1):
        vlsm_rows.append([
            f"FREE-{idx}", "Bebas", "Blok Cadangan", str(blk.network_address), f"/{blk.prefixlen}",
            str(blk.netmask), "-", str(blk.broadcast_address), "-", max(blk.num_addresses - 2, 0),
            0, blk.num_addresses, blk.num_addresses, "-",
        ])

    host_rows = [["Host", "Subnet", "Switch", "Router", "Host VLSM", "IP Address", "Prefix", "Gateway", "Docker Image", "Kategori", "Port Layanan"]]
    for h in hosts:
        host_rows.append([
            h["host"], h["subnet_id"], h["switch"], h["router"], h["vlsm_hosts"],
            h["ip"], f"/{h['prefix']}", h["gateway"], h["image"], h["category"], h["ports"],
        ])

    route_rows = [["Router", "Tujuan CIDR", "Next Hop", "Interface", "Keterangan"]]
    for r, rlist in routes.items():
        for dst, nh, iface, note in rlist:
            route_rows.append([r, dst, nh, iface, note])

    iface_rows = [["Router", "Interface", "Terhubung Ke", "IP Address", "Prefix", "ID Subnet"]]
    for r, ifaces in router_ifaces.items():
        for it in ifaces:
            iface_rows.append([r, it["iface"], it["peer"], it["ip"], f"/{it['prefix']}" if it["prefix"] != "-" else "-", it["subnet_id"]])

    payload = {
        "sheets": [
            {"name": "Rute", "rows": rute_rows},
            {"name": "Pembagian IP - VLSM", "rows": vlsm_rows},
            {"name": "Alamat Host", "rows": host_rows},
            {"name": "Interface Router", "rows": iface_rows},
            {"name": "Routing CIDR", "rows": route_rows},
        ]
    }
    SCRATCH_WORKBOOK.parent.mkdir(parents=True, exist_ok=True)
    SCRATCH_WORKBOOK.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    parent, subnets, hosts, free_blocks = allocate_vlsm()
    router_ifaces, cables, routes = build_wiring_and_routes(subnets, hosts)
    write_csv_files(subnets, hosts, cables)
    write_dot_tree(parent, subnets, free_blocks)
    write_markdown_docs(subnets, hosts, router_ifaces, routes, free_blocks)
    write_workbook_json(subnets, hosts, router_ifaces, routes, free_blocks)
    print(f"OK: {len(subnets)} subnets, {len(hosts)} hosts, {len(cables)} cables, {sum(len(v) for v in routes.values())} routes, 1196 allocated / 852 free.")


if __name__ == "__main__":
    main()
