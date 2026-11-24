#!/usr/bin/env python3
"""Build the 60-node, 59-link Operation Geofront topology in local GNS3."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gns3_helper import (
    authenticate,
    ensure_project_open,
    get_nodes_map,
    load_cables_csv,
    load_hosts_csv,
    req,
)

DEBINET_IMG = "ardhptr21/debinet:latest"

NODE_COORDS = {
    "NAT1": (0, -140),
    "Gendo": (0, 0),
    "Switch-Cmd": (130, -140),
    "Tokyo3-Core": (230, -240),
    # Branch Yui
    "Yui": (-100, -130),
    "Switch-Hangar": (-250, -170),
    "Hangar-Crew": (-420, -280),
    "Mari": (-170, -280),
    "Switch-Dock": (-260, -400),
    "Dock-Crew": (-380, -520),
    "Rei": (-70, -320),
    "Switch-Quarters": (-110, -460),
    "Quarters": (-110, -610),
    "Shinji": (60, -280),
    "Switch-Garden": (80, -430),
    "Garden-Staff": (100, -570),
    # Branch Hikari
    "Hikari": (-240, -20),
    "Switch-Comm": (-420, -20),
    "Comm-Net": (-600, -50),
    "Kaworu": (-360, -130),
    "Switch-Relay": (-520, -160),
    "Relay-Node": (-680, -230),
    # Branch Asuka
    "Asuka": (-210, 120),
    "Switch-Archive": (-360, 260),
    "Archive-Vault": (-480, 390),
    "Kensuke": (-390, 90),
    "Switch-Bunker": (-560, 100),
    "Sachiel": (-730, 100),
    "Ritsuko": (-390, 200),
    "Switch-Lab": (-560, 260),
    "Entry-Plug": (-730, 220),
    "Dummy-Plug": (-680, 380),
    # Branch Kaji
    "Kaji": (-110, 180),
    "Switch-Intel": (-190, 300),
    "Spy": (-270, 420),
    # Branch Misato
    "Misato": (-10, 180),
    "Switch-Cage": (-20, 310),
    "Unit-01": (-120, 460),
    "Unit-02": (-20, 460),
    "Unit-00": (80, 460),
    # Branch Shigeru
    "Shigeru": (140, 140),
    "Makoto": (140, 270),
    "Switch-Radar": (140, 400),
    "Radar-Array": (140, 540),
    "Switch-Monolith": (310, 240),
    "Zeruel": (330, 390),
    "Armisael": (470, 360),
    # Branch Fuyutsuki
    "Fuyutsuki": (230, 20),
    "Switch-Terminal": (400, -70),
    "Magi-Casper": (440, -210),
    "Magi-Balthasar": (560, -170),
    "Magi-Melchior": (630, -70),
    "Maya": (430, 50),
    "Switch-Medic": (580, 60),
    "Pen-Pen": (730, 20),
    "Medic-Bay": (650, 190),
    "Toji": (390, 160),
    "Switch-Dogma": (510, 240),
    "Lilith": (580, 370),
    "Adam": (680, 280),
}

SERVER_ICON_HOSTS = {
    "Tokyo3-Core",
    "Magi-Casper",
    "Magi-Balthasar",
    "Magi-Melchior",
    "Pen-Pen",
    "Relay-Node",
    "Comm-Net",
    "Archive-Vault",
    "Radar-Array",
}


def parse_endpoint(node: str, iface: str) -> tuple[str, int, int]:
    if iface == "nat0":
        return node, 0, 0
    if iface.startswith("port"):
        return node, 0, int(iface.replace("port", ""))
    if iface.startswith("eth"):
        return node, int(iface.replace("eth", "")), 0
    raise ValueError(f"Unknown interface format: {node} {iface}")


def main():
    token = authenticate()
    pid = ensure_project_open(token)
    print(f"[+] Project open: {pid}")

    _, tmpls = req("GET", "/v3/templates", token=token)
    tmpl_by_type = {t["template_type"]: t["template_id"] for t in tmpls}
    nat_tmpl = tmpl_by_type["nat"]
    sw_tmpl = tmpl_by_type["ethernet_switch"]

    hosts = load_hosts_csv()
    cables = load_cables_csv()

    # Compute exact adapter count needed per router from cables.csv
    router_max_eth = defaultdict(int)
    routers = set()
    switches = set()
    for c in cables:
        for side_node, side_if in ((c["a_node"], c["a_iface"]), (c["b_node"], c["b_iface"])):
            if side_node.startswith("Switch-"):
                switches.add(side_node)
            elif side_node != "NAT1" and side_if.startswith("eth"):
                # Could be router or host; filter out hosts below
                router_max_eth[side_node] = max(router_max_eth[side_node], int(side_if.replace("eth", "")))
        if c["type"] == "Router-Switch":
            routers.add(c["a_node"])

    assert len(routers) == 17, f"Expected 17 routers, got {len(routers)}"
    assert len(switches) == 17, f"Expected 17 switches, got {len(switches)}"
    assert len(hosts) == 25, f"Expected 25 hosts, got {len(hosts)}"

    existing = get_nodes_map(token, pid)

    def create_docker_node(name: str, image: str, adapters: int, symbol: str):
        if name in existing:
            return
        x, y = NODE_COORDS[name]
        body = {
            "name": name,
            "node_type": "docker",
            "compute_id": "local",
            "x": x,
            "y": y,
            "symbol": symbol,
            "console_type": "telnet",
            "properties": {"image": image, "adapters": adapters},
        }
        st, res = req("POST", f"/v3/projects/{pid}/nodes", body, token=token)
        if st not in (200, 201):
            raise RuntimeError(f"Create docker node {name} failed ({st}): {res}")
        print(f"[+] Node {name} ({image}, eth0..eth{adapters - 1})")

    # 1. NAT1 via template (uses default nat interface virbr0)
    if "NAT1" not in existing:
        x, y = NODE_COORDS["NAT1"]
        st, res = req("POST", f"/v3/projects/{pid}/templates/{nat_tmpl}", {"name": "NAT1", "x": x, "y": y}, token=token)
        if st not in (200, 201):
            raise RuntimeError(f"Create NAT1 failed ({st}): {res}")
        if res.get("name") != "NAT1":
            req("PUT", f"/v3/projects/{pid}/nodes/{res['node_id']}", {"name": "NAT1"}, token=token)
        print("[+] Node NAT1")

    # 2. 17 Switches via template (reconcile if GNS3 auto-named Switch1..17)
    coord_to_sw = {NODE_COORDS[sw]: sw for sw in switches}
    for n in list(existing.values()):
        if n["node_type"] == "ethernet_switch" and n["name"] not in switches:
            target = coord_to_sw.get((n["x"], n["y"]))
            if target:
                st, res = req("PUT", f"/v3/projects/{pid}/nodes/{n['node_id']}", {"name": target}, token=token)
                if st not in (200, 201):
                    raise RuntimeError(f"Rename switch {n['name']} -> {target} failed ({st}): {res}")
                print(f"[~] Switch renamed {n['name']} -> {target}")
    existing = get_nodes_map(token, pid)

    for sw in sorted(switches):
        if sw not in existing:
            x, y = NODE_COORDS[sw]
            st, res = req("POST", f"/v3/projects/{pid}/templates/{sw_tmpl}", {"name": sw, "x": x, "y": y}, token=token)
            if st not in (200, 201):
                raise RuntimeError(f"Create switch {sw} failed ({st}): {res}")
            if res.get("name") != sw:
                st2, res2 = req("PUT", f"/v3/projects/{pid}/nodes/{res['node_id']}", {"name": sw}, token=token)
                if st2 not in (200, 201):
                    raise RuntimeError(f"Rename switch to {sw} failed ({st2}): {res2}")
            print(f"[+] Switch {sw}")

    # 3. 17 Routers (debinet)
    for r in sorted(routers):
        adapters = router_max_eth[r] + 1
        create_docker_node(r, DEBINET_IMG, adapters, ":/symbols/affinity/square/blue/router.svg")

    # 4. 25 End-Hosts
    for h in hosts:
        sym = ":/symbols/affinity/square/blue/server.svg" if h["host"] in SERVER_ICON_HOSTS else ":/symbols/affinity/square/blue/client_vm.svg"
        create_docker_node(h["host"], h["image"], 1, sym)

    nodes = get_nodes_map(token, pid)
    assert len(nodes) == 60, f"Expected 60 nodes, got {len(nodes)}"

    # Create 59 links idempotently
    _, cur_links = req("GET", f"/v3/projects/{pid}/links", token=token)
    have_pairs = set()
    for lnk in cur_links or []:
        n0, n1 = lnk["nodes"]
        have_pairs.add(frozenset([(n0["node_id"], n0["adapter_number"], n0["port_number"]), (n1["node_id"], n1["adapter_number"], n1["port_number"])]))

    created_links = 0
    for c in cables:
        an, aa, ap = parse_endpoint(c["a_node"], c["a_iface"])
        bn, ba, bp = parse_endpoint(c["b_node"], c["b_iface"])
        pair = frozenset([(nodes[an]["node_id"], aa, ap), (nodes[bn]["node_id"], ba, bp)])
        if pair in have_pairs:
            continue
        payload = {
            "nodes": [
                {"node_id": nodes[an]["node_id"], "adapter_number": aa, "port_number": ap},
                {"node_id": nodes[bn]["node_id"], "adapter_number": ba, "port_number": bp},
            ]
        }
        st, res = req("POST", f"/v3/projects/{pid}/links", payload, token=token)
        if st not in (200, 201):
            raise RuntimeError(f"Create link {an}:{c['a_iface']} <-> {bn}:{c['b_iface']} failed ({st}): {res}")
        created_links += 1

    _, final_links = req("GET", f"/v3/projects/{pid}/links", token=token)
    print(f"[+] Topology ready: {len(nodes)} nodes, {len(final_links)} links ({created_links} newly added).")
    assert len(final_links) == 59, f"Expected 59 links, got {len(final_links)}"


if __name__ == "__main__":
    main()
