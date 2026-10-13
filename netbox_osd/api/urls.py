from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_osd-api"

router = NetBoxRouter()
router.register("clusters", views.CephClusterViewSet, basename="cephcluster")
router.register("osds", views.CephOSDViewSet, basename="cephosd")
router.register("notes", views.CephOSDStatusNoteViewSet, basename="cephosdstatusnote")

urlpatterns = router.urls
