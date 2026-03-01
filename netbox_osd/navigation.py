from netbox.plugins.navigation import PluginMenu, PluginMenuButton, PluginMenuItem


menu = PluginMenu(
    label="Ceph",
    groups=(
        (
            "Clusters",
            (
                PluginMenuItem(
                    link="plugins:netbox_osd:cephcluster_list",
                    link_text="Clusters",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_osd:cephcluster_add",
                            title="Add Cluster",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
            ),
        ),
        (
            "OSDs",
            (
                PluginMenuItem(
                    link="plugins:netbox_osd:cephosd_list",
                    link_text="OSDs",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_osd:cephosd_add",
                            title="Add OSD",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
                PluginMenuItem(
                    link="plugins:netbox_osd:cephosdsstatusnote_list",
                    link_text="Status Notes",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_osd:cephosdsstatusnote_add",
                            title="Add Note",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
            ),
        ),
    ),
    icon_class="mdi mdi-database",
)
