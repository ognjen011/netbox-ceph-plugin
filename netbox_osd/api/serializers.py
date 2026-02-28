from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from dcim.api.serializers import DeviceSerializer

from ..models import CephCluster, CephOSD, CephOSDStatusNote


class CephClusterSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_osd-api:cephcluster-detail"
    )

    class Meta:
        model = CephCluster
        fields = [
            "id",
            "url",
            "display",
            "name",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name"]


class CephOSDSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_osd-api:cephosd-detail"
    )
    cluster = CephClusterSerializer(nested=True, required=False, allow_null=True)
    device = DeviceSerializer(nested=True)

    class Meta:
        model = CephOSD
        fields = [
            "id",
            "url",
            "display",
            "cluster",
            "name",
            "device",
            "osd_type",
            "encrypted",
            "status",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "cluster", "device", "status"]


class CephOSDStatusNoteSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_osd-api:cephosdsstatusnote-detail"
    )
    osd = serializers.PrimaryKeyRelatedField(queryset=CephOSD.objects.all())

    class Meta:
        model = CephOSDStatusNote
        fields = [
            "id",
            "url",
            "display",
            "osd",
            "status",
            "reason",
            "resolved",
            "resolved_at",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
        brief_fields = ["id", "url", "display", "osd", "status", "resolved"]
