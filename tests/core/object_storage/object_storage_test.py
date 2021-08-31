from unittest.mock import patch

import pytest

from pcapi.core.object_storage import BACKENDS_MAPPING
from pcapi.core.object_storage import _check_backend_setting
from pcapi.core.object_storage import _check_backends_module_paths
from pcapi.core.object_storage import build_thumb_path
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
        _check_backend_setting()

    @override_settings(OBJECT_STORAGE_PROVIDER="OVH")
    def test_correct_setting(self):
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

    @override_settings(OBJECT_STORAGE_PROVIDER="OVH,GCP")
    @patch("pcapi.core.object_storage.backends.ovh.OVHBackend.delete_public_object")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.delete_public_object")
    def test_ovh_gcp_backends_call(self, mock_gcp_delete_public_object, mock_ovh_delete_public_object):
        delete_public_object("bucket", "object_id")
        mock_ovh_delete_public_object.assert_called_once_with("bucket", "object_id")
        mock_gcp_delete_public_object.assert_called_once_with("bucket", "object_id")


class BuildThumbPathTest:
    def test_returns_path_without_sql_entity_when_given_model_is_mediation(self):
        # given
        mediation_object = Mediation()
        mediation_object.id = 123
        mediation_object.offerId = 567

        # when
        thumb_path = build_thumb_path(mediation_object, 0)

        # then
        assert thumb_path == "mediations/PM"

    def test_returns_classic_path_when_given_model_is_product(self):
        # given
        product_object = Product()
        product_object.id = 123

        # when
        thumb_path = build_thumb_path(product_object, 0)

        # then
        assert thumb_path == "products/PM"

    def test_returns_path_with_index_if_above_0(self):
        # given
        product_object = Product()
        product_object.id = 123

        # when
        thumb_path = build_thumb_path(product_object, 3)

        # then
        assert thumb_path == "products/PM_3"
