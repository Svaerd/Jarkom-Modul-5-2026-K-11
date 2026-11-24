#!/usr/bin/env python3
"""Configure and verify Babak 1 (Soal 2-8) in local GNS3 for K-11 Modul 5."""

from __future__ import annotations

import argparse
import ipaddress
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_vlsm import allocate_vlsm, build_wiring_and_routes
from gns3_helper import (
    ROOT,
    authenticate,
    docker_exec,
    get_nodes_map,
    get_project_id,
    load_cables_csv,
    req,
    restart_node,
    start_nodes_batch,
    write_container_file,
    write_node_file,
)

SCRIPT_DIR = ROOT / "script"
EVIDENCE_DIR = ROOT / "evidence" / "babak1"


def router_script_path(router: str) -> Path:
    return SCRIPT_DIR / f"{router.lower()}.sh"


def render_router_script(router: str, router_routes: list[tuple[str, str, str, str]], stage: str) -> str:
    """Build idempotent /root/<router>.sh for Soal 2-5 (Soal 20 compatible)."""
    lines = [
        "#!/bin/bash",
        "set -euo pipefail",
        "",
        f"# Konfigurasi idempoten router {router} (Modul 5 K-11)",
        "sysctl -w net.ipv4.ip_forward=1 >/dev/null",
    ]

    if stage in ("soal3", "soal4", "soal5"):
        lines.extend(["", "# Soal 3: Routing statis minimal (ringkasan CIDR)"])
        for dst, nh, iface, note in router_routes:
            if dst == "default" and router == "Gendo":
                # Gendo keeps its dynamic default route acquired from NAT1 DHCP
                continue
            lines.append(f"ip route replace {dst} via {nh} dev {iface} # {note}")

    if router == "Gendo" and stage in ("soal4", "soal5"):
        lines.extend([
            "",
            "# Soal 4: Dynamic NAT hanya untuk prefix internal keluar lewat NAT1 (eth0)",
            "iptables -t nat -C POSTROUTING -s 10.69.0.0/21 -o eth0 -j MASQUERADE 2>/dev/null || \\",
            "  iptables -t nat -A POSTROUTING -s 10.69.0.0/21 -o eth0 -j MASQUERADE",
        ])

    if router == "Gendo" and stage == "soal5":
        lines.extend([
            "",
            "# Soal 5: Firewall Gendo (policy INPUT & FORWARD = DROP)",
            "add_rule() {",
            '  local chain="$1"; shift',
            '  iptables -C "$chain" "$@" 2>/dev/null || iptables -A "$chain" "$@"',
            "}",
            "",
            "add_rule INPUT -i lo -j ACCEPT",
            "add_rule INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            "add_rule INPUT -i eth0 -p udp --sport 67 --dport 68 -j ACCEPT",
            "add_rule INPUT -s 10.69.0.0/21 ! -i eth0 -j ACCEPT",
            "",
            "add_rule FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            "add_rule FORWARD -s 10.69.0.0/21 ! -i eth0 -o eth0 -j ACCEPT",
            "add_rule FORWARD -s 10.69.0.0/21 -d 10.69.0.0/21 ! -i eth0 ! -o eth0 -j ACCEPT",
            "",
            "iptables -P INPUT DROP",
            "iptables -P FORWARD DROP",
            "iptables -P OUTPUT ACCEPT",
        ])

    return "\n".join(lines) + "\n"


def deploy_router_scripts(tok: str, pid: str, nodes: dict, routes: dict, stage: str):
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    for router in sorted(routes):
        fname = f"{router.lower()}.sh"
        content = render_router_script(router, routes[router], stage)
        router_script_path(router).write_text(content, encoding="utf-8")
        cid = nodes[router]["properties"]["container_id"]
        write_container_file(cid, f"/root/{fname}", content, executable=True)
        write_container_file(cid, "/root/init.sh", f"#!/bin/sh\nbash /root/{fname}\n", executable=True)
        rc, _, err = docker_exec(cid, f"bash /root/{fname}")
        if rc != 0:
            raise RuntimeError(f"{router} /root/{fname} failed (rc={rc}): {err}")


def save_evidence(filename: str, sections: list[str]):
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / filename
    path.write_text("\n".join(sections) + "\n", encoding="utf-8")
    print(f"[+] Saved evidence: {path}")


def run_soal2(tok: str, pid: str, routes: dict):
    nodes = get_nodes_map(tok, pid)
    routers = sorted(routes)
    to_start = [r for r in routers if nodes[r].get("status") != "started"]
    if to_start:
        start_nodes_batch(tok, pid, nodes, to_start, batch_size=8)
    nodes = get_nodes_map(tok, pid)

    # Wait briefly for interfaces to settle on freshly booted routers
    time.sleep(2.0)
    deploy_router_scripts(tok, pid, nodes, routes, "soal2")

    out_lines = ["=== SOAL 2: VERIFIKASI INTERFACE, IP FORWARDING, DAN LINK ROUTER-ROUTER ==="]
    for r in routers:
        cid = nodes[r]["properties"]["container_id"]
        rc, out, err = docker_exec(cid, "ip -br a; sysctl net.ipv4.ip_forward")
        if rc != 0 or "net.ipv4.ip_forward = 1" not in out:
            raise RuntimeError(f"Soal 2 check failed on {r}: {out} {err}")
        out_lines.append(f"\n--- {r} ---")
        out_lines.append(out.strip())

    # Ping both ends of all 16 router-to-router links
    cables = [c for c in load_cables_csv() if c["type"] == "Router-Router"]
    assert len(cables) == 16
    out_lines.append("\n--- PING DUA UJUNG 16 LINK ROUTER-ROUTER (32 ARAH) ---")
    for c in cables:
        a_node, a_ip = c["a_node"], c["a_ip"].split("/")[0]
        b_node, b_ip = c["b_node"], c["b_ip"].split("/")[0]
        for src, dst, label in ((a_node, b_ip, f"{a_node}->{b_node}({b_ip})"), (b_node, a_ip, f"{b_node}->{a_node}({a_ip})")):
            cid = nodes[src]["properties"]["container_id"]
            rc, out, err = docker_exec(cid, f"ping -c 2 -W 2 {dst}")
            if rc != 0 or "0% packet loss" not in out:
                raise RuntimeError(f"Link ping failed {label}: {out} {err}")
            rtt = [ln for ln in out.splitlines() if "rtt " in ln or "round-trip" in ln or "packet loss" in ln]
            out_lines.append(f"[OK] {c['subnet_id']} {label}: {' | '.join(rtt)}")

    save_evidence("soal2.txt", out_lines)
    print("[+] SOAL 2 PASSED: 17 routers up, ip_forward=1, all 32 link pings OK.")


def run_soal3(tok: str, pid: str, hosts: list[dict], routes: dict):
    nodes = get_nodes_map(tok, pid)
    deploy_router_scripts(tok, pid, nodes, routes, "soal3")

    # Start only the 4 test hosts and assign temporary runtime IP + default gateway
    test_names = ["Armisael", "Lilith", "Sachiel", "Comm-Net"]
    host_by_name = {h["host"]: h for h in hosts}
    start_nodes_batch(tok, pid, nodes, [n for n in test_names if nodes[n].get("status") != "started"], batch_size=4)
    nodes = get_nodes_map(tok, pid)
    time.sleep(1.0)

    for hname in test_names:
        h = host_by_name[hname]
        cid = nodes[hname]["properties"]["container_id"]
        rc, out, err = docker_exec(
            cid,
            f"ip link set eth0 up && ip addr replace {h['cidr']} dev eth0 && ip route replace default via {h['gateway']} dev eth0",
        )
        if rc != 0:
            raise RuntimeError(f"Temp IP failed on {hname}: {out} {err}")

    out_lines = ["=== SOAL 3: ROUTING STATIS, RINGKASAN CIDR, DAN PING LINTAS CABANG ==="]
    for r in ("Gendo", "Yui", "Hikari", "Asuka", "Shigeru", "Fuyutsuki", "Ritsuko"):
        cid = nodes[r]["properties"]["container_id"]
        _, out, _ = docker_exec(cid, "ip route")
        out_lines.append(f"\n--- ip route @ {r} ---")
        out_lines.append(out.strip())

    # Assert exact 21 branch routes + default on Gendo
    _, g_routes, _ = docker_exec(nodes["Gendo"]["properties"]["container_id"], "ip route | grep ' via '")
    via_lines = [ln for ln in g_routes.splitlines() if ln.strip()]
    assert len(via_lines) == 22, f"Expected 22 via routes on Gendo (1 default + 21 branches), got {len(via_lines)}:\n{g_routes}"

    arm_cid = nodes["Armisael"]["properties"]["container_id"]
    for target_name in ("Lilith", "Sachiel", "Comm-Net"):
        tip = host_by_name[target_name]["ip"]
        rc, out, err = docker_exec(arm_cid, f"ping -c 3 -W 2 {tip}")
        if rc != 0 or "0% packet loss" not in out:
            raise RuntimeError(f"Armisael -> {target_name} ({tip}) failed: {out} {err}")
        out_lines.append(f"\n--- ping Armisael -> {target_name} ({tip}) ---")
        out_lines.append(out.strip())

    save_evidence("soal3.txt", out_lines)
    print("[+] SOAL 3 PASSED: 21 branch routes + 4 CIDR summaries on Gendo, Armisael pings OK.")


def run_soal4(tok: str, pid: str, hosts: list[dict], routes: dict):
    nodes = get_nodes_map(tok, pid)
    deploy_router_scripts(tok, pid, nodes, routes, "soal4")
    host_by_name = {h["host"]: h for h in hosts}

    for hname in ("Armisael", "Lilith"):
        cid = nodes[hname]["properties"]["container_id"]
        rc, _, err = docker_exec(cid, "printf 'nameserver 8.8.8.8\\nnameserver 1.1.1.1\\n' > /etc/resolv.conf")
        if rc != 0:
            raise RuntimeError(f"Failed resolv.conf on {hname}: {err}")

    out_lines = ["=== SOAL 4: DYNAMIC NAT (MASQUERADE) DAN DNS RESOLVER ==="]
    g_cid = nodes["Gendo"]["properties"]["container_id"]
    _, nat_before, _ = docker_exec(g_cid, "iptables -t nat -L POSTROUTING -v -n")
    out_lines.append("\n--- NAT counter sebelum ping inter-LAN ---")
    out_lines.append(nat_before.strip())

    # Inter-LAN ping should NOT increment eth0 MASQUERADE counter
    arm_cid = nodes["Armisael"]["properties"]["container_id"]
    rc, inter_out, _ = docker_exec(arm_cid, f"ping -c 3 -W 2 {host_by_name['Lilith']['ip']}")
    assert rc == 0
    _, nat_mid, _ = docker_exec(g_cid, "iptables -t nat -L POSTROUTING -v -n")
    out_lines.append("\n--- NAT counter sesudah ping Armisael -> Lilith (inter-LAN) ---")
    out_lines.append(nat_mid.strip())

    for hname in ("Armisael", "Lilith"):
        cid = nodes[hname]["properties"]["container_id"]
        for dst in ("8.8.8.8", "deb.debian.org"):
            rc, out, err = docker_exec(cid, f"ping -c 3 -W 3 {dst}")
            if rc != 0 or "0% packet loss" not in out:
                raise RuntimeError(f"Soal 4 ping {hname} -> {dst} failed: {out} {err}")
            out_lines.append(f"\n--- {hname}: ping -c 3 {dst} ---")
            out_lines.append(out.strip())

    _, nat_after, _ = docker_exec(g_cid, "iptables -t nat -L POSTROUTING -v -n")
    out_lines.append("\n--- NAT counter sesudah ping internet @ Gendo ---")
    out_lines.append(nat_after.strip())
    assert "MASQUERADE" in nat_after and "10.69.0.0/21" in nat_after

    save_evidence("soal4.txt", out_lines)
    print("[+] SOAL 4 PASSED: Armisael & Lilith ping 8.8.8.8 & deb.debian.org, MASQUERADE active.")


def run_soal5(tok: str, pid: str, hosts: list[dict], routes: dict):
    nodes = get_nodes_map(tok, pid)
    deploy_router_scripts(tok, pid, nodes, routes, "soal5")
    g_cid = nodes["Gendo"]["properties"]["container_id"]

    # Idempotency check (Soal 20 readiness): execute gendo.sh a second time and compare rule counts
    _, s1, _ = docker_exec(g_cid, "iptables -S; echo ---NAT---; iptables -t nat -S")
    rc, _, err = docker_exec(g_cid, "bash /root/gendo.sh")
    assert rc == 0, f"Second run of gendo.sh failed: {err}"
    _, s2, _ = docker_exec(g_cid, "iptables -S; echo ---NAT---; iptables -t nat -S")
    assert s1 == s2, f"gendo.sh is NOT idempotent!\n---Run1---\n{s1}\n---Run2---\n{s2}"

    out_lines = ["=== SOAL 5: LOCKDOWN GENDO (POLICY DROP INPUT/FORWARD) ==="]
    out_lines.append("\n--- iptables -S @ Gendo ---")
    _, ipt_s, _ = docker_exec(g_cid, "iptables -S")
    out_lines.append(ipt_s.strip())
    assert "-P INPUT DROP" in ipt_s and "-P FORWARD DROP" in ipt_s

    out_lines.append("\n--- iptables -t nat -S @ Gendo ---")
    _, nat_s, _ = docker_exec(g_cid, "iptables -t nat -S")
    out_lines.append(nat_s.strip())

    host_by_name = {h["host"]: h for h in hosts}
    arm_cid = nodes["Armisael"]["properties"]["container_id"]
    for label, target in (
        ("internet 8.8.8.8", "8.8.8.8"),
        ("antar-LAN Lilith", host_by_name["Lilith"]["ip"]),
        ("internal->Gendo eth7", "10.69.4.165"),
    ):
        rc, out, err = docker_exec(arm_cid, f"ping -c 3 -W 2 {target}")
        if rc != 0 or "0% packet loss" not in out:
            raise RuntimeError(f"Soal 5 Armisael -> {label} ({target}) failed: {out} {err}")
        out_lines.append(f"\n--- Armisael -> {label} ({target}) ---")
        out_lines.append(out.strip())

    # Inbound test from NAT1 side (host virbr0) -> Gendo eth0 must be dropped
    _, g_eth0, _ = docker_exec(g_cid, "ip -4 -o addr show eth0 | awk '{print $4}' | cut -d/ -f1")
    g_eth0_ip = g_eth0.strip()
    probe = subprocess.run(["ping", "-c", "2", "-W", "1", g_eth0_ip], capture_output=True, text=True)
    assert probe.returncode != 0, f"Inbound ping from NAT1 side to Gendo eth0 ({g_eth0_ip}) unexpectedly succeeded!"
    out_lines.append(f"\n--- Probe inbound NAT1 -> Gendo eth0 ({g_eth0_ip}) ---")
    out_lines.append(probe.stdout.strip() + f"\n(exit_code={probe.returncode}, koneksi baru dari NAT1 ditolak)")
    out_lines.append(f"\n--- Idempotency check (2x bash /root/gendo.sh): identik ({len(ipt_s.splitlines())} filter lines, {len(nat_s.splitlines())} nat lines) ---")

    save_evidence("soal5.txt", out_lines)
    print("[+] SOAL 5 PASSED: Gendo locked down, idempotent, internal->internet/LAN/Gendo OK, NAT1 inbound blocked.")


def run_soal6(tok: str, pid: str, hosts: list[dict]):
    nodes = get_nodes_map(tok, pid)

    # Stop any already-started test hosts cleanly before pushing permanent /etc/network/interfaces
    for h in hosts:
        hname = h["host"]
        if nodes[hname].get("status") == "started":
            req("POST", f"/v3/projects/{pid}/nodes/{nodes[hname]['node_id']}/stop", {}, token=tok)
    time.sleep(2.0)

    for h in hosts:
        hname = h["host"]
        iface_obj = ipaddress.IPv4Interface(h["cidr"])
        iface_txt = (
            "auto lo\n"
            "iface lo inet loopback\n\n"
            "auto eth0\n"
            "iface eth0 inet static\n"
            f"\taddress {iface_obj.ip}\n"
            f"\tnetmask {iface_obj.netmask}\n"
            f"\tgateway {h['gateway']}\n"
        )
        write_node_file(tok, pid, nodes[hname]["node_id"], "etc/network/interfaces", iface_txt)

    nodes = get_nodes_map(tok, pid)
    stopped = [h["host"] for h in hosts if nodes[h["host"]].get("status") != "started"]
    if stopped:
        start_nodes_batch(tok, pid, nodes, stopped, batch_size=8)
    time.sleep(2.0)

    # Restart Unit-01 via stop+start to verify IP/gateway persistence across reboot
    restart_node(tok, pid, nodes["Unit-01"]["node_id"])
    time.sleep(1.0)

    nodes = get_nodes_map(tok, pid)
    out_lines = ["=== SOAL 6: IP STATIS PERMANEN DI 25 HOST NON-ROUTER ==="]

    for h in hosts:
        hname = h["host"]
        cid = nodes[hname]["properties"]["container_id"]
        write_container_file(
            cid,
            "/root/init.sh",
            "#!/bin/sh\nprintf 'nameserver 8.8.8.8\\nnameserver 1.1.1.1\\n' > /etc/resolv.conf\n",
            executable=True,
        )
        docker_exec(cid, "sh /root/init.sh")
        rc, ip_out, err = docker_exec(cid, "ip -br a; ip route")
        if rc != 0 or h["cidr"] not in ip_out or f"default via {h['gateway']}" not in ip_out:
            raise RuntimeError(f"Host {hname} missing permanent IP/gw after boot/reload:\n{ip_out}\n{err}")
        rc_gw, gw_out, _ = docker_exec(cid, f"ping -c 2 -W 2 {h['gateway']}")
        rc_inet, inet_out, _ = docker_exec(cid, "ping -c 2 -W 2 8.8.8.8")
        if rc_gw != 0 or rc_inet != 0:
            raise RuntimeError(f"Host {hname} connectivity failed: gw={rc_gw}, inet={rc_inet}")

        if hname == "Unit-01":
            _, u_ip, _ = docker_exec(cid, "ip -br a; ip route; ping -c 3 -W 2 " + h["gateway"])
            out_lines.append("\n--- Unit-01 (setelah reload) ---")
            out_lines.append(u_ip.strip())

        gw_stat = [ln for ln in gw_out.splitlines() if "packet loss" in ln][0]
        inet_stat = [ln for ln in inet_out.splitlines() if "packet loss" in ln][0]
        out_lines.append(f"[OK] {hname:16s} {h['cidr']:16s} gw={h['gateway']:12s} | gw: {gw_stat} | inet: {inet_stat}")

    save_evidence("soal6.txt", out_lines)
    print("[+] SOAL 6 PASSED: All 25 hosts verified with permanent IP, gateway, and internet after reload.")


def render_listener_script(node_name: str, mode: str, services: list[tuple[int, str]]) -> str:
    """Build idempotent /root/<node>.sh for Soal 7 (log listeners) or Soal 8 (banner responders)."""
    slug = node_name.lower()
    lines = [
        "#!/bin/bash",
        "set -euo pipefail",
        "",
        f"# Konfigurasi layanan {node_name} (Modul 5 K-11)",
        "if ! dpkg -s iptables netcat-traditional >/dev/null 2>&1; then",
        "  apt-get update -qq",
        "  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq iptables netcat-traditional",
        "fi",
        "",
        "stop_loop() {",
        '  local pidfile="$1" port="$2"',
        '  if [ -f "$pidfile" ]; then',
        '    local oldpid; oldpid=$(cat "$pidfile" 2>/dev/null || true)',
        '    [ -n "$oldpid" ] && kill "$oldpid" 2>/dev/null || true',
        "  fi",
        '  pkill -f "nc.traditional -n -l -p ${port}\\b" 2>/dev/null || true',
        "}",
        "",
    ]
    for port, arg in services:
        pidf = f"/run/{slug}-{port}.pid"
        lines.append(f'stop_loop "{pidf}" "{port}"')
        if mode == "log":
            logf = arg
            lines.append(
                f'( while true; do nc.traditional -n -l -p {port} >> {logf} 2>&1; done ) </dev/null >/dev/null 2>&1 &'
            )
        else:
            banner_expr = arg
            lines.append(
                f"( while true; do nc.traditional -n -l -p {port} -c 'echo \"{banner_expr}\"'; done ) </dev/null >/dev/null 2>&1 &"
            )
        lines.append(f'echo $! > "{pidf}"')
    lines.append("sleep 0.3")
    return "\n".join(lines) + "\n"


def deploy_host_service(nodes: dict, node_name: str, mode: str, services: list[tuple[int, str]]):
    fname = f"{node_name.lower()}.sh"
    content = render_listener_script(node_name, mode, services)
    (SCRIPT_DIR / fname).write_text(content, encoding="utf-8")
    cid = nodes[node_name]["properties"]["container_id"]
    write_container_file(cid, f"/root/{fname}", content, executable=True)
    write_container_file(
        cid,
        "/root/init.sh",
        f"#!/bin/sh\nprintf 'nameserver 8.8.8.8\\nnameserver 1.1.1.1\\n' > /etc/resolv.conf\nbash /root/{fname}\n",
        executable=True,
    )
    rc, out, err = docker_exec(cid, f"bash /root/{fname}", timeout=120)
    if rc != 0:
        raise RuntimeError(f"{node_name} /root/{fname} failed (rc={rc}): {out}\n{err}")


def run_soal7(tok: str, pid: str, hosts: list[dict]):
    nodes = get_nodes_map(tok, pid)
    host_by_name = {h["host"]: h for h in hosts}

    magi_specs = {
        "Magi-Casper": [(5000, "/var/log/magi-5000.log")],
        "Magi-Balthasar": [(5000, "/var/log/magi-5000.log"), (5001, "/var/log/magi-5001.log")],
        "Magi-Melchior": [(5000, "/var/log/magi-5000.log")],
    }
    for name, svcs in magi_specs.items():
        cid = nodes[name]["properties"]["container_id"]
        docker_exec(cid, "rm -f /var/log/magi-*.log")
        deploy_host_service(nodes, name, "log", svcs)
        # Re-run once to prove idempotency (no duplicate listeners)
        rc, _, err = docker_exec(cid, f"bash /root/{name.lower()}.sh")
        assert rc == 0, f"Idempotent rerun failed on {name}: {err}"

    out_lines = ["=== SOAL 7: LAYANAN LISTENER MAGI (CASPER, BALTHASAR, MELCHIOR) ==="]
    for name in magi_specs:
        cid = nodes[name]["properties"]["container_id"]
        _, info, _ = docker_exec(cid, "dpkg-query -W -f='${Package} ${Version} (${Status})\\n' iptables netcat-traditional; ss -tlnp || netstat -tlnp || ps -ef | grep nc.traditional")
        out_lines.append(f"\n--- Status paket & listener @ {name} ---")
        out_lines.append(info.strip())

    lilith_cid = nodes["Lilith"]["properties"]["container_id"]
    tests = [
        ("Magi-Casper", host_by_name["Magi-Casper"]["ip"], 5000, "Pesan Lilith -> Casper 5000"),
        ("Magi-Balthasar", host_by_name["Magi-Balthasar"]["ip"], 5000, "Pesan Lilith -> Balthasar 5000"),
        ("Magi-Balthasar", host_by_name["Magi-Balthasar"]["ip"], 5001, "Pesan Lilith -> Balthasar 5001"),
        ("Magi-Melchior", host_by_name["Magi-Melchior"]["ip"], 5000, "Pesan Lilith -> Melchior 5000"),
    ]
    out_lines.append("\n--- Uji kirim pesan dari Lilith ---")
    for target, ip, port, msg in tests:
        rc, out, err = docker_exec(lilith_cid, f"printf '%s\\n' '{msg}' | nc -N -w 2 {ip} {port}")
        if rc != 0:
            raise RuntimeError(f"Lilith -> {target}:{port} nc failed (rc={rc}): {out} {err}")
        out_lines.append(f"[OK] Lilith -> {target} ({ip}:{port}): '{msg}' (exit={rc})")

    time.sleep(0.3)
    for name, svcs in magi_specs.items():
        cid = nodes[name]["properties"]["container_id"]
        for port, logf in svcs:
            _, log_txt, _ = docker_exec(cid, f"cat {logf}")
            out_lines.append(f"\n--- Log diterima @ {name} port {port} ({logf}) ---")
            out_lines.append(log_txt.strip())
            assert f"Lilith ->" in log_txt, f"Missing expected log on {name}:{port}: {log_txt!r}"

    save_evidence("soal7.txt", out_lines)
    print("[+] SOAL 7 PASSED: MAGI packages, listeners, Lilith messages, and logs verified.")


def run_soal8(tok: str, pid: str, hosts: list[dict]):
    nodes = get_nodes_map(tok, pid)
    host_by_name = {h["host"]: h for h in hosts}

    deploy_host_service(nodes, "Pen-Pen", "banner", [(80, "Welcome to $(hostname)")])
    deploy_host_service(nodes, "Tokyo3-Core", "banner", [(80, "Welcome to $(hostname)"), (8080, "syifa imutz")])

    out_lines = ["=== SOAL 8: LAYANAN NORMAL PEN-PEN DAN TOKYO3-CORE ==="]
    for name in ("Pen-Pen", "Tokyo3-Core"):
        cid = nodes[name]["properties"]["container_id"]
        _, info, _ = docker_exec(cid, "hostname; ss -tlnp || ps -ef | grep nc.traditional")
        out_lines.append(f"\n--- Status @ {name} ---")
        out_lines.append(info.strip())

    lilith_cid = nodes["Lilith"]["properties"]["container_id"]
    checks = [
        ("Pen-Pen", host_by_name["Pen-Pen"]["ip"], 80, "Welcome to Pen-Pen"),
        ("Tokyo3-Core", host_by_name["Tokyo3-Core"]["ip"], 80, "Welcome to Tokyo3-Core"),
        ("Tokyo3-Core", host_by_name["Tokyo3-Core"]["ip"], 8080, "syifa imutz"),
    ]
    out_lines.append("\n--- Uji nc dari Lilith (2x per port untuk bukti persistent loop) ---")
    for name, ip, port, expected in checks:
        for run_idx in (1, 2):
            rc, out, err = docker_exec(lilith_cid, f"nc -w 2 {ip} {port} < /dev/null")
            if rc != 0 or expected not in out:
                raise RuntimeError(f"Lilith -> {name}:{port} run {run_idx} failed (rc={rc}): out={out!r} err={err!r}")
            out_lines.append(f"[OK] run#{run_idx} Lilith -> {name} ({ip}:{port}) [rc={rc}]: {out.strip()}")
            time.sleep(0.15)

    out_lines.append("\n--- Uji port tertutup (port 22) harus langsung gagal, bukan hang ---")
    for name in ("Pen-Pen", "Tokyo3-Core"):
        ip = host_by_name[name]["ip"]
        t0 = time.monotonic()
        rc, out, err = docker_exec(lilith_cid, f"nc -zv -w 3 {ip} 22")
        elapsed = time.monotonic() - t0
        if rc == 0 or elapsed >= 1.5:
            raise RuntimeError(f"Port 22 probe on {name} unexpected: rc={rc}, elapsed={elapsed:.3f}s, out={out}, err={err}")
        out_lines.append(f"[OK] {name} ({ip}:22): exit={rc}, durasi={elapsed:.3f}s, msg={(out + err).strip()}")

    save_evidence("soal8.txt", out_lines)
    print("[+] SOAL 8 PASSED: Pen-Pen & Tokyo3-Core banners and fast port-22 rejection verified.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", required=True, choices=["soal2", "soal3", "soal4", "soal5", "soal6", "soal7", "soal8"])
    args = parser.parse_args()

    _, subnets, hosts, _ = allocate_vlsm()
    _, _, routes = build_wiring_and_routes(subnets, hosts)
    tok = authenticate()
    pid = get_project_id(tok)
    assert pid is not None, "Project K-11-MODUL-5 missing"

    if args.step == "soal2":
        run_soal2(tok, pid, routes)
    elif args.step == "soal3":
        run_soal3(tok, pid, hosts, routes)
    elif args.step == "soal4":
        run_soal4(tok, pid, hosts, routes)
    elif args.step == "soal5":
        run_soal5(tok, pid, hosts, routes)
    elif args.step == "soal6":
        run_soal6(tok, pid, hosts)
    elif args.step == "soal7":
        run_soal7(tok, pid, hosts)
    elif args.step == "soal8":
        run_soal8(tok, pid, hosts)


if __name__ == "__main__":
    main()
