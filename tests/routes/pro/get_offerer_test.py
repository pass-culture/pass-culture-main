import pytest

from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Get:
    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_user_offerer_does_not_exist(self, app):
            # Given
            user = create_user()
            repository.save(user)
            invalid_id = 12

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get("/offerers/%s" % invalid_id)

            # then
            assert response.status_code == 404
            assert response.json["global"] == ["La page que vous recherchez n'existe pas"]

    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_user_has_rights_on_offerer(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            create_bank_information(venue=venue)
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer, venue)
            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(f"/offerers/{humanize(offerer.id)}")

            # then
            assert response.status_code == 200
            response_json = response.json
            assert "bic" in response_json["managedVenues"][0]
            assert "iban" in response_json["managedVenues"][0]
            assert response_json["userHasAccess"] is True
