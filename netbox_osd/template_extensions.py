from netbox.plugins import PluginTemplateExtension

from .models import CephOSD
from .tables import CephOSDTable


class DeviceCephOSDPanel(PluginTemplateExtension):
    """Adds a Ceph OSDs panel to the Device detail page."""

    models = ["dcim.device"]

    def full_width_page(self):
        device = self.context["object"]
        osds = CephOSD.objects.filter(device=device).prefetch_related("tags")
        table = CephOSDTable(osds, orderable=False)
        table.configure(self.context["request"])

        return self.render(
            "netbox_osd/inc/device_osd_panel.html",
            extra_context={
                "osds_table": table,
                "device": device,
            },
        )


template_extensions = [DeviceCephOSDPanel]
