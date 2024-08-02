from unittest import mock

import pytest

from pcapi.core import testing
from pcapi.core.external.subcategory_suggestion_backends import fixtures
from pcapi.core.external.subcategory_suggestion_backends.subcategory_suggestion import SubcategorySuggestionBackend
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_access_by_no_one(self, client):
        response = client.get("/offers/suggested-subcategories?offer_name=foo")

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.external.subcategory_suggestion.subcategory_suggestion_backend", SubcategorySuggestionBackend())
@mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
class Returns200Test:
    num_queries = 1  # user
    num_queries += 1  # venue
    num_queries += 1  # offerer

    def test_suggest_subcategories(self, mock_get_id_token_from_google, requests_mock, client):
        # Given
        pro = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()
        requests_mock.post(
            "https://compliance.passculture.team/latest/model/categorisation",
            json=fixtures.SUBCATEGORY_SUGGESTION_MUSEE_RESULT,
        )

        # When
        client = client.with_session_auth(email=pro.email)
        venue_id = venue.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(
                f"/offers/suggested-subcategories?offer_name=foo&offer_description=bar&venue_id={venue_id}"
            )

        # Then
        assert response.status_code == 200
        assert response.json == {"subcategoryIds": ["VISITE_GUIDEE", "VISITE", "EVENEMENT_PATRIMOINE"]}
