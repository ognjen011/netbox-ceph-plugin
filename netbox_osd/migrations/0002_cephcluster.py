import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_osd", "0001_initial"),
        ("extras", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CephCluster",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
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
                "verbose_name": "Ceph Cluster",
                "verbose_name_plural": "Ceph Clusters",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="cephosd",
            name="cluster",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="osds",
                to="netbox_osd.cephcluster",
                help_text="Ceph cluster this OSD belongs to",
            ),
        ),
    ]
