#!/usr/bin/env python3
"""Shared GNS3 v3 API and Docker container execution helpers for K-11 Modul 5."""

from __future__ import annotations

import base64
import csv
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
GNS3_BASE = "http://127.0.0.1:3080"
GNS3_USER = "K-11"
GNS3_PASS = "K-11@GNS3"
PROJECT_NAME = "K-11-MODUL-5"


def req(method: str, path: str, body=None, token: str | None = None, raw_data: bytes | None = None, content_type: str = "application/json"):
    """Send an HTTP request to local gns3server and return (status_code, decoded_payload)."""
    if raw_data is not None:
        data = raw_data
    elif body is not None:
        data = json.dumps(body).encode()
    else:
        data = None

    request = urllib.request.Request(GNS3_BASE + path, method=method, data=data)
    if data is not None:
        request.add_header("Content-Type", content_type)
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            raw = resp.read().decode("utf-8", "replace")
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                return resp.status, json.loads(raw) if raw else None
            return resp.status, raw
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", "replace")
        try:
            return exc.code, json.loads(err)
        except Exception:
            return exc.code, err


def authenticate() -> str:
    status, payload = req("POST", "/v3/access/users/authenticate", {"username": GNS3_USER, "password": GNS3_PASS})
    if status != 200:
        raise RuntimeError(f"GNS3 auth failed ({status}): {payload}")
    return payload["access_token"]


def get_project_id(token: str, name: str = PROJECT_NAME) -> str | None:
    _, projects = req("GET", "/v3/projects", token=token)
    for proj in projects or []:
        if proj["name"] == name:
            return proj["project_id"]
    return None


def ensure_project_open(token: str, name: str = PROJECT_NAME) -> str:
    pid = get_project_id(token, name)
    if pid is None:
        st, created = req("POST", "/v3/projects", {"name": name}, token=token)
        if st not in (200, 201):
            raise RuntimeError(f"Failed creating project {name}: {st} {created}")
        pid = created["project_id"]
    st, proj = req("GET", f"/v3/projects/{pid}", token=token)
    if st == 200 and proj.get("status") != "opened":
        req("POST", f"/v3/projects/{pid}/open", {}, token=token)
        time.sleep(0.5)
    return pid


def get_nodes_map(token: str, pid: str) -> dict[str, dict]:
    st, nodes = req("GET", f"/v3/projects/{pid}/nodes", token=token)
    if st != 200:
        raise RuntimeError(f"Failed listing nodes ({st}): {nodes}")
    return {n["name"]: n for n in (nodes or [])}


def write_node_file(token: str, pid: str, node_id: str, rel_path: str, text: str):
    """Write text to a file inside a GNS3 node via File API (path relative to /)."""
    rel = rel_path.lstrip("/")
    for attempt in range(3):
        st, out = req(
            "POST",
            f"/v3/projects/{pid}/nodes/{node_id}/files/{rel}",
            raw_data=text.encode(),
            content_type="text/plain",
            token=token,
        )
        if st in (200, 201):
            return st, out
        time.sleep(1)
    raise RuntimeError(f"Failed writing /{rel} to node {node_id}: {st} {out}")


def start_nodes_batch(token: str, pid: str, nodes_map: dict[str, dict], names: list[str], batch_size: int = 8):
    """Start GNS3 nodes in batches and wait until started."""
    for i in range(0, len(names), batch_size):
        chunk = names[i : i + batch_size]
        for name in chunk:
            node = nodes_map[name]
            if node.get("status") != "started":
                st, res = req("POST", f"/v3/projects/{pid}/nodes/{node['node_id']}/start", {}, token=token)
                if st not in (200, 201, 204):
                    raise RuntimeError(f"Failed starting {name}: {st} {res}")
        time.sleep(1.0)


def restart_node(token: str, pid: str, node_id: str, timeout: int = 20) -> dict:
    """Stop and start a GNS3 node cleanly (avoids GNS3 Docker /reload dropping veths)."""
    req("POST", f"/v3/projects/{pid}/nodes/{node_id}/stop", {}, token=token)
    deadline = time.time() + timeout
    while time.time() < deadline:
        st, info = req("GET", f"/v3/projects/{pid}/nodes/{node_id}", token=token)
        if st == 200 and info.get("status") == "stopped":
            break
        time.sleep(0.5)
    time.sleep(0.5)
    st, res = req("POST", f"/v3/projects/{pid}/nodes/{node_id}/start", {}, token=token)
    if st not in (200, 201, 204):
        raise RuntimeError(f"Failed starting node {node_id}: {st} {res}")
    while time.time() < deadline:
        st, info = req("GET", f"/v3/projects/{pid}/nodes/{node_id}", token=token)
        if st == 200 and info.get("status") == "started":
            cid = info.get("properties", {}).get("container_id")
            if cid:
                rc, _, _ = docker_exec(cid, "ip -4 -o addr show eth0 | grep -q 'inet '")
                if rc == 0:
                    return info
        time.sleep(0.5)
    raise RuntimeError(f"Node {node_id} did not come up with eth0 within {timeout}s")


def docker_exec(container_id: str, command: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a shell command inside a started GNS3 Docker container using sh -c."""
    proc = subprocess.run(
        ["docker", "exec", container_id, "sh", "-c", command],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def write_container_file(container_id: str, abs_path: str, text: str, executable: bool = False):
    """Write text into a running container via base64 so /root bind-mount persists and stays host-readable."""
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    mode = "0755" if executable else "0644"
    parent_dir = str(Path(abs_path).parent)
    cmd = f"mkdir -p '{parent_dir}' && printf '%s' '{b64}' | base64 -d > '{abs_path}' && chmod {mode} '{abs_path}'"
    if abs_path.startswith("/root/"):
        cmd = "chmod 0755 /root && " + cmd
    rc, _, err = docker_exec(container_id, cmd)
    if rc != 0:
        raise RuntimeError(f"Failed writing {abs_path} in {container_id[:12]}: {err}")


def load_hosts_csv() -> list[dict[str, str]]:
    with (DOCS / "hosts.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_cables_csv() -> list[dict[str, str]]:
    with (DOCS / "cables.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_addresses_csv() -> list[dict[str, str]]:
    with (DOCS / "addresses.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
