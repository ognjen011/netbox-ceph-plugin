from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import views
from .models import CephCluster, CephOSD, CephOSDStatusNote

urlpatterns = [
    # ── CephCluster ───────────────────────────────────────────────────────────
    path("clusters/", views.CephClusterListView.as_view(), name="cephcluster_list"),
    path("clusters/add/", views.CephClusterEditView.as_view(), name="cephcluster_add"),
    path("clusters/import/", views.CephClusterImportView.as_view(), name="cephcluster_import"),
    path("clusters/delete/", views.CephClusterBulkDeleteView.as_view(), name="cephcluster_bulk_delete"),
    path("clusters/<int:pk>/", views.CephClusterView.as_view(), name="cephcluster"),
    path("clusters/<int:pk>/edit/", views.CephClusterEditView.as_view(), name="cephcluster_edit"),
    path("clusters/<int:pk>/delete/", views.CephClusterDeleteView.as_view(), name="cephcluster_delete"),
    path(
        "clusters/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="cephcluster_changelog",
        kwargs={"model": CephCluster},
    ),

    # ── CephOSD ───────────────────────────────────────────────────────────────
    path("osds/", views.CephOSDListView.as_view(), name="cephosd_list"),
    path("osds/add/", views.CephOSDEditView.as_view(), name="cephosd_add"),
    path("osds/import/", views.CephOSDImportView.as_view(), name="cephosd_import"),
    path("osds/delete/", views.CephOSDBulkDeleteView.as_view(), name="cephosd_bulk_delete"),
    path("osds/edit/", views.CephOSDBulkEditView.as_view(), name="cephosd_bulk_edit"),
    path("osds/<int:pk>/", views.CephOSDView.as_view(), name="cephosd"),
    path("osds/<int:pk>/edit/", views.CephOSDEditView.as_view(), name="cephosd_edit"),
    path("osds/<int:pk>/delete/", views.CephOSDDeleteView.as_view(), name="cephosd_delete"),
    path(
        "osds/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="cephosd_changelog",
        kwargs={"model": CephOSD},
    ),

    # ── CephOSDStatusNote ─────────────────────────────────────────────────────
    path("notes/", views.CephOSDStatusNoteListView.as_view(), name="cephosdsstatusnote_list"),
    path("notes/add/", views.CephOSDStatusNoteEditView.as_view(), name="cephosdsstatusnote_add"),
    path("notes/import/", views.CephOSDStatusNoteImportView.as_view(), name="cephosdsstatusnote_import"),
    path("notes/delete/", views.CephOSDStatusNoteBulkDeleteView.as_view(), name="cephosdsstatusnote_bulk_delete"),
    path("notes/<int:pk>/", views.CephOSDStatusNoteView.as_view(), name="cephosdsstatusnote"),
    path("notes/<int:pk>/edit/", views.CephOSDStatusNoteEditView.as_view(), name="cephosdsstatusnote_edit"),
    path("notes/<int:pk>/delete/", views.CephOSDStatusNoteDeleteView.as_view(), name="cephosdsstatusnote_delete"),
    path(
        "notes/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="cephosdsstatusnote_changelog",
        kwargs={"model": CephOSDStatusNote},
    ),
]
