from unittest import mock

import pytest

from pcapi.core.external import subcategory_suggestion
from pcapi.core.external.subcategory_suggestion_backends import fixtures
from pcapi.core.external.subcategory_suggestion_backends.subcategory_suggestion import SubcategorySuggestionBackend
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class GetMostProbableSubcategoryIdsTest:
    def test_get_most_probable_subcategory_ids_and_call_id(self):
        call_id, category_ids = subcategory_suggestion.get_most_probable_subcategory_ids("Madame Bovary")
        assert category_ids[0] == "LIVRE_PAPIER"
        assert category_ids[1] == "SPECTACLE_REPRESENTATION"
        assert category_ids[2] == "ABO_PLATEFORME_VIDEO"
        assert call_id == "123e4567-e89b-12d3-a456-426614174123"

    @mock.patch(
        "pcapi.core.external.subcategory_suggestion.subcategory_suggestion_backend", SubcategorySuggestionBackend()
    )
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_get_most_probable_subcategory_ids_and_call_id_api_mock(self, mock_get_id_token_from_google, requests_mock):
        requests_mock.post(
            "https://compliance.passculture.team/latest/model/categorisation",
            json=fixtures.SUBCATEGORY_SUGGESTION_MUSEE_RESULT,
        )
        offerer = offerers_factories.OffererFactory(name="Gestionnaire de plein de musées")
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer, name="Le Musée des trucs", venueTypeCode="MUSEUM"
        )
        offer_name = "Une visite au musée"
        offer_description = "C'est quand même mieux que de s'ennuyer"

        call_id, category_ids = subcategory_suggestion.get_most_probable_subcategory_ids(
            offer_name, offer_description, venue.id
        )
        assert category_ids[0] == "VISITE_GUIDEE"
        assert category_ids[1] == "VISITE"
        assert category_ids[2] == "EVENEMENT_PATRIMOINE"
        assert call_id == "123e4567-e89b-12d3-a456-426614174000"
