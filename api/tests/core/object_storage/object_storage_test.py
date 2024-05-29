from unittest.mock import MagicMock
from unittest.mock import patch

from google.cloud.exceptions import NotFound
import pytest

from pcapi.core.object_storage import BACKENDS_MAPPING
from pcapi.core.object_storage import _check_backend_setting
from pcapi.core.object_storage import _check_backends_module_paths
from pcapi.core.object_storage import delete_public_object
from pcapi.core.object_storage import store_public_object
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_settings


class StorePublicObjectTest:
    @override_settings(OBJECT_STORAGE_PROVIDER="local")
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.store_public_object")
    def test_local_backend_call(self, mock_local_store_public_object):
        store_public_object("folder", "object_id", b"mouette", "image/jpeg", bucket="bucket")
        mock_local_store_public_object.assert_called_once_with("folder", "object_id", b"mouette", "image/jpeg")

    @override_settings(OBJECT_STORAGE_PROVIDER="GCP")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    def test_gcp_backend_call(self, mock_gcp_store_public_object):
        store_public_object("folder", "object_id", b"mouette", "image/jpeg", bucket="bucket")
        mock_gcp_store_public_object.assert_called_once_with("folder", "object_id", b"mouette", "image/jpeg")

    @override_settings(OBJECT_STORAGE_PROVIDER="local,GCP")
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.store_public_object")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.store_public_object")
    def test_multiple_backends_call(self, mock_gcp_store_public_object, mock_local_store_public_object):
        store_public_object("folder", "object_id", b"mouette", "image/jpeg", bucket="bucket")
        mock_local_store_public_object.assert_called_once_with("folder", "object_id", b"mouette", "image/jpeg")
        mock_gcp_store_public_object.assert_called_once_with("folder", "object_id", b"mouette", "image/jpeg")


class CheckBackendSettingTest:
    @override_settings(OBJECT_STORAGE_PROVIDER="")
    def test_empty_setting(self):
        with pytest.raises(RuntimeError):
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
        delete_public_object("folder", "object_id", bucket="bucket")
        mock_local_delete_public_object.assert_called_once_with("folder", "object_id")

    @override_settings(OBJECT_STORAGE_PROVIDER="GCP")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.delete_public_object")
    def test_gcp_backend_call(self, mock_gcp_delete_public_object):
        delete_public_object("folder", "object_id", bucket="bucket")
        mock_gcp_delete_public_object.assert_called_once_with("folder", "object_id")

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
            delete_public_object("folder", "object_id", bucket="bucket")
        except NotFound as exc:
            assert False, f"'delete_public_object' raised an exception {exc}"

    @override_settings(OBJECT_STORAGE_PROVIDER="local,GCP")
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    @patch("pcapi.core.object_storage.backends.gcp.GCPBackend.delete_public_object")
    def test_multiple_backends_call(self, mock_gcp_delete_public_object, mock_local_delete_public_object):
        delete_public_object("folder", "object_id", bucket="bucket")
        mock_local_delete_public_object.assert_called_once_with("folder", "object_id")
        mock_gcp_delete_public_object.assert_called_once_with("folder", "object_id")


@pytest.mark.usefixtures("db_session")
class GetThumbStorageIdTest:
    def test_mediation(self):
        mediation = offers_factories.MediationFactory(id=123, thumbCount=1)

        assert mediation.get_thumb_storage_id() == "mediations/PM"

    def test_product(self):
        product = offers_factories.ProductFactory(id=123, thumbCount=1)

        assert product.get_thumb_storage_id() == "products/PM"

    def test_product_with_4_thumbs(self):
        product_with_4_thumbs = offers_factories.ProductFactory(id=123, thumbCount=4)

        assert product_with_4_thumbs.get_thumb_storage_id() == "products/PM_3"

    def test_venue_custom_suffix_str(self):
        venue = offerers_factories.VenueFactory(id=123, thumbCount=1)

        assert venue.get_thumb_storage_id("opposable_thumbs_22") == "venues/PM_opposable_thumbs_22"

    def test_venue_ignore_thumb_count(self):
        venue = offerers_factories.VenueFactory(id=123, thumbCount=5)

        assert venue.get_thumb_storage_id(suffix_str="", ignore_thumb_count=True) == "venues/PM"

    def test_no_thumb(self):
        product_with_no_thumb = offers_factories.ProductFactory(id=123)

        with pytest.raises(ValueError):
            product_with_no_thumb.get_thumb_storage_id()
