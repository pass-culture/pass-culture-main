from unittest.mock import ANY
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as models
import pcapi.core.pro_advice.exceptions as pro_advice_exceptions
import pcapi.core.users.factories as users_factories
import pcapi.utils.date as date_utils
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    @patch("pcapi.core.pro_advice.api.create_pro_advice")
    @time_machine.travel("2026-03-03 12:00:00", tick=False)
    def test_create_pro_advice(self, mock_create_pro_advice, client):
        updated_at = date_utils.get_naive_utc_now()
        mock_create_pro_advice.return_value = models.ProAdvice(
            content="Une super reco.",
            author="Le libraire du coin",
            updatedAt=updated_at,
        )

        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        payload = {
            "content": "Une super reco.",
            "author": "Le libraire du coin",
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 201

        assert response.json == {
            "proAdvice": {
                "content": "Une super reco.",
                "author": "Le libraire du coin",
                "updatedAt": date_utils.format_into_utc_date(updated_at),
            }
        }

        mock_create_pro_advice.assert_called_once_with(offer, "Une super reco.", "Le libraire du coin", ANY)

    @patch("pcapi.core.pro_advice.api.create_pro_advice")
    @time_machine.travel("2026-03-03 12:00:00", tick=False)
    def test_create_pro_advice_without_author(self, mock_create_pro_advice, client):
        updated_at = date_utils.get_naive_utc_now()
        mock_create_pro_advice.return_value = models.ProAdvice(
            content="Une super reco.",
            author=None,
            updatedAt=updated_at,
        )

        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        payload = {
            "content": "Une super reco.",
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 201

        assert response.json == {
            "proAdvice": {
                "content": "Une super reco.",
                "author": None,
                "updatedAt": date_utils.format_into_utc_date(updated_at),
            }
        }

        mock_create_pro_advice.assert_called_once_with(offer, "Une super reco.", None, ANY)


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_content_exceeds_max_length(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        payload = {
            "content": "x" * 801,
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 400
        assert response.json["content"] == [
            "Cette chaîne de caractères doit avoir une taille maximum de 800 caractères"
        ]

    def test_author_exceeds_max_length(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        payload = {
            "content": "Un conseil.",
            "author": "x" * 21,
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 400
        assert response.json["author"] == ["Cette chaîne de caractères doit avoir une taille maximum de 20 caractères"]

    @patch("pcapi.core.pro_advice.api.create_pro_advice")
    def test_create_pro_advice_raises_error(self, mock_create_pro_advice, client):
        mock_create_pro_advice.side_effect = pro_advice_exceptions.ProAdviceException(
            {"global": ["Impossible de créer une recommandation sur cette offre"]}
        )
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.DRAFT)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        payload = {
            "content": "Un conseil.",
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Impossible de créer une recommandation sur cette offre"]

    def test_content_is_empty_string(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        payload = {
            "content": "",
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 400
        assert response.json["content"] == ["Cette chaîne de caractères doit avoir une taille minimum de 1 caractères"]

    def test_author_is_empty_string(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        payload = {
            "content": "Un conseil.",
            "author": "",
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 400
        assert response.json["author"] == ["Cette chaîne de caractères doit avoir une taille minimum de 1 caractères"]


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_unauthenticated(self, client):
        offer = offers_factories.OfferFactory()

        payload = {
            "content": "Un conseil.",
        }
        response = client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_offer_not_found(self, client):
        pro_user = users_factories.ProFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        payload = {
            "content": "Un conseil.",
        }
        response = auth_client.post(
            "/offers/99999999/pro_advice",
            json=payload,
        )

        assert response.status_code == 404

    def test_unauthorized_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED)

        auth_client = client.with_session_auth(email=pro_user.email)
        payload = {
            "content": "Un conseil.",
        }
        response = auth_client.post(
            f"/offers/{offer.id}/pro_advice",
            json=payload,
        )

        assert response.status_code == 404
