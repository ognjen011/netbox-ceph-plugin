#!/usr/bin/env python3
"""
Import Ceph OSD data from a YAML file into NetBox via the REST API.

Usage:
    python import_yaml.py osds.yaml

Requirements:
    pip install requests pyyaml

Environment variables:
    NETBOX_URL    e.g. https://netbox.example.com
    NETBOX_TOKEN  your API token
"""

import os
import sys
import yaml
import requests

NETBOX_URL = os.environ.get("NETBOX_URL", "http://localhost:8000").rstrip("/")
NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN", "")

if not NETBOX_TOKEN:
    sys.exit("Set NETBOX_TOKEN environment variable first.")

SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
})


def get_cluster_id(name: str) -> int:
    r = SESSION.get(f"{NETBOX_URL}/api/plugins/osd/clusters/", params={"name": name})
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        raise ValueError(f"Cluster '{name}' not found in NetBox")
    return results[0]["id"]


def get_device_id(name: str) -> int:
    r = SESSION.get(f"{NETBOX_URL}/api/dcim/devices/", params={"name": name})
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        raise ValueError(f"Device '{name}' not found in NetBox")
    return results[0]["id"]


def import_osds(yaml_file: str):
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    cluster_name = data.get("cluster")
    cluster_id = get_cluster_id(cluster_name) if cluster_name else None
    print(f"Cluster: {cluster_name} → id={cluster_id}")

    # Cache device lookups so we don't hit the API repeatedly
    device_cache: dict[str, int] = {}

    payload = []
    for osd in data["osds"]:
        device_name = osd["device"]
        if device_name not in device_cache:
            device_cache[device_name] = get_device_id(device_name)

        payload.append({
            "name": osd["name"],
            "cluster": cluster_id,
            "device": device_cache[device_name],
            "osd_type": osd.get("osd_type", "hdd"),
            "encrypted": osd.get("encrypted", False),
            "status": osd.get("status", "active"),
            "description": osd.get("description", ""),
        })

    print(f"Importing {len(payload)} OSDs...")

    # NetBox supports bulk POST — send the whole list in one request
    r = SESSION.post(f"{NETBOX_URL}/api/plugins/osd/osds/", json=payload)

    if r.status_code in (200, 201):
        created = r.json()
        if isinstance(created, list):
            print(f"  Created {len(created)} OSDs.")
        else:
            print(f"  Created OSD: {created.get('name')}")
    else:
        print(f"  ERROR {r.status_code}: {r.text}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} <osds.yaml>")
    import_osds(sys.argv[1])
