from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets import CephClusterFilterSet, CephOSDFilterSet, CephOSDStatusNoteFilterSet
from ..models import CephCluster, CephOSD, CephOSDStatusNote
from .serializers import CephClusterSerializer, CephOSDSerializer, CephOSDStatusNoteSerializer


class CephClusterViewSet(NetBoxModelViewSet):
    queryset = CephCluster.objects.prefetch_related("tags")
    serializer_class = CephClusterSerializer
    filterset_class = CephClusterFilterSet


class CephOSDViewSet(NetBoxModelViewSet):
    queryset = CephOSD.objects.prefetch_related("cluster", "device__rack", "device__site", "tags")
    serializer_class = CephOSDSerializer
    filterset_class = CephOSDFilterSet


class CephOSDStatusNoteViewSet(NetBoxModelViewSet):
    queryset = CephOSDStatusNote.objects.prefetch_related("osd", "tags")
    serializer_class = CephOSDStatusNoteSerializer
    filterset_class = CephOSDStatusNoteFilterSet
