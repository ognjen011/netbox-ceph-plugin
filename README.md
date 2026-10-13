# netbox-ceph-plugin

A NetBox plugin for tracking Ceph OSDs across your storage infrastructure.

## Features

- **CephOSD** — track each OSD by name (`osd.0`, `osd.42`), host device, type (HDD / SSD / NVMe), encryption status, and current state (Active / Down / Out / Destroyed)
- **CephOSDStatusNote** — append structured notes whenever an OSD changes state; record the reason and mark it resolved when the issue is cleared
- **Device page integration** — a Ceph OSDs panel is automatically injected into every NetBox Device detail page
- **Device OSD tab** — open a device's **Ceph OSDs** tab to see only the OSDs assigned to that node
- **Rack & Site** derived automatically from the host device — no duplication
- **Full REST API** under `/api/plugins/osd/`
- **Tags, custom fields, change log, journaling** — all inherited from NetBox's own object model

## Requirements

- NetBox ≥ 4.0
- Python ≥ 3.10

## Installation

```bash
pip install -e /path/to/netbox-osd-plugin
```

Add to `configuration.py`:

```python
PLUGINS = [
    "netbox_osd",
]
```

Run migrations:

```bash
python manage.py migrate netbox_osd
```

## Data model

### CephCluster

| Field | Description |
|-------|-------------|
| `name` | Ceph cluster name |
| `site` | NetBox site (optional) |
| `kubernetes_cluster` | Name of the hosting Kubernetes cluster (optional) |
| `kubernetes_namespace` | Namespace containing the deployment, e.g. `rook-ceph` (optional) |
| `description` | Free-text notes |

For Rook-Ceph deployments, record the Kubernetes cluster and namespace here.
Leave them blank for deployments outside Kubernetes. These fields are available
in the cluster form, REST API, CSV import, filters, and optional table columns.

### CephOSD

| Field        | Description                                         |
|-------------|-----------------------------------------------------|
| `name`      | OSD identifier, e.g. `osd.0`, `osd.88`             |
| `device`    | NetBox Device (the storage host)                    |
| `osd_type`  | `hdd` / `ssd` / `nvme`                             |
| `encrypted` | Boolean — at-rest encryption                        |
| `status`    | `active` / `down` / `out` / `destroyed`            |
| `disk_path` | Data device path, preferably `/dev/disk/by-id/...` (optional) |
| `serial_number` | Physical data drive serial number (optional) |
| `capacity_bytes` | Positive integer capacity in bytes; blank if unknown |
| `osd_uuid` | Ceph OSD FSID UUID, distinct from the cluster FSID (optional) |
| `db_path` | Separate BlueStore `block.db` device or logical volume (optional) |
| `wal_path` | Separate BlueStore `block.wal` device or logical volume (optional) |
| `description` | Free-text notes (path, pool, etc.)               |
| `tags`      | NetBox tags                                         |

Rack and site are read from `device.rack` and `device.site`.

Storage fields are available in the edit form, REST API, CSV imports, and YAML
import script. Existing imports can omit them. For API requests, use `null` for
unknown capacity or UUID and an empty string for unused paths or serial numbers.
Leave DB/WAL paths blank when they are not configured as separate devices.
The details page displays capacity in a readable size format; list and device
tab tables offer the storage fields as optional columns.

### CephOSDStatusNote

| Field        | Description                                          |
|-------------|------------------------------------------------------|
| `osd`       | FK → CephOSD                                         |
| `status`    | `down` / `out` / `maintenance` / `recovered` / `other` |
| `reason`    | Free-text: why the OSD is in this state              |
| `resolved`  | Boolean — toggle when the issue is fixed             |
| `resolved_at` | Timestamp set automatically when resolved          |

## REST API

```
GET  /api/plugins/osd/osds/
GET  /api/plugins/osd/osds/<id>/
POST /api/plugins/osd/osds/

GET  /api/plugins/osd/notes/
POST /api/plugins/osd/notes/
```

Supports the same filtering, pagination, and authentication as all NetBox API endpoints.

For example, update OSD storage properties with
`PATCH /api/plugins/osd/osds/<id>/`:

```json
{
  "disk_path": "/dev/disk/by-id/nvme-example-drive-01",
  "serial_number": "EXAMPLE-NVME-01",
  "capacity_bytes": 3840000000000,
  "osd_uuid": "88ab9018-f84b-4d62-90b4-ce7c076728ff",
  "db_path": "",
  "wal_path": ""
}
```

Record the hosting Kubernetes cluster using
`PATCH /api/plugins/osd/clusters/<id>/`:

```json
{
  "kubernetes_cluster": "production-k8s",
  "kubernetes_namespace": "rook-ceph"
}
```

## Tests

With the plugin installed and enabled in a NetBox environment, run:

```bash
python manage.py test netbox_osd.tests
```

For a local preview, `examples/seed_demo.py` creates four labelled demo servers,
two Ceph clusters, and twelve OSDs with storage properties and sample status notes.
It includes a Rook-Ceph deployment, a standalone deployment, and an empty spare
server. Run it explicitly through NetBox's management shell as described in the
script. It is never run automatically and reuses existing demo objects without
overwriting their field values.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.
