import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Get:
    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_user_offerer_does_not_exist(self, app):
            # Given
            pro = users_factories.UserFactory(isBeneficiary=False)
            invalid_id = 12

            # When
            response = TestClient(app.test_client()).with_auth(pro.email).get("/offerers/%s" % invalid_id)

            # then
            assert response.status_code == 404
            assert response.json["global"] == ["La page que vous recherchez n'existe pas"]

    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_user_has_rights_on_offerer(self, app):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False)
            venue = offers_factories.VenueFactory()
            offers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)

            create_bank_information(venue=venue)

            # when
            response = (
                TestClient(app.test_client())
                .with_auth(pro.email)
                .get(f"/offerers/{humanize(venue.managingOfferer.id)}")
            )

            # then
            assert response.status_code == 200
            response_json = response.json
            assert "bic" in response_json["managedVenues"][0]
            assert "iban" in response_json["managedVenues"][0]
