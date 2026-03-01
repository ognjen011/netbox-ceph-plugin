from django.db.models import Count
from django_tables2 import RequestConfig
from netbox.views import generic
from utilities.views import register_model_view
from dcim.models import Device

from .filtersets import CephClusterFilterSet, CephOSDFilterSet, CephOSDStatusNoteFilterSet
from .forms import (
    CephClusterForm,
    CephClusterFilterForm,
    CephClusterImportForm,
    CephOSDForm,
    CephOSDBulkEditForm,
    CephOSDFilterForm,
    CephOSDImportForm,
    CephOSDStatusNoteForm,
    CephOSDStatusNoteFilterForm,
    CephOSDStatusNoteImportForm,
)
from .models import CephCluster, CephOSD, CephOSDStatusNote
from .tables import CephClusterTable, ClusterNodeTable, CephOSDTable, CephOSDStatusNoteTable


# ─── CephCluster ──────────────────────────────────────────────────────────────

@register_model_view(CephCluster)
class CephClusterView(generic.ObjectView):
    queryset = CephCluster.objects.prefetch_related("tags")

    def get_extra_context(self, request, instance):
        # Nodes: distinct devices that have OSDs in this cluster, annotated with count
        nodes_qs = (
            Device.objects.filter(ceph_osds__cluster=instance)
            .annotate(osd_count=Count("ceph_osds"))
            .distinct()
        )
        nodes_table = ClusterNodeTable(nodes_qs)
        RequestConfig(request).configure(nodes_table)

        # OSDs in this cluster
        osds_qs = instance.osds.prefetch_related("device__rack", "device__site", "tags")
        osds_table = CephOSDTable(osds_qs, orderable=True)
        osds_table.configure(request)

        return {
            "nodes_table": nodes_table,
            "osds_table": osds_table,
        }


@register_model_view(CephCluster, "list", path="")
class CephClusterListView(generic.ObjectListView):
    queryset = CephCluster.objects.prefetch_related("tags")
    table = CephClusterTable
    filterset = CephClusterFilterSet
    filterset_form = CephClusterFilterForm


@register_model_view(CephCluster, "add")
@register_model_view(CephCluster, "edit")
class CephClusterEditView(generic.ObjectEditView):
    queryset = CephCluster.objects.all()
    form = CephClusterForm


@register_model_view(CephCluster, "delete")
class CephClusterDeleteView(generic.ObjectDeleteView):
    queryset = CephCluster.objects.all()


@register_model_view(CephCluster, "bulk_delete")
class CephClusterBulkDeleteView(generic.BulkDeleteView):
    queryset = CephCluster.objects.all()
    filterset = CephClusterFilterSet
    table = CephClusterTable


@register_model_view(CephCluster, "import")
class CephClusterImportView(generic.BulkImportView):
    queryset = CephCluster.objects.all()
    model_form = CephClusterImportForm


# ─── CephOSD ──────────────────────────────────────────────────────────────────

@register_model_view(CephOSD)
class CephOSDView(generic.ObjectView):
    queryset = CephOSD.objects.prefetch_related("cluster", "device__rack", "device__site", "tags")

    def get_extra_context(self, request, instance):
        notes_table = CephOSDStatusNoteTable(
            instance.status_notes.prefetch_related("tags"),
            orderable=False,
        )
        notes_table.configure(request)
        return {"notes_table": notes_table}


@register_model_view(CephOSD, "list", path="")
class CephOSDListView(generic.ObjectListView):
    queryset = CephOSD.objects.prefetch_related("cluster", "device__rack", "device__site", "tags")
    table = CephOSDTable
    filterset = CephOSDFilterSet
    filterset_form = CephOSDFilterForm


@register_model_view(CephOSD, "add")
@register_model_view(CephOSD, "edit")
class CephOSDEditView(generic.ObjectEditView):
    queryset = CephOSD.objects.all()
    form = CephOSDForm


@register_model_view(CephOSD, "delete")
class CephOSDDeleteView(generic.ObjectDeleteView):
    queryset = CephOSD.objects.all()


@register_model_view(CephOSD, "bulk_edit")
class CephOSDBulkEditView(generic.BulkEditView):
    queryset = CephOSD.objects.prefetch_related("tags")
    filterset = CephOSDFilterSet
    table = CephOSDTable
    form = CephOSDBulkEditForm


@register_model_view(CephOSD, "bulk_delete")
class CephOSDBulkDeleteView(generic.BulkDeleteView):
    queryset = CephOSD.objects.all()
    filterset = CephOSDFilterSet
    table = CephOSDTable


@register_model_view(CephOSD, "import")
class CephOSDImportView(generic.BulkImportView):
    queryset = CephOSD.objects.all()
    model_form = CephOSDImportForm


# ─── CephOSDStatusNote ────────────────────────────────────────────────────────

@register_model_view(CephOSDStatusNote)
class CephOSDStatusNoteView(generic.ObjectView):
    queryset = CephOSDStatusNote.objects.prefetch_related("osd", "tags")


@register_model_view(CephOSDStatusNote, "list", path="")
class CephOSDStatusNoteListView(generic.ObjectListView):
    queryset = CephOSDStatusNote.objects.prefetch_related("osd", "tags")
    table = CephOSDStatusNoteTable
    filterset = CephOSDStatusNoteFilterSet
    filterset_form = CephOSDStatusNoteFilterForm


@register_model_view(CephOSDStatusNote, "add")
@register_model_view(CephOSDStatusNote, "edit")
class CephOSDStatusNoteEditView(generic.ObjectEditView):
    queryset = CephOSDStatusNote.objects.all()
    form = CephOSDStatusNoteForm


@register_model_view(CephOSDStatusNote, "delete")
class CephOSDStatusNoteDeleteView(generic.ObjectDeleteView):
    queryset = CephOSDStatusNote.objects.all()


@register_model_view(CephOSDStatusNote, "bulk_delete")
class CephOSDStatusNoteBulkDeleteView(generic.BulkDeleteView):
    queryset = CephOSDStatusNote.objects.all()
    filterset = CephOSDStatusNoteFilterSet
    table = CephOSDStatusNoteTable


@register_model_view(CephOSDStatusNote, "import")
class CephOSDStatusNoteImportView(generic.BulkImportView):
    queryset = CephOSDStatusNote.objects.all()
    model_form = CephOSDStatusNoteImportForm
