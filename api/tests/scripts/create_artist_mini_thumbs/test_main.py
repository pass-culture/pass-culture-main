from unittest import mock

import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.scripts.create_artist_mini_thumbs.main import main


FAKE_IMAGE_BYTES = b"fake-image"


@pytest.mark.usefixtures("db_session")
class CreateArtistMiniThumbsTest:
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_creates_mini_thumb_for_artist_with_mediation_uuid(
        self, mock_list_files, mock_get_public_object, mock_store_mini_thumb
    ):
        artist = artist_factories.ArtistFactory(mediation_uuid="some-uuid", computed_image=None)
        mock_list_files.return_value = []
        mock_get_public_object.return_value = [FAKE_IMAGE_BYTES]

        main(not_dry=True)

        mock_get_public_object.assert_called_once_with(folder="thumbs/artist", object_id="some-uuid")
        mock_store_mini_thumb.assert_called_once_with(FAKE_IMAGE_BYTES, artist.mediation_uuid)

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_creates_mini_thumb_for_artist_with_computed_image(
        self, mock_list_files, mock_get_public_object, mock_store_mini_thumb
    ):
        artist_factories.ArtistFactory(
            mediation_uuid=None,
            computed_image="http://localhost/storage/thumbs/some-object-id",
        )
        mock_list_files.return_value = []
        mock_get_public_object.return_value = [FAKE_IMAGE_BYTES]

        main(not_dry=True)

        mock_get_public_object.assert_called_once_with(folder="thumbs", object_id="some-object-id")
        mock_store_mini_thumb.assert_called_once_with(FAKE_IMAGE_BYTES, "some-object-id")

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_skips_artist_that_already_has_mini_thumb(
        self, mock_list_files, mock_get_public_object, mock_store_mini_thumb
    ):
        artist_factories.ArtistFactory(mediation_uuid="already-done-uuid", computed_image=None)
        mock_list_files.return_value = ["thumbs/artist/72x72/already-done-uuid"]

        main(not_dry=True)

        mock_get_public_object.assert_not_called()
        mock_store_mini_thumb.assert_not_called()

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_skips_artist_without_wikidata_id(self, mock_list_files, mock_get_public_object, mock_store_mini_thumb):
        artist_factories.ArtistFactory(mediation_uuid="some-uuid", computed_image=None, wikidata_id=None)
        mock_list_files.return_value = []

        main(not_dry=True)

        mock_get_public_object.assert_not_called()
        mock_store_mini_thumb.assert_not_called()

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_dry_run_does_not_store(self, mock_list_files, mock_get_public_object, mock_store_mini_thumb):
        artist_factories.ArtistFactory(mediation_uuid="some-uuid", computed_image=None)
        mock_list_files.return_value = []
        mock_get_public_object.return_value = [FAKE_IMAGE_BYTES]

        main(not_dry=False)

        mock_store_mini_thumb.assert_not_called()

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_continues_on_error(self, mock_list_files, mock_get_public_object, mock_store_mini_thumb, caplog):
        artist_factories.ArtistFactory(mediation_uuid="failing-uuid", computed_image=None)
        artist_factories.ArtistFactory(mediation_uuid="good-uuid", computed_image=None)
        mock_list_files.return_value = []
        mock_get_public_object.side_effect = [Exception("storage error"), [FAKE_IMAGE_BYTES]]

        main(not_dry=True)

        assert mock_store_mini_thumb.call_count == 1
        assert "Error processing artist" in caplog.text

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_skips_artist_with_no_image_at_all(self, mock_list_files, mock_get_public_object, mock_store_mini_thumb):
        artist_factories.ArtistFactory(mediation_uuid=None, computed_image=None)
        mock_list_files.return_value = []

        main(not_dry=True)

        mock_get_public_object.assert_not_called()
        mock_store_mini_thumb.assert_not_called()
