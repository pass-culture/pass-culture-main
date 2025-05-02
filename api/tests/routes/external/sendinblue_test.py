import logging
from unittest.mock import patch

import pytest

from pcapi.connectors.recommendation import RecommendationApiException
from pcapi.connectors.recommendation import RecommendationApiTimeoutException
from pcapi.core.categories import subcategories
from pcapi.core.history import models as history_models
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.factories import ProductMediationFactory
from pcapi.core.offers.models import ImageType
from pcapi.core.testing import assert_num_queries
from pcapi.core.users.factories import UserFactory
from pcapi.models import db


class SubscribeOrUnsubscribeUserTestHelper:
    # attributes overriden in inherited test classes
    endpoint = NotImplemented
    initial_marketing_email = NotImplemented
    expected_marketing_email = NotImplemented

    def test_webhook_ok(self, client):
        # Given
        existing_user = UserFactory(
            email="lucy.ellingson@kennet.ca",
            notificationSubscriptions={"marketing_push": True, "marketing_email": self.initial_marketing_email},
        )
        data = {"email": "lucy.ellingson@kennet.ca"}
        assert existing_user.notificationSubscriptions["marketing_email"] is self.initial_marketing_email

        # When
        response = client.post(self.endpoint, json=data)

        # Then
        assert response.status_code == 204
        db.session.refresh(existing_user)
        assert existing_user.notificationSubscriptions["marketing_email"] is self.expected_marketing_email

        action = (
            db.session.query(history_models.ActionHistory)
            .filter(
                history_models.ActionHistory.actionType == history_models.ActionType.INFO_MODIFIED,
                history_models.ActionHistory.authorUserId == existing_user.id,
                history_models.ActionHistory.userId == existing_user.id,
            )
            .one()
        )
        assert action.extraData == {
            "modified_info": {
                "notificationSubscriptions.marketing_email": {
                    "old_info": self.initial_marketing_email,
                    "new_info": self.expected_marketing_email,
                }
            },
        }

    def test_webhook_bad_request(self, client):
        data = {}
        response = client.post(self.endpoint, json=data)

        assert response.status_code == 400

    def test_webhook_user_does_not_exist(self, client):
        # Given
        data = {"email": "lucy.ellingson@kennet.ca"}

        # When
        response = client.post(self.endpoint, json=data)

        # Then
        assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
class UnsubscribeUserTest(SubscribeOrUnsubscribeUserTestHelper):
    endpoint = "/webhooks/sendinblue/unsubscribe"
    initial_marketing_email = True
    expected_marketing_email = False


@pytest.mark.usefixtures("db_session")
class SubscribeUserTest(SubscribeOrUnsubscribeUserTestHelper):
    endpoint = "/webhooks/sendinblue/subscribe"
    initial_marketing_email = False
    expected_marketing_email = True


@pytest.mark.usefixtures("db_session")
class NotifyImportContactsTest:
    def test_notify_importcontacts(self, client, caplog):
        # When
        with caplog.at_level(logging.INFO):
            response = client.post("/webhooks/sendinblue/importcontacts/18/1")

        # Then
        assert response.status_code == 204
        assert caplog.records[0].message == "ContactsApi->import_contacts finished"
        assert caplog.records[0].extra == {
            "list_id": 18,
            "iteration": 1,
        }


@pytest.mark.usefixtures("db_session")
@pytest.mark.features(WIP_ENABLE_BREVO_RECOMMENDATION_ROUTE=True)
@pytest.mark.settings(BREVO_WEBHOOK_SECRET="secret")
class GetUserRecommendationsTest:
    headers = {"Authorization": "Bearer secret"}

    @patch(
        "pcapi.connectors.recommendation.get_playlist",
        return_value=b'{"playlist_recommended_offers": ["1", "2"], "params": {}}',
    )
    def test_get_user_recommendations(self, _get_playlist_mock, client):
        user_id = UserFactory(id=1).id
        product = ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        ProductMediationFactory(product=product, uuid="12345678", imageType=ImageType.RECTO)
        OfferFactory(id=1, product=product)
        offer_2 = OfferFactory(id=2)

        expected_num_queries = 1  # feature
        expected_num_queries += 1  # user
        expected_num_queries += 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/webhooks/brevo/recommendations/{user_id}", headers=self.headers)

        assert response.status_code == 200
        assert sorted(response.json["offers"], key=lambda item: item["name"]) == [
            {"image": None, "name": offer_2.name, "url": "https://webapp-v2.example.com/offre/2"},
            {
                "image": "http://localhost/storage/thumbs/12345678",
                "name": product.name,
                "url": "https://webapp-v2.example.com/offre/1",
            },
        ]

    @pytest.mark.features(WIP_ENABLE_BREVO_RECOMMENDATION_ROUTE=False)
    def test_401_on_invalid_token(self, client):
        user_id = UserFactory(id=1).id
        response = client.get(
            f"/webhooks/brevo/recommendations/{user_id}", headers={"Authorization": "Bearer invalid-secret"}
        )

        assert response.status_code == 401

    def test_fails_on_user_not_found(self, client):
        response = client.get("/webhooks/brevo/recommendations/0", headers=self.headers)

        assert response.status_code == 404

    @pytest.mark.features(WIP_ENABLE_BREVO_RECOMMENDATION_ROUTE=False)
    def test_404_on_feature_flag_disabled(self, client):
        user_id = UserFactory(id=1).id
        response = client.get(f"/webhooks/brevo/recommendations/{user_id}", headers=self.headers)

        assert response.status_code == 404

    @patch("pcapi.connectors.recommendation.get_playlist", return_value=b"invalid JSON}")
    def test_fails_on_decode_error(self, _get_playlist_mock, client):
        user_id = UserFactory(id=1).id
        response = client.get(f"/webhooks/brevo/recommendations/{user_id}", headers=self.headers)

        assert response.status_code == 500

    @patch("pcapi.connectors.recommendation.get_playlist", side_effect=RecommendationApiException)
    def test_fails_on_api_error(self, _get_playlist_mock, client):
        user_id = UserFactory(id=1).id
        response = client.get(f"/webhooks/brevo/recommendations/{user_id}", headers=self.headers)

        assert response.status_code == 502

    @patch("pcapi.connectors.recommendation.get_playlist", side_effect=RecommendationApiTimeoutException)
    def test_fails_on_api_timeout(self, _get_playlist_mock, client):
        user_id = UserFactory(id=1).id
        response = client.get(f"/webhooks/brevo/recommendations/{user_id}", headers=self.headers)

        assert response.status_code == 504
