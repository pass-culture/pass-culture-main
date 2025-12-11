import datetime
import decimal

import pytest
import time_machine

from pcapi import settings
from pcapi.core.educational import factories
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


def _create_educational_year():
    factories.create_educational_year(date_time=datetime.datetime.fromisoformat("2022-01-17T22:00:00Z"))


class Return200Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_valid_stock_for_collective_offer(self, client):
        _create_educational_year()
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500.12,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 201
        response_dict = response.json
        created_stock: CollectiveStock = db.session.get(CollectiveStock, response_dict["id"])
        offer = db.session.get(CollectiveOffer, offer.id)
        assert offer.id == created_stock.collectiveOfferId
        assert created_stock.price == decimal.Decimal("1500.12")
        assert created_stock.priceDetail == "Détail du prix"
        assert offer.validation == OfferValidationStatus.DRAFT
        assert created_stock.startDatetime == datetime.datetime(2022, 1, 17, 22, 0, 0)
        assert created_stock.endDatetime == datetime.datetime(2022, 1, 17, 22, 0, 0)

    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_valid_stock_for_collective_offe_with_start_end_datetime(self, client):
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        factories.EducationalYearFactory(beginningDate="2021-09-01T22:00:00Z", expirationDate="2022-07-31T22:00:00Z")

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-18T18:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500.12,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 201
        response_dict = response.json
        created_stock: CollectiveStock = db.session.get(CollectiveStock, response_dict["id"])
        offer = db.session.get(CollectiveOffer, offer.id)
        assert offer.id == created_stock.collectiveOfferId
        assert created_stock.price == decimal.Decimal("1500.12")
        assert created_stock.priceDetail == "Détail du prix"
        assert offer.validation == OfferValidationStatus.DRAFT
        assert created_stock.startDatetime == datetime.datetime(2022, 1, 17, 22, 0, 0)
        assert created_stock.endDatetime == datetime.datetime(2022, 1, 18, 18, 0, 0)


class Return400Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_collective_stocks_should_not_be_available_if_user_not_linked_to_offerer(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def test_missing_end_datetime(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 10,
            "educationalPriceDetail": "Détail du prix",
        }

        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["Ce champ est obligatoire"]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_number_of_tickets_to_be_negative_on_creation(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": -1,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut pas être négatif."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_price_to_be_negative_on_creation(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": -1500,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut pas être négatif."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_price_to_be_too_high(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": settings.EAC_OFFER_PRICE_LIMIT + 1,
            "numberOfTickets": 1,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix est trop élevé."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_too_many_tickets(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 100,
            "numberOfTickets": settings.EAC_NUMBER_OF_TICKETS_LIMIT + 1,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places est trop élevé."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_bookingLimitDatetime_after_startDatetime(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-18T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_price_details_with_more_than_1000_caracters(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_multiple_stocks(self, client):
        _create_educational_year()
        offer = factories.CollectiveStockFactory().collectiveOffer
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_invalid_stock_for_collective_offer(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "1970-12-01T00:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "1970-01-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"startDatetime": ["L'évènement ne peut commencer dans le passé."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_startDatetime_after_endDatetime(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        factories.EducationalYearFactory(beginningDate="2021-09-01T22:00:00Z", expirationDate="2022-07-31T22:00:00Z")

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-18T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-16T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")

        response = client.post("/collective/stocks", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_missing_educational_year(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-18T18:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Détail du prix",
        }

        response = client.with_session_auth("user@example.com").post("/collective/stocks", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"code": "START_EDUCATIONAL_YEAR_MISSING"}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_startDatetime_endDatetime_in_different_educational_year(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        factories.EducationalYearFactory(
            beginningDate="2021-09-01T22:00:00Z", expirationDate="2022-07-31T22:00:00Z", id=1
        )
        factories.EducationalYearFactory(
            beginningDate="2022-09-01T22:00:00Z", expirationDate="2023-07-31T22:00:00Z", id=2
        )

        stock_payload = {
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2023-01-18T18:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Détail du prix",
        }

        client.with_session_auth("user@example.com")

        with assert_num_queries(7):
            # query += 1 -> load session and user
            # query += 1 -> ensure the offerer is VALIDATED
            # query += 1 -> check the number of existing stock for the offer id
            # query += 1 -> find education year for start date
            # query += 1 -> find education year for end date
            # query += 1 -> rollback
            # query += 1 -> rollback
            response = client.post("/collective/stocks", json=stock_payload)

            assert response.status_code == 400
            assert response.json == {"code": "START_AND_END_EDUCATIONAL_YEAR_DIFFERENT"}

    def should_not_accept_payload_with_dates_in_the_past(self, client):
        past = (date_utils.get_naive_utc_now() - datetime.timedelta(days=1)).isoformat() + "Z"
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            "bookingLimitDatetime": past,
            "educationalPriceDetail": "Hello",
            "endDatetime": past,
            "numberOfTickets": 25,
            "offerId": offer.id,
            "startDatetime": past,
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        with assert_num_queries(2):  # session + rollback
            response = client.post("/collective/stocks", json=stock_payload)

            assert response.status_code == 400
            assert response.json == {
                "endDatetime": ["L'évènement ne peut se terminer dans le passé."],
                "startDatetime": ["L'évènement ne peut commencer dans le passé."],
            }

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.parametrize("status", [OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED])
    def should_not_accept_stock_creation_for_pending_and_rejected_offer(self, status, client):
        _create_educational_year()
        offer = factories.CollectiveOfferFactory(validation=status)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        response = client.with_session_auth("user@example.com").post(
            "/collective/stocks/",
            json={
                "offerId": offer.id,
                "startDatetime": "2022-01-17T22:00:00Z",
                "endDatetime": "2022-01-17T22:00:00Z",
                "bookingLimitDatetime": "2021-12-31T20:00:00Z",
                "totalPrice": 1500.12,
                "numberOfTickets": 38,
                "educationalPriceDetail": "Détail du prix",
            },
        )

        assert response.status_code == 400
        assert response.json == {"global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]}
