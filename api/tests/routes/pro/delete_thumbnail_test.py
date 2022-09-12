from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Mediation
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class OfferMediationTest:
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_delete_mediation(self, mock_search_async_index_offer_ids, mock_delete_public_object, client):
        offer = offers_factories.OfferFactory()
        mediation = offers_factories.MediationFactory(offer=offer, thumbCount=1)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        client = client.with_session_auth(email="user@example.com")
        response = client.delete(f"/offers/thumbnails/{offer.id}")

        expected_thumb_path = f"{mediation.thumb_path_component}/{humanize(mediation.id)}"
        assert Mediation.query.all() == []
        assert response.status_code == 204
        assert mock_delete_public_object.call_args_list == [
            (("thumbs", expected_thumb_path),),
        ]
        mock_search_async_index_offer_ids.assert_called_once_with([offer.id])

    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    def test_delete_no_mediation(self, mock_delete_public_object, client):
        offer = offers_factories.OfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        client = client.with_session_auth(email="user@example.com")
        response = client.delete(f"/offers/thumbnails/{offer.id}")

        assert response.status_code == 204
        mock_delete_public_object.assert_not_called()

    def test_user_cannot_delete_mediation(self, client):
        offer = offers_factories.OfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        client = client.with_session_auth(email="user@example.com")
        response = client.delete(f"/offers/thumbnails/{offer.id}")

        assert response.status_code == 403

    def test_unkown_offer(self, client):
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        client = client.with_session_auth(email="user@example.com")
        response = client.delete("/offers/thumbnails/123445678")

        assert response.status_code == 404
        expected_error = ["Aucun objet ne correspond à cet identifiant dans notre base de données"]
        assert response.json["global"] == expected_error
