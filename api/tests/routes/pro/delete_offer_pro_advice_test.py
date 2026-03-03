from unittest.mock import ANY
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.pro_advice.exceptions as pro_advice_exceptions
import pcapi.core.users.factories as users_factories
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    @patch("pcapi.core.pro_advice.api.delete_pro_advice")
    def test_delete_pro_advice(self, mock_delete_pro_advice, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)
        offers_factories.ProAdviceFactory(offer=offer)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        response = auth_client.delete(f"/offers/{offer.id}/pro_advice")

        assert response.status_code == 204
        mock_delete_pro_advice.assert_called_once_with(offer, ANY)


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @patch("pcapi.core.pro_advice.api.delete_pro_advice")
    def test_delete_pro_advice_raises_error(self, mock_delete_pro_advice, client):
        mock_delete_pro_advice.side_effect = pro_advice_exceptions.ProAdviceException(
            {"global": ["Impossible de supprimer une recommandation sur cette offre"]}
        )
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.DRAFT)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        response = auth_client.delete(f"/offers/{offer.id}/pro_advice")

        assert response.status_code == 400
        assert response.json["global"] == ["Impossible de supprimer une recommandation sur cette offre"]


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_unauthenticated(self, client):
        offer = offers_factories.OfferFactory()

        response = client.delete(f"/offers/{offer.id}/pro_advice")

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_offer_not_found(self, client):
        pro_user = users_factories.ProFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        response = auth_client.delete("/offers/99999999/pro_advice")

        assert response.status_code == 404

    def test_unauthorized_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=pro_user.email)
        response = auth_client.delete(f"/offers/{offer.id}/pro_advice")

        assert response.status_code == 404
