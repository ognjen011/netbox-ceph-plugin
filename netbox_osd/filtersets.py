import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Device, Rack, Site

from .choices import OSDStatusChoices, OSDTypeChoices, NoteStatusChoices
from .models import CephCluster, CephOSD, CephOSDStatusNote


class CephClusterFilterSet(NetBoxModelFilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label="Site (ID)",
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name="site__slug",
        queryset=Site.objects.all(),
        to_field_name="slug",
        label="Site (slug)",
    )

    class Meta:
        model = CephCluster
        fields = ["name", "site_id"]

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CephOSDFilterSet(NetBoxModelFilterSet):
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CephCluster.objects.all(),
        label="Cluster (ID)",
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        field_name="cluster__name",
        queryset=CephCluster.objects.all(),
        to_field_name="name",
        label="Cluster (name)",
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Device (ID)",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__rack",
        queryset=Rack.objects.all(),
        label="Rack (ID)",
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__site",
        queryset=Site.objects.all(),
        label="Site (ID)",
    )
    osd_type = django_filters.MultipleChoiceFilter(choices=OSDTypeChoices)
    status = django_filters.MultipleChoiceFilter(choices=OSDStatusChoices)
    encrypted = django_filters.BooleanFilter()

    class Meta:
        model = CephOSD
        fields = ["name", "osd_type", "status", "encrypted"]

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CephOSDStatusNoteFilterSet(NetBoxModelFilterSet):
    osd_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CephOSD.objects.all(),
        label="OSD (ID)",
    )
    status = django_filters.MultipleChoiceFilter(choices=NoteStatusChoices)
    resolved = django_filters.BooleanFilter()

    class Meta:
        model = CephOSDStatusNote
        fields = ["osd_id", "status", "resolved"]

    def search(self, queryset, name, value):
        return queryset.filter(reason__icontains=value)
