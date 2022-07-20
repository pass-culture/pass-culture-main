from unittest.mock import MagicMock
from unittest.mock import patch

from google.cloud.exceptions import NotFound
import pytest

from pcapi.core.object_storage import BACKENDS_MAPPING
from pcapi.core.object_storage import _check_backend_setting
from pcapi.core.object_storage import _check_backends_module_paths
from pcapi.core.object_storage import delete_public_object
from pcapi.core.object_storage import store_public_object
from pcapi.core.offers.models import Mediation
from pcapi.core.testing import override_settings
from pcapi.models.product import Product


class StorePublicObjectTest:
    @override_settings(OBJECT_STORAGE_PROVIDER="local")
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.store_public_object")
    def test_local_backend_call(self, mock_local_store_public_object):
        store_public_object("bucket", "object_id", b"mouette", "image/jpeg")
        mock_local_store_public_object.assert_called_once_with("bucket", "object_id", b"mouette", "image/jpeg")

    @override_settings(OBJECT_STORAGE_PROVIDER="OVH")
    @patch("pcapi.core.object_storage.backends.ovh.OVHBackend.store_public_object")
    def test_ovh_backend_call(self, mock_ovh_store_public_object):
        store_public_object("bucket", "object_id", b"mouette", "image/jpeg")
        mock_ovh_store_public_object.assert_called_once_with("bucket", "object_id", b"mouette", "image/jpeg")

    @override_settings(OBJECT_STORAGE_PROVIDER="GCP")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    def test_gcp_backend_call(self, mock_gcp_store_public_object):
        store_public_object("bucket", "object_id", b"mouette", "image/jpeg")
        mock_gcp_store_public_object.assert_called_once_with("bucket", "object_id", b"mouette", "image/jpeg")

    @override_settings(OBJECT_STORAGE_PROVIDER="OVH,GCP")
    @patch("pcapi.core.object_storage.backends.ovh.OVHBackend.store_public_object")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    def test_ovh_gcp_backends_call(self, mock_gcp_store_public_object, mock_ovh_store_public_object):
        store_public_object("bucket", "object_id", b"mouette", "image/jpeg")
        mock_ovh_store_public_object.assert_called_once_with("bucket", "object_id", b"mouette", "image/jpeg")
        mock_gcp_store_public_object.assert_called_once_with("bucket", "object_id", b"mouette", "image/jpeg")


class CheckBackendSettingTest:
    @override_settings(OBJECT_STORAGE_PROVIDER="")
    def test_empty_setting(self):
        with pytest.raises(RuntimeError):
            _check_backend_setting()

    @override_settings(OBJECT_STORAGE_PROVIDER="OVH")
    def test_correct_setting(self):
        _check_backend_setting()

    @override_settings(OBJECT_STORAGE_PROVIDER="local, GCP")
    def test_correct_multi_values(self):
        _check_backend_setting()

    @override_settings(OBJECT_STORAGE_PROVIDER="AWS")
    def test_unknown_backend(self):
        with pytest.raises(RuntimeError):
            _check_backend_setting()


class CheckBackendsModulePathsTest:
    @pytest.fixture()
    def wrong_backend_path(self):
        BACKENDS_MAPPING["some_backend"] = "pcapi.some_dir.SomeBackend"
        yield BACKENDS_MAPPING
        BACKENDS_MAPPING.pop("some_backend")

    def test_wrong_path(self, wrong_backend_path):
        with pytest.raises(ModuleNotFoundError):
            _check_backends_module_paths()


class DeletePublicObjectTest:
    @override_settings(OBJECT_STORAGE_PROVIDER="local")
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    def test_local_backend_call(self, mock_local_delete_public_object):
        delete_public_object("bucket", "object_id")
        mock_local_delete_public_object.assert_called_once_with("bucket", "object_id")

    @override_settings(OBJECT_STORAGE_PROVIDER="OVH")
    @patch("pcapi.core.object_storage.backends.ovh.OVHBackend.delete_public_object")
    def test_ovh_backend_call(self, mock_ovh_delete_public_object):
        delete_public_object("bucket", "object_id")
        mock_ovh_delete_public_object.assert_called_once_with("bucket", "object_id")

    @override_settings(OBJECT_STORAGE_PROVIDER="GCP")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.delete_public_object")
    def test_gcp_backend_call(self, mock_gcp_delete_public_object):
        delete_public_object("bucket", "object_id")
        mock_gcp_delete_public_object.assert_called_once_with("bucket", "object_id")

    @override_settings(OBJECT_STORAGE_PROVIDER="GCP")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.get_gcp_storage_client_bucket")
    def test_gcp_backend_call_when_gcp_return_return_not_found_error_not_raises_exception(
        self, mocked_get_gcp_storage_client_bucket
    ):
        mocked_bucket = MagicMock()
        gcp_cloud_blob = MagicMock()
        gcp_cloud_blob.delete.side_effect = NotFound(
            "DELETE storage/v1/o/thumbs%2Fmediations%object_id?prettyPrint=false: No such object: thumbs/mediations/object_id"
        )
        mocked_bucket.blob.return_value = gcp_cloud_blob
        mocked_get_gcp_storage_client_bucket.return_value = mocked_bucket

        try:
            delete_public_object("bucket", "object_id")
        except NotFound as exc:
            assert False, f"'delete_public_object' raised an exception {exc}"

    @override_settings(OBJECT_STORAGE_PROVIDER="OVH,GCP")
    @patch("pcapi.core.object_storage.backends.ovh.OVHBackend.delete_public_object")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.delete_public_object")
    def test_ovh_gcp_backends_call(self, mock_gcp_delete_public_object, mock_ovh_delete_public_object):
        delete_public_object("bucket", "object_id")
        mock_ovh_delete_public_object.assert_called_once_with("bucket", "object_id")
        mock_gcp_delete_public_object.assert_called_once_with("bucket", "object_id")


class GetThumbStorageIdTest:
    def test_with_mediation(self):
        obj = Mediation(id=123)
        assert obj.get_thumb_storage_id(0) == "mediations/PM"

    def test_with_product(self):
        obj = Product(id=123)
        assert obj.get_thumb_storage_id(0) == "products/PM"

    def test_with_index_above_0(self):
        obj = Product(id=123)
        assert obj.get_thumb_storage_id(3) == "products/PM_3"
