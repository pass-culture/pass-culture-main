import pytest
import time_machine

from pcapi import settings
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveStock
import pcapi.core.offerers.factories as offerers_factories
from pcapi.models.offer_mixin import OfferValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_valid_stock_for_collective_offer(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 201
        response_dict = response.json
        created_stock: CollectiveStock = CollectiveStock.query.get(response_dict["id"])
        offer = CollectiveOffer.query.get(offer.id)
        assert offer.id == created_stock.collectiveOfferId
        assert created_stock.price == 1500
        assert created_stock.priceDetail == "Détail du prix"
        assert offer.validation == OfferValidationStatus.DRAFT


class Return400Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_collective_stocks_should_not_be_available_if_user_not_linked_to_offerer(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        # assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_number_of_tickets_to_be_negative_on_creation(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": -1,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut pas être négatif."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_price_to_be_negative_on_creation(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": -1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut pas être négatif."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_price_to_be_too_high(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": settings.EAC_OFFER_PRICE_LIMIT + 1,
            "numberOfTickets": 1,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix est trop élevé."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_too_many_tickets(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 100,
            "numberOfTickets": settings.EAC_NUMBER_OF_TICKETS_LIMIT + 1,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places est trop élevé."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_bookingLimitDatetime_after_beginningDatetime(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-18T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_price_details_with_more_than_1000_caracters(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_multiple_stocks(self, client):
        # Given
        offer = educational_factories.CollectiveStockFactory().collectiveOffer
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 409
        assert response.json == {"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"}

    def test_create_valid_stock_for_collective_offer(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        stock_payload = {
            "offerId": offer.id,
            "beginningDatetime": "1970-12-01T00:00:00Z",
            "bookingLimitDatetime": "1970-01-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"beginningDatetime": ["L'évènement ne peut commencer dans le passé."]}
