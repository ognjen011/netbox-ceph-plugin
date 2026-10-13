from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("netbox_osd", "0004_cephosd_storage_properties")]

    operations = [
        migrations.AddField(
            model_name="cephcluster", name="kubernetes_cluster",
            field=models.CharField(
                max_length=253, blank=True,
                help_text="Name of the Kubernetes cluster hosting this Ceph deployment, if applicable",
            ),
        ),
        migrations.AddField(
            model_name="cephcluster", name="kubernetes_namespace",
            field=models.CharField(
                max_length=63, blank=True,
                help_text="Kubernetes namespace containing the Ceph deployment, e.g. rook-ceph",
            ),
        ),
    ]
