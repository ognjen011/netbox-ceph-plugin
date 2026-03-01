from django import forms
from django.utils.timezone import now
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelImportForm, NetBoxModelBulkEditForm
from dcim.models import Device, Rack, Site
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from .choices import OSDStatusChoices, OSDTypeChoices, NoteStatusChoices
from .models import CephCluster, CephOSD, CephOSDStatusNote


# ─── CephCluster ──────────────────────────────────────────────────────────────

class CephClusterForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        help_text="Datacenter (site) where this cluster resides",
    )
    description = CommentField()

    fieldsets = (
        FieldSet("name", "site", name="Cluster"),
        FieldSet("description", name="Notes"),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = CephCluster
        fields = ["name", "site", "description", "tags"]


class CephClusterFilterForm(NetBoxModelFilterSetForm):
    model = CephCluster

    site_id = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
    )
    tag = TagFilterField(model)


# ─── CephOSD ──────────────────────────────────────────────────────────────────

class CephOSDForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(
        queryset=CephCluster.objects.all(),
        required=False,
        help_text="Ceph cluster this OSD belongs to",
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        help_text="Host device (node) this OSD runs on",
    )
    description = CommentField()

    fieldsets = (
        FieldSet("cluster", "name", "device", "osd_type", "encrypted", "status", name="OSD"),
        FieldSet("description", name="Notes"),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = CephOSD
        fields = [
            "cluster",
            "name",
            "device",
            "osd_type",
            "encrypted",
            "status",
            "description",
            "tags",
        ]


class CephOSDBulkEditForm(NetBoxModelBulkEditForm):
    model = CephOSD

    cluster = DynamicModelChoiceField(
        queryset=CephCluster.objects.all(),
        required=False,
    )
    osd_type = forms.ChoiceField(
        choices=[("", "---------")] + list(OSDTypeChoices),
        required=False,
        label="OSD type",
    )
    status = forms.ChoiceField(
        choices=[("", "---------")] + list(OSDStatusChoices),
        required=False,
    )
    encrypted = forms.NullBooleanField(
        required=False,
        widget=forms.NullBooleanSelect(),
    )

    nullable_fields = ("cluster",)


class CephOSDFilterForm(NetBoxModelFilterSetForm):
    model = CephOSD

    cluster_id = DynamicModelChoiceField(
        queryset=CephCluster.objects.all(),
        required=False,
        label="Cluster",
    )
    device_id = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
    )
    rack_id = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label="Rack",
    )
    site_id = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
    )
    osd_type = forms.MultipleChoiceField(
        choices=OSDTypeChoices,
        required=False,
        label="OSD type",
    )
    status = forms.MultipleChoiceField(
        choices=OSDStatusChoices,
        required=False,
    )
    encrypted = forms.NullBooleanField(required=False, widget=forms.NullBooleanSelect())
    tag = TagFilterField(model)


# ─── CephOSDStatusNote ────────────────────────────────────────────────────────

class CephOSDStatusNoteForm(NetBoxModelForm):
    osd = DynamicModelChoiceField(
        queryset=CephOSD.objects.all(),
        help_text="OSD this note belongs to",
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Describe why the OSD is in this state",
    )
    resolved_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text="Leave blank if not yet resolved",
    )

    fieldsets = (
        FieldSet("osd", "status", name="OSD Status"),
        FieldSet("reason", name="Details"),
        FieldSet("resolved", "resolved_at", name="Resolution"),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = CephOSDStatusNote
        fields = [
            "osd",
            "status",
            "reason",
            "resolved",
            "resolved_at",
            "tags",
        ]

    def clean(self):
        cleaned = super().clean()
        resolved = cleaned.get("resolved")
        resolved_at = cleaned.get("resolved_at")

        if resolved and not resolved_at:
            cleaned["resolved_at"] = now()

        if not resolved:
            cleaned["resolved_at"] = None

        return cleaned


class CephOSDStatusNoteFilterForm(NetBoxModelFilterSetForm):
    model = CephOSDStatusNote

    osd_id = DynamicModelChoiceField(
        queryset=CephOSD.objects.all(),
        required=False,
        label="OSD",
    )
    status = forms.MultipleChoiceField(
        choices=NoteStatusChoices,
        required=False,
    )
    resolved = forms.NullBooleanField(required=False, widget=forms.NullBooleanSelect())
    tag = TagFilterField(model)


# ─── CSV Import Forms ─────────────────────────────────────────────────────────

class CephClusterImportForm(NetBoxModelImportForm):
    """
    CSV columns: name, site, description

    - site: exact site slug (optional)

    Example:
        name,site,description
        prod-ceph-01,dc1,Production Ceph cluster
        dev-ceph-01,,Dev cluster
    """

    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name="slug",
        required=False,
        help_text="Site slug",
    )

    class Meta:
        model = CephCluster
        fields = ["name", "site", "description"]


class CephOSDImportForm(NetBoxModelImportForm):
    """
    CSV columns: name, cluster, device, osd_type, encrypted, status, description

    - cluster : exact cluster name (optional)
    - device  : exact device name in NetBox
    - osd_type: hdd | ssd | nvme
    - encrypted: true | false
    - status  : active | down | out | destroyed

    Example:
        name,cluster,device,osd_type,encrypted,status,description
        osd.0,prod-ceph-01,storage-01,nvme,true,active,
        osd.1,prod-ceph-01,storage-01,nvme,true,active,
        osd.2,prod-ceph-01,storage-01,hdd,false,down,Scheduled for replacement
    """

    cluster = CSVModelChoiceField(
        queryset=CephCluster.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Cluster name",
    )
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        help_text="Device (host) name",
    )
    osd_type = CSVChoiceField(
        choices=OSDTypeChoices,
        help_text="hdd / ssd / nvme",
    )
    status = CSVChoiceField(
        choices=OSDStatusChoices,
        help_text="active / down / out / destroyed",
    )

    class Meta:
        model = CephOSD
        fields = ["cluster", "name", "device", "osd_type", "encrypted", "status", "description"]


class CephOSDStatusNoteImportForm(NetBoxModelImportForm):
    """
    CSV columns: osd_device, osd_name, status, reason, resolved

    - osd_device : device name the OSD lives on (used with osd_name to find the OSD)
    - osd_name   : OSD identifier, e.g. osd.0
    - status     : down | out | maintenance | recovered | other
    - reason     : free text (quote if it contains commas)
    - resolved   : true | false

    Example:
        osd_device,osd_name,status,reason,resolved
        storage-01,osd.2,down,SMART errors on /dev/sdb ticket #4421,false
        storage-02,osd.3,out,Drive permanently failed replaced,true
    """

    osd_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        help_text="Device name the OSD lives on",
    )
    osd_name = forms.CharField(
        help_text="OSD name, e.g. osd.0",
    )
    status = CSVChoiceField(
        choices=NoteStatusChoices,
        help_text="down / out / maintenance / recovered / other",
    )

    class Meta:
        model = CephOSDStatusNote
        fields = ["osd_device", "osd_name", "status", "reason", "resolved"]

    def clean(self):
        cleaned = super().clean()
        device = cleaned.get("osd_device")
        osd_name = cleaned.get("osd_name")
        if device and osd_name:
            try:
                cleaned["osd"] = CephOSD.objects.get(device=device, name=osd_name)
            except CephOSD.DoesNotExist:
                raise forms.ValidationError(
                    f"No OSD named '{osd_name}' found on device '{device}'"
                )
        return cleaned

    def save(self, commit=True):
        self.instance.osd = self.cleaned_data["osd"]
        return super().save(commit=commit)
