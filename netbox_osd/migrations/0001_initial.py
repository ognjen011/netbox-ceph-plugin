import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("dcim", "0001_initial"),  # adjust if your NetBox version differs
        ("extras", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CephOSD",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "osd_type",
                    models.CharField(
                        choices=[("hdd", "HDD"), ("ssd", "SSD"), ("nvme", "NVMe")],
                        default="hdd",
                        max_length=10,
                    ),
                ),
                ("encrypted", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("down", "Down"),
                            ("out", "Out"),
                            ("destroyed", "Destroyed"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ceph_osds",
                        to="dcim.device",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem",
                        to="extras.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ceph OSD",
                "verbose_name_plural": "Ceph OSDs",
                "ordering": ["device", "name"],
                "unique_together": {("device", "name")},
            },
        ),
        migrations.CreateModel(
            name="CephOSDStatusNote",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("down", "Down"),
                            ("out", "Out"),
                            ("maintenance", "Maintenance"),
                            ("recovered", "Recovered"),
                            ("other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                ("reason", models.TextField()),
                ("resolved", models.BooleanField(default=False)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "osd",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_notes",
                        to="netbox_osd.cephosd",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem",
                        to="extras.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "verbose_name": "OSD Status Note",
                "verbose_name_plural": "OSD Status Notes",
                "ordering": ["-created"],
            },
        ),
    ]
