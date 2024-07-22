from unittest import mock

import pytest

from pcapi.connectors import subcategory_suggestion
from pcapi.core.offerers import factories as offerers_factories

from tests.connectors.suggestion import fixtures


pytestmark = pytest.mark.usefixtures("db_session")


@mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
class CategorySuggestionTest:
    def test_suggested_categories(self, mock_get_id_token_from_google, requests_mock):
        offerer = offerers_factories.OffererFactory(name="Gestionnaire de plein de musées")
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer, name="Le Musée des trucs", venueTypeCode="MUSEUM"
        )
        offer_name = "Une visite au musée"
        offer_description = "C'est quand même mieux que de s'ennuyer"

        requests_mock.post(
            "https://compliance.passculture.team/latest/model/categorisation",
            json=fixtures.SUGGESTION_MUSEE_RESULT,
        )

        suggested_subcategories = subcategory_suggestion.get_suggested_categories(
            offer_name=offer_name, offer_description=offer_description, venue=venue
        )
        assert suggested_subcategories.most_probable_subcategories[0].subcategory == "VISITE_GUIDEE"
        assert suggested_subcategories.most_probable_subcategories[1].subcategory == "VISITE"
        assert suggested_subcategories.most_probable_subcategories[2].subcategory == "EVENEMENT_PATRIMOINE"
