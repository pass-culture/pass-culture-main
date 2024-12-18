from unittest import mock

import pytest

from pcapi.core.artist import commands
from pcapi.core.artist.models import Artist

from . import fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class ImportAllArtistsTest:
    @mock.patch("pcapi.core.artist.commands.get_all_artists")
    def test_import_all_artists(
        self,
        get_all_artists_mock,
    ):
        get_all_artists_mock.return_value = fixtures.big_query_artist_fixture

        commands.import_all_artists()

        get_all_artists_mock.assert_called_once()

        all_artists = Artist.query.all()
        assert len(all_artists) == 2
