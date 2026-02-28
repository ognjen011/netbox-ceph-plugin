# netbox-osd-plugin

A NetBox plugin for tracking Ceph OSDs across your storage infrastructure.

## Features

- **CephOSD** — track each OSD by name (`osd.0`, `osd.42`), host device, type (HDD / SSD / NVMe), encryption status, and current state (Active / Down / Out / Destroyed)
- **CephOSDStatusNote** — append structured notes whenever an OSD changes state; record the reason and mark it resolved when the issue is cleared
- **Device page integration** — a Ceph OSDs panel is automatically injected into every NetBox Device detail page
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

### CephOSD

| Field        | Description                                         |
|-------------|-----------------------------------------------------|
| `name`      | OSD identifier, e.g. `osd.0`, `osd.88`             |
| `device`    | NetBox Device (the storage host)                    |
| `osd_type`  | `hdd` / `ssd` / `nvme`                             |
| `encrypted` | Boolean — at-rest encryption                        |
| `status`    | `active` / `down` / `out` / `destroyed`            |
| `description` | Free-text notes (path, pool, etc.)               |
| `tags`      | NetBox tags                                         |

Rack and site are read from `device.rack` and `device.site`.

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
