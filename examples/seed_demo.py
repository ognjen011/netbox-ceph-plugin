"""Add optional, clearly labelled demo inventory to a local NetBox instance.

Run from NetBox's directory with this plugin installed and migrated:
    python manage.py shell -c 'exec(open("/path/to/examples/seed_demo.py").read())'

Existing objects are reused without replacing their field values. This script
does not run automatically during installation or migrations.
"""

from uuid import NAMESPACE_URL, uuid5

from django.db import transaction
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Rack, Site
from extras.models import Tag
from netbox_osd.models import CephCluster, CephOSD, CephOSDStatusNote


with transaction.atomic():
    demo_tag, _ = Tag.objects.get_or_create(
        slug="ceph-plugin-demo", defaults={"name": "Ceph plugin demo", "color": "9e9e9e"},
    )
    storage_tag, _ = Tag.objects.get_or_create(
        slug="ceph-storage", defaults={"name": "ceph-storage", "color": "2196f3"},
    )
    site, _ = Site.objects.get_or_create(
        slug="ceph-demo-dc", defaults={"name": "Ceph Demo DC", "status": "active"},
    )
    role, _ = DeviceRole.objects.get_or_create(
        slug="ceph-demo-storage", defaults={"name": "Ceph Demo Storage", "color": "2196f3"},
    )
    manufacturer, _ = Manufacturer.objects.get_or_create(
        slug="ceph-demo", defaults={"name": "Ceph Demo"},
    )
    device_type, _ = DeviceType.objects.get_or_create(
        manufacturer=manufacturer, model="Demo Storage Server",
        defaults={"slug": "ceph-demo-storage-server", "u_height": 2},
    )
    racks = []
    for letter in ("A", "B"):
        rack, _ = Rack.objects.get_or_create(
            site=site, name=f"Ceph Demo Rack {letter}",
            defaults={"status": "active", "u_height": 42},
        )
        racks.append(rack)
    rook, _ = CephCluster.objects.get_or_create(
        name="demo-rook-ceph",
        defaults={"site": site, "kubernetes_cluster": "demo-production-k8s",
                  "kubernetes_namespace": "rook-ceph", "description": "Local Rook-Ceph demo inventory"},
    )
    baremetal, _ = CephCluster.objects.get_or_create(
        name="demo-baremetal-ceph",
        defaults={"site": site, "description": "Local standalone Ceph demo inventory"},
    )
    for obj in (site, *racks, rook, baremetal):
        obj.tags.add(demo_tag)

    for node in range(1, 5):
        name = f"demo-ceph-storage-{node:02d}" if node < 4 else "demo-ceph-spare-01"
        device, _ = Device.objects.get_or_create(
            site=site, name=name,
            defaults={"role": role, "device_type": device_type, "rack": racks[0 if node < 3 else 1],
                      "position": 1 if node in (1, 3) else 3, "face": "front", "status": "active",
                      "description": "Local Ceph plugin demo server"},
        )
        device.tags.add(demo_tag, storage_tag)
        if node == 4:
            print(f"{device.name}: spare server, no OSDs; {device.get_absolute_url()}")
            continue
        cluster = rook if node < 3 else baremetal
        for disk, osd_type in enumerate(("nvme", "nvme", "ssd", "hdd")):
            osd_id = (node - 1) * 4 + disk if node < 3 else disk
            status = "out" if node == 2 and disk == 3 else "down" if node == 3 and disk == 3 else "active"
            separate_db = osd_type == "hdd"
            osd, _ = CephOSD.objects.get_or_create(
                device=device, name=f"osd.{osd_id}",
                defaults={
                    "cluster": cluster, "osd_type": osd_type, "encrypted": osd_type != "hdd",
                    "status": status, "disk_path": f"/dev/disk/by-id/demo-{node:02d}-{disk:02d}",
                    "serial_number": f"DEMO-{node:02d}-{disk:02d}",
                    "capacity_bytes": 16000000000000 if osd_type == "hdd" else 3840000000000,
                    "osd_uuid": uuid5(NAMESPACE_URL, f"netbox-ceph-demo:{name}:{osd_id}"),
                    "db_path": f"/dev/mapper/demo-db-{osd_id}" if separate_db else "",
                    "wal_path": f"/dev/mapper/demo-wal-{osd_id}" if separate_db else "",
                    "description": "Local Ceph plugin demo OSD",
                },
            )
            osd.tags.add(demo_tag)
            if status != "active":
                CephOSDStatusNote.objects.get_or_create(
                    osd=osd, reason="Demo: drive replacement pending", defaults={"status": status},
                )
        print(f"{device.name}: {cluster.name}, {device.ceph_osds.count()} OSDs; {device.get_absolute_url()}")
    print(f"Rook cluster: {rook.get_absolute_url()}")
    print(f"Standalone cluster: {baremetal.get_absolute_url()}")
