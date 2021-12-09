import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.offers.models import Stock
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_create_valid_stock_for_educational_offer(self, app, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory()
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/stocks/educational/", json=stock_payload)

        # Then
        assert response.status_code == 201
        response_dict = response.json
        created_stock = Stock.query.get(dehumanize(response_dict["id"]))
        assert offer.id == created_stock.offerId
        assert created_stock.price == 1500


class Return400Test:
    def test_create_educational_stocks_should_not_be_available_if_user_not_linked_to_offerer(self, app, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory()
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/stocks/educational/", json=stock_payload)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }

    def should_not_allow_number_of_tickets_to_be_negative_on_creation(self, app, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory()
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": -1,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/stocks/educational/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut pas être négatif."]}

    def should_not_allow_price_to_be_negative_on_creation(self, app, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory()
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": -1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/stocks/educational/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut pas être négatif."]}

    def should_not_accept_payload_with_bookingLimitDatetime_after_beginningDatetime(self, app, client):
        # Given
        offer = offer_factories.EducationalEventOfferFactory()
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": humanize(offer.id),
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-18T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/stocks/educational/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }
