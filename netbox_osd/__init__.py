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


config = NetBoxOSDConfig
