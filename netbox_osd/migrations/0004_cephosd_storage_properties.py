from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("netbox_osd", "0003_cephcluster_site")]

    operations = [
        migrations.AddField(
            model_name="cephosd", name="disk_path",
            field=models.CharField(
                max_length=255, blank=True,
                help_text="Data device path, preferably a stable /dev/disk/by-id/ path",
            ),
        ),
        migrations.AddField(
            model_name="cephosd", name="serial_number",
            field=models.CharField(
                max_length=100, blank=True,
                help_text="Serial number of the physical data drive",
            ),
        ),
        migrations.AddField(
            model_name="cephosd", name="capacity_bytes",
            field=models.PositiveBigIntegerField(
                null=True, blank=True, validators=[MinValueValidator(1)],
                verbose_name="Capacity (bytes)",
                help_text="Data device capacity in bytes; leave blank if unknown",
            ),
        ),
        migrations.AddField(
            model_name="cephosd", name="osd_uuid",
            field=models.UUIDField(
                null=True, blank=True, verbose_name="OSD UUID",
                help_text="Ceph OSD FSID (not the cluster FSID)",
            ),
        ),
        migrations.AddField(
            model_name="cephosd", name="db_path",
            field=models.CharField(
                max_length=255, blank=True, verbose_name="DB device path",
                help_text="Separate BlueStore block.db device or logical volume, if configured",
            ),
        ),
        migrations.AddField(
            model_name="cephosd", name="wal_path",
            field=models.CharField(
                max_length=255, blank=True, verbose_name="WAL device path",
                help_text="Separate BlueStore block.wal device or logical volume, if configured",
            ),
        ),
    ]
