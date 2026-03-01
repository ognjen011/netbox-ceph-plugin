import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0001_initial"),
        ("netbox_osd", "0002_cephcluster"),
    ]

    operations = [
        migrations.AddField(
            model_name="cephcluster",
            name="site",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="ceph_clusters",
                to="dcim.site",
                help_text="Datacenter (site) where this cluster resides",
            ),
        ),
    ]
