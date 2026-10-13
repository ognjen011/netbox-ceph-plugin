from netbox.plugins import PluginConfig


class NetBoxOSDConfig(PluginConfig):
    name = "netbox_osd"
    verbose_name = "Ceph OSD Tracker"
    description = "Track Ceph OSDs, their hosts, racks, types, and status history"
    version = "0.1.0"
    author = "Ognjen"
    base_url = "osd"
    min_version = "4.0.0"
    default_settings = {}

    def ready(self):
        super().ready()
        # Register the Device tab before NetBox builds its core URL patterns.
        from . import views  # noqa: F401


config = NetBoxOSDConfig
