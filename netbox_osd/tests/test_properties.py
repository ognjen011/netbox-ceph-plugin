from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.test import TestCase, override_settings
from django.urls import reverse
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site

from netbox_osd.forms import (
    CephClusterForm, CephClusterImportForm, CephOSDForm, CephOSDImportForm,
)
from netbox_osd.models import CephCluster, CephOSD, CephOSDStatusNote


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class PropertiesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Ceph property tests", slug="ceph-property-tests")
        role = DeviceRole.objects.create(name="Ceph property tests", slug="ceph-property-tests")
        manufacturer = Manufacturer.objects.create(name="Ceph property tests", slug="ceph-property-tests")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Ceph property tests", slug="ceph-property-tests",
        )
        cls.device = Device.objects.create(
            name="ceph-property-tests", site=site, role=role, device_type=device_type,
        )
        cls.other_device = Device.objects.create(
            name="ceph-property-tests-other", site=site, role=role, device_type=device_type,
        )
        cls.cluster = CephCluster.objects.create(name="ceph-property-tests")
        cls.user = get_user_model().objects.create_superuser(
            username="ceph-property-tests", password="test-only-password",
        )

    def setUp(self):
        self.client.force_login(self.user)

    @staticmethod
    def storage_data():
        return {
            "disk_path": "/dev/disk/by-id/nvme-test-drive",
            "serial_number": "NVME-TEST-01",
            "capacity_bytes": 3840000000000,
            "osd_uuid": "88ab9018-f84b-4d62-90b4-ce7c076728ff",
            "db_path": "/dev/mapper/ceph-db",
            "wal_path": "/dev/mapper/ceph-wal",
        }

    def test_osd_api_create_update_and_clear_storage(self):
        data = {
            "name": "osd.42", "device": self.device.pk,
            "cluster": self.cluster.pk, **self.storage_data(),
        }
        response = self.client.post("/api/plugins/osd/osds/", data, content_type="application/json")
        self.assertEqual(response.status_code, 201, response.content)
        for field, value in self.storage_data().items():
            self.assertEqual(response.json()[field], value)
        obj = CephOSD.objects.get(pk=response.json()["id"])
        self.assertEqual(obj.capacity_bytes, 3840000000000)
        self.assertEqual(obj.osd_uuid, UUID(data["osd_uuid"]))
        path = f"/api/plugins/osd/osds/{obj.pk}/"
        response = self.client.patch(path, {"serial_number": "UPDATED"}, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["serial_number"], "UPDATED")
        self.assertEqual(response.json()["disk_path"], data["disk_path"])
        empty = {"disk_path": "", "serial_number": "", "capacity_bytes": None,
                 "osd_uuid": None, "db_path": "", "wal_path": ""}
        response = self.client.patch(path, empty, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        for field, value in empty.items():
            self.assertEqual(response.json()[field], value)

    def test_osd_api_accepts_legacy_payload_and_rejects_invalid_values(self):
        data = {"name": "osd.42", "device": self.device.pk}
        response = self.client.post("/api/plugins/osd/osds/", data, content_type="application/json")
        self.assertEqual(response.status_code, 201, response.content)
        self.assertIsNone(response.json()["capacity_bytes"])
        self.assertIsNone(response.json()["osd_uuid"])
        path = f'/api/plugins/osd/osds/{response.json()["id"]}/'
        for invalid in ({"capacity_bytes": -1}, {"capacity_bytes": 0}, {"osd_uuid": "invalid"}):
            with self.subTest(invalid=invalid):
                response = self.client.patch(
                    path, invalid, content_type="application/json",
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(next(iter(invalid)), response.json())

    def test_osd_edit_and_csv_forms(self):
        common = {
            "name": "osd.42", "device": self.device.pk, "cluster": self.cluster.pk,
            "osd_type": "nvme", "status": "active", "encrypted": True,
            **self.storage_data(),
        }
        form = CephOSDForm(data=common)
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.osd_uuid, UUID(common["osd_uuid"]))
        csv_data = {**common, "name": "osd.43", "device": self.device.name,
                    "cluster": self.cluster.name}
        form = CephOSDImportForm(data=csv_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().capacity_bytes, common["capacity_bytes"])
        for field in self.storage_data():
            csv_data.pop(field)
        csv_data["name"] = "osd.44"
        form = CephOSDImportForm(data=csv_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.save().osd_uuid)

    def test_model_capacity_validation(self):
        for capacity in (-1, 0):
            with self.subTest(capacity=capacity):
                obj = CephOSD(name="osd.42", device=self.device, capacity_bytes=capacity)
                with self.assertRaises(ValidationError):
                    obj.full_clean()

    def test_migrations_match_new_model_fields(self):
        apps = MigrationLoader(connection).project_state().apps
        fields_by_model = {
            CephOSD: tuple(self.storage_data()),
            CephCluster: ("kubernetes_cluster", "kubernetes_namespace"),
        }
        for model, fields in fields_by_model.items():
            migrated = apps.get_model("netbox_osd", model.__name__)
            for field in fields:
                with self.subTest(model=model.__name__, field=field):
                    self.assertEqual(
                        model._meta.get_field(field).deconstruct(),
                        migrated._meta.get_field(field).deconstruct(),
                    )

    def test_cluster_api_deployment_create_update_clear_and_filter(self):
        data = {"name": "rook-property-tests", "kubernetes_cluster": "production-k8s",
                "kubernetes_namespace": "rook-ceph"}
        response = self.client.post("/api/plugins/osd/clusters/", data, content_type="application/json")
        self.assertEqual(response.status_code, 201, response.content)
        obj = CephCluster.objects.get(pk=response.json()["id"])
        for field, value in data.items():
            self.assertEqual(response.json()[field], value)
        filtered = self.client.get("/api/plugins/osd/clusters/", {"kubernetes_cluster": "production-k8s"})
        self.assertEqual(filtered.status_code, 200, filtered.content)
        self.assertEqual([item["id"] for item in filtered.json()["results"]], [obj.pk])
        path = f"/api/plugins/osd/clusters/{obj.pk}/"
        response = self.client.patch(path, {"kubernetes_namespace": "storage"}, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["kubernetes_namespace"], "storage")
        response = self.client.patch(
            path, {"kubernetes_cluster": "", "kubernetes_namespace": ""}, content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["kubernetes_cluster"], "")

    def test_cluster_forms_and_legacy_import(self):
        data = {"name": "rook-property-tests", "kubernetes_cluster": "production-k8s",
                "kubernetes_namespace": "rook-ceph"}
        form = CephClusterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().kubernetes_cluster, "production-k8s")
        data["name"] = "rook-property-tests-import"
        form = CephClusterImportForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().kubernetes_namespace, "rook-ceph")
        form = CephClusterImportForm(data={"name": "legacy-property-tests"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().kubernetes_cluster, "")

    def test_details_notes_and_device_tab_render(self):
        self.cluster.kubernetes_cluster = "production-k8s"
        self.cluster.kubernetes_namespace = "rook-ceph"
        self.cluster.save()
        osd = CephOSD.objects.create(
            name="osd.42", device=self.device, cluster=self.cluster, **self.storage_data(),
        )
        CephOSD.objects.create(name="osd.43", device=self.other_device)
        note = CephOSDStatusNote.objects.create(osd=osd, status="down", reason="Test note")
        response = self.client.get(osd.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        for value in ("NVME-TEST-01", "/dev/disk/by-id/nvme-test-drive", "3840000000000 bytes",
                      "/dev/mapper/ceph-db", "/dev/mapper/ceph-wal", str(osd.osd_uuid)):
            self.assertContains(response, value)
        self.assertEqual(self.client.get(note.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get("/plugins/osd/notes/").status_code, 200)
        response = self.client.get(self.cluster.get_absolute_url())
        self.assertContains(response, "production-k8s")
        self.assertContains(response, "rook-ceph")
        path = reverse("dcim:device_ceph_osds", kwargs={"pk": self.device.pk})
        response = self.client.get(path)
        self.assertContains(response, "osd.42")
        self.assertNotContains(response, "osd.43")
