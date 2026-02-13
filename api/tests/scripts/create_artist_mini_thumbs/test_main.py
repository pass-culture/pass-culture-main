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
        artist = artist_factories.ArtistFactory(mediation_uuid="some-uuid")
        mock_list_files.return_value = []
        mock_get_public_object.return_value = [FAKE_IMAGE_BYTES]

        main(not_dry=True)

        mock_get_public_object.assert_called_once_with(folder="thumbs/artist", object_id="some-uuid")
        mock_store_mini_thumb.assert_called_once_with(FAKE_IMAGE_BYTES, artist.mediation_uuid)

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_skips_artist_that_already_has_mini_thumb(
        self, mock_list_files, mock_get_public_object, mock_store_mini_thumb
    ):
        artist_factories.ArtistFactory(mediation_uuid="already-done-uuid")
        mock_list_files.return_value = ["thumbs/artist/72x72/already-done-uuid"]

        main(not_dry=True)

        mock_get_public_object.assert_not_called()
        mock_store_mini_thumb.assert_not_called()

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_skips_artist_without_mediation_uuid(self, mock_list_files, mock_get_public_object, mock_store_mini_thumb):
        artist_factories.ArtistFactory(mediation_uuid=None)
        mock_list_files.return_value = []

        main(not_dry=True)

        mock_get_public_object.assert_not_called()
        mock_store_mini_thumb.assert_not_called()

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_dry_run_does_not_store(self, mock_list_files, mock_get_public_object, mock_store_mini_thumb):
        artist_factories.ArtistFactory(mediation_uuid="some-uuid")
        mock_list_files.return_value = []
        mock_get_public_object.return_value = [FAKE_IMAGE_BYTES]

        main(not_dry=False)

        mock_store_mini_thumb.assert_not_called()

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_limit_restricts_number_of_artists_processed(
        self, mock_list_files, mock_get_public_object, mock_store_mini_thumb
    ):
        artist_factories.ArtistFactory(mediation_uuid="uuid-1")
        artist_factories.ArtistFactory(mediation_uuid="uuid-2")
        artist_factories.ArtistFactory(mediation_uuid="uuid-3")
        mock_list_files.return_value = []
        mock_get_public_object.return_value = [FAKE_IMAGE_BYTES]

        main(not_dry=True, limit=1)

        assert mock_store_mini_thumb.call_count == 1

    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.artist_api.store_mini_thumb")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.get_public_object")
    @mock.patch("pcapi.scripts.create_artist_mini_thumbs.main.object_storage.list_files")
    def test_offset_skips_artists(self, mock_list_files, mock_get_public_object, mock_store_mini_thumb):
        artist_factories.ArtistFactory(mediation_uuid="uuid-1")
        artist_factories.ArtistFactory(mediation_uuid="uuid-2")
        artist_factories.ArtistFactory(mediation_uuid="uuid-3")
        mock_list_files.return_value = []
        mock_get_public_object.return_value = [FAKE_IMAGE_BYTES]

        main(not_dry=True, offset=1)

        assert mock_store_mini_thumb.call_count == 2
