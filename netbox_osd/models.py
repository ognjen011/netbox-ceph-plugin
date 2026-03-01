from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .choices import OSDStatusChoices, OSDTypeChoices, NoteStatusChoices


class CephCluster(NetBoxModel):
    """
    A Ceph cluster.  OSDs and their host devices are grouped under a cluster.
    """

    name = models.CharField(max_length=100, unique=True)
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ceph_clusters",
        help_text="Datacenter (site) where this cluster resides",
    )
    description = models.TextField(blank=True)

    clone_fields = ["site", "description"]

    class Meta:
        ordering = ["name"]
        verbose_name = "Ceph Cluster"
        verbose_name_plural = "Ceph Clusters"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_osd:cephcluster", args=[self.pk])

    @property
    def osd_count(self):
        return self.osds.count()

    @property
    def node_count(self):
        return self.osds.values("device").distinct().count()


class CephOSD(NetBoxModel):
    """
    Represents a single Ceph OSD (e.g. osd.1, osd.88).

    Linked to a NetBox Device (the storage host).  Rack and site are derived
    from the device — no duplication needed.
    """

    cluster = models.ForeignKey(
        to=CephCluster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="osds",
        help_text="Ceph cluster this OSD belongs to",
    )
    name = models.CharField(
        max_length=100,
        help_text="OSD identifier, e.g. osd.0, osd.42",
    )
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="ceph_osds",
        help_text="Host device this OSD runs on",
    )
    osd_type = models.CharField(
        max_length=10,
        choices=OSDTypeChoices,
        default=OSDTypeChoices.HDD,
        verbose_name="OSD type",
    )
    encrypted = models.BooleanField(
        default=False,
        help_text="Is this OSD encrypted at rest?",
    )
    status = models.CharField(
        max_length=20,
        choices=OSDStatusChoices,
        default=OSDStatusChoices.ACTIVE,
    )
    description = models.TextField(
        blank=True,
        help_text="Optional notes about this OSD (drive path, pool, etc.)",
    )

    clone_fields = ["cluster", "device", "osd_type", "encrypted", "status"]

    class Meta:
        ordering = ["device", "name"]
        verbose_name = "Ceph OSD"
        verbose_name_plural = "Ceph OSDs"
        unique_together = [["device", "name"]]

    def __str__(self):
        return f"{self.name} @ {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_osd:cephosd", args=[self.pk])

    def get_status_color(self):
        return OSDStatusChoices.colors.get(self.status)

    def get_osd_type_color(self):
        return OSDTypeChoices.colors.get(self.osd_type)

    @property
    def rack(self):
        return self.device.rack

    @property
    def site(self):
        return self.device.site


class CephOSDStatusNote(NetBoxModel):
    """
    A timestamped status note for a CephOSD.

    Use this to record *why* an OSD went down or out, track maintenance
    windows, or log recovery.  Multiple notes per OSD build an audit trail.
    """

    osd = models.ForeignKey(
        to=CephOSD,
        on_delete=models.CASCADE,
        related_name="status_notes",
    )
    status = models.CharField(
        max_length=20,
        choices=NoteStatusChoices,
        help_text="OSD state that triggered this note",
    )
    reason = models.TextField(
        help_text="Describe why the OSD is in this state",
    )
    resolved = models.BooleanField(
        default=False,
        help_text="Mark this note as resolved / no longer active",
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was this issue resolved?",
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "OSD Status Note"
        verbose_name_plural = "OSD Status Notes"

    def __str__(self):
        return f"{self.osd} — {self.get_status_display()} ({self.created:%Y-%m-%d})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_osd:cephosdsstatusnote", args=[self.pk])

    def get_status_color(self):
        return NoteStatusChoices.colors.get(self.status)
