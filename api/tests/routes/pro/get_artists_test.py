import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.users.factories as users_factories
from pcapi import settings
from pcapi.core import testing


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @pytest.mark.features(WIP_OFFER_ARTISTS=True)
    def when_user_has_rights_on_managing_offerer(self, client):
        artist1 = artist_factories.ArtistFactory(name="name-1")
        artist2 = artist_factories.ArtistFactory(name="name-2", mediation_uuid="uuid-2")

        pro = users_factories.ProFactory()

        auth_client = client.with_session_auth(pro.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        # select artists
        num_queries += 1
        with testing.assert_num_queries(num_queries):
            response = auth_client.get("/artists?search=name")
            assert response.status_code == 200

        assert {
            "id": artist1.id,
            "name": artist1.name,
            "thumbUrl": None,
        } in response.json
        assert {
            "id": artist2.id,
            "name": artist2.name,
            "thumbUrl": f"{settings.GCP_BUCKET_NAME}/{settings.ARTIST_THUMBS_FOLDER_NAME}/{artist2.mediation_uuid}",
        } in response.json
