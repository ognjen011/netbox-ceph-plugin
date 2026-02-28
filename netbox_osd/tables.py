import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn, TagColumn, ToggleColumn

from .models import CephCluster, CephOSD, CephOSDStatusNote


# ─── CephCluster ──────────────────────────────────────────────────────────────

class CephClusterTable(NetBoxTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    node_count = tables.Column(verbose_name="Nodes", orderable=False)
    osd_count = tables.Column(verbose_name="OSDs", orderable=False)
    tags = TagColumn(url_name="plugins:netbox_osd:cephcluster_list")

    class Meta(NetBoxTable.Meta):
        model = CephCluster
        fields = (
            "pk",
            "name",
            "node_count",
            "osd_count",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = ("pk", "name", "node_count", "osd_count", "tags")

    def render_node_count(self, record):
        return record.node_count

    def render_osd_count(self, record):
        return record.osd_count


# ─── Cluster → Nodes (Device) sub-table ──────────────────────────────────────

class ClusterNodeTable(tables.Table):
    """
    Simple table of Devices (nodes) within a cluster, annotated with OSD counts.
    Not a NetBoxTable — just a display table, no bulk actions needed.
    """

    name = tables.Column(
        linkify=lambda record: record.get_absolute_url(),
        verbose_name="Device (node)",
    )
    site = tables.Column(
        accessor="site",
        linkify=lambda record: record.site.get_absolute_url() if record.site else None,
    )
    rack = tables.Column(
        accessor="rack",
        linkify=lambda record: record.rack.get_absolute_url() if record.rack else None,
    )
    osd_count = tables.Column(verbose_name="OSDs", orderable=False)

    class Meta:
        attrs = {"class": "table table-hover table-headings"}
        sequence = ("name", "site", "rack", "osd_count")
        empty_text = "No nodes in this cluster."


# ─── CephOSD ──────────────────────────────────────────────────────────────────

class CephOSDTable(NetBoxTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    cluster = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    rack = tables.Column(
        accessor="device.rack",
        linkify=lambda record: record.device.rack.get_absolute_url() if record.device.rack else None,
        orderable=False,
    )
    site = tables.Column(
        accessor="device.site",
        linkify=lambda record: record.device.site.get_absolute_url() if record.device.site else None,
        orderable=False,
    )
    osd_type = ChoiceFieldColumn(verbose_name="Type")
    encrypted = tables.BooleanColumn()
    status = ChoiceFieldColumn()
    open_notes = tables.Column(verbose_name="Open notes", orderable=False, empty_values=())
    tags = TagColumn(url_name="plugins:netbox_osd:cephosd_list")

    class Meta(NetBoxTable.Meta):
        model = CephOSD
        fields = (
            "pk",
            "name",
            "cluster",
            "device",
            "rack",
            "site",
            "osd_type",
            "encrypted",
            "status",
            "open_notes",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = (
            "pk",
            "name",
            "cluster",
            "device",
            "rack",
            "site",
            "osd_type",
            "encrypted",
            "status",
            "open_notes",
        )

    def render_open_notes(self, record):
        count = record.status_notes.filter(resolved=False).count()
        return count or "—"


# ─── CephOSDStatusNote ────────────────────────────────────────────────────────

class CephOSDStatusNoteTable(NetBoxTable):
    pk = ToggleColumn()
    osd = tables.Column(linkify=True)
    status = ChoiceFieldColumn()
    resolved = tables.BooleanColumn()
    tags = TagColumn(url_name="plugins:netbox_osd:cephosdsstatusnote_list")

    class Meta(NetBoxTable.Meta):
        model = CephOSDStatusNote
        fields = (
            "pk",
            "osd",
            "status",
            "reason",
            "resolved",
            "resolved_at",
            "tags",
            "created",
            "last_updated",
        )
        default_columns = (
            "pk",
            "osd",
            "status",
            "reason",
            "resolved",
            "created",
        )
