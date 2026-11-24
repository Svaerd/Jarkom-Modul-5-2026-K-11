#!/usr/bin/env python3
"""Helper for before/after kernel & network diffing and blind sabotage execution (Soal 9, 10, 12)."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gns3_helper import docker_exec

SNAPSHOT_CMD = """
echo "=== IP LINK ==="
ip -br link
echo "=== IP ADDR ==="
ip -br a
echo "=== IP ROUTE ALL ==="
ip route show table all | sort
echo "=== IP RULE ==="
ip rule list
echo "=== SYSCTL NET.IPV4 ==="
sysctl -a 2>/dev/null | grep -E '^net\\.ipv4\\.(ip_forward|conf\\.[^.]+\\.(rp_filter|forwarding|accept_redirects|send_redirects)|icmp_)' | sort
echo "=== IPTABLES FILTER ==="
iptables -S
echo "=== IPTABLES NAT ==="
iptables -t nat -S
echo "=== IPTABLES MANGLE ==="
iptables -t mangle -S
echo "=== IPTABLES RAW ==="
iptables -t raw -S
echo "=== IPTABLES-LEGACY FILTER ==="
iptables-legacy -S 2>/dev/null || true
echo "=== IPTABLES-LEGACY NAT ==="
iptables-legacy -t nat -S 2>/dev/null || true
echo "=== RESOLV.CONF ==="
cat /etc/resolv.conf
"""


def take_snapshot(cid: str) -> str:
    rc, out, err = docker_exec(cid, SNAPSHOT_CMD, timeout=20)
    if rc != 0:
        raise RuntimeError(f"Snapshot failed in {cid[:12]}: {err}")
    return out


def diff_snapshots(label: str, before: str, after: str) -> str:
    lines = list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=f"{label}-before",
            tofile=f"{label}-after",
            lineterm="",
        )
    )
    return "\n".join(lines) if lines else "(no kernel/network diff detected)"


def blind_exec_gdrive(cid: str, file_id: str, tmp_name: str) -> str:
    """Download Google Drive script directly inside target container, run it blindly, and remove it."""
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    tmp_path = f"/tmp/{tmp_name}"
    dl_cmd = (
        f"curl -fsSL -w 'content_type=%{{content_type}} size=%{{size_download}}\\n' "
        f"'{url}' -o '{tmp_path}'"
    )
    rc, meta, err = docker_exec(cid, dl_cmd, timeout=30)
    if rc != 0:
        raise RuntimeError(f"Download failed for {tmp_name} in {cid[:12]}: {meta} {err}")
    if "text/html" in meta.lower():
        docker_exec(cid, f"rm -f '{tmp_path}'")
        raise RuntimeError(f"Download returned HTML instead of script for {tmp_name}: {meta.strip()}")

    rc_run, out_run, err_run = docker_exec(cid, f"bash '{tmp_path}'; ec=$?; rm -f '{tmp_path}'; exit $ec", timeout=30)
    return f"download: {meta.strip()}\nexec_rc: {rc_run}\nstdout:\n{out_run.strip()}\nstderr:\n{err_run.strip()}"
