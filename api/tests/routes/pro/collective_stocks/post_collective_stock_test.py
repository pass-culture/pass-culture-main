import datetime
import decimal

import pytest
import time_machine

from pcapi import settings
from pcapi.core.educational import factories
from pcapi.core.educational.models import CollectiveAdditionalFeeType
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")

BASE_PAYLOAD_NO_DETAIL = {
    "startDatetime": "2022-01-17T22:00:00Z",
    "endDatetime": "2022-01-17T22:00:00Z",
    "bookingLimitDatetime": "2021-12-31T20:00:00Z",
    "price": 1500.12,
    "numberOfTickets": 38,
}

BASE_PAYLOAD = {**BASE_PAYLOAD_NO_DETAIL, "priceDetail": "Détail du prix"}


def _create_educational_year():
    factories.create_educational_year(date_time=datetime.datetime.fromisoformat("2022-01-17T22:00:00Z"))


class Return200Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_valid_stock_for_collective_offer(self, client):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 201
        created_stock = db.session.query(CollectiveStock).filter_by(id=response.json["id"]).one()
        assert offer.id == created_stock.collectiveOfferId
        assert created_stock.price == decimal.Decimal("1500.12")
        assert created_stock.servicePrice == decimal.Decimal("1500.12")
        assert created_stock.collectiveAdditionalFees == []
        assert created_stock.numberOfTickets == 38
        assert created_stock.numberOfTeachers == 0
        assert created_stock.priceDetail == "Détail du prix"
        assert offer.validation == OfferValidationStatus.DRAFT
        assert created_stock.startDatetime == datetime.datetime(2022, 1, 17, 22, 0, 0)
        assert created_stock.endDatetime == datetime.datetime(2022, 1, 17, 22, 0, 0)

        # check double-writing stock.priceDetail -> offer.additionalDetails
        assert offer.additionalDetails == "Détail du prix"

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    def test_price_fields(self, client):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        fees = [
            {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 10.003},
            {"type": CollectiveAdditionalFeeType.ACCOMMODATION.name, "label": None, "amount": 15.003},
            {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "custom fee", "amount": 20.504},
            {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "other custom fee", "amount": 25},
        ]
        stock_payload = {
            **BASE_PAYLOAD_NO_DETAIL,
            "offerId": offer.id,
            "numberOfTeachers": 10,
            "price": 110.50,
            "servicePrice": 40,
            "collectiveAdditionalFees": fees,
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 201
        created_stock = db.session.query(CollectiveStock).filter_by(id=response.json["id"]).one()
        assert created_stock.priceDetail is None
        assert created_stock.numberOfTeachers == 10
        assert created_stock.price == 110.50
        assert created_stock.servicePrice == 40

        expected = [
            {**fee, "amount": decimal.Decimal(str(fee["amount"])).quantize(decimal.Decimal("1.00"))} for fee in fees
        ]
        actual = [
            {"type": fee.type.name, "label": fee.label, "amount": fee.amount}
            for fee in sorted(created_stock.collectiveAdditionalFees, key=lambda f: f.amount)
        ]
        assert actual == expected

        # the sum of the given amounts is different from the value in DB
        # this is because each amount is rounded to 2 decimals before the sum is computed
        assert sum(fee["amount"] for fee in fees) == 70.51
        total_fees = sum(fee.amount for fee in created_stock.collectiveAdditionalFees)
        assert total_fees == 70.50
        assert total_fees + created_stock.servicePrice == created_stock.price

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    def test_price_fields_no_fees(self, client):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD_NO_DETAIL,
            "offerId": offer.id,
            "numberOfTeachers": 10,
            "price": 10.99,
            "servicePrice": 10.99,
            "collectiveAdditionalFees": [],
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 201
        created_stock = db.session.query(CollectiveStock).filter_by(id=response.json["id"]).one()
        assert created_stock.priceDetail is None
        assert created_stock.numberOfTeachers == 10
        assert created_stock.price == decimal.Decimal("10.99")
        assert created_stock.servicePrice == decimal.Decimal("10.99")
        assert created_stock.collectiveAdditionalFees == []


class Return404Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_collective_stocks_should_not_be_available_if_user_not_linked_to_offerer(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_collective_stocks_should_not_be_available_if_offer_not_found(self, client):
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        stock_payload = {**BASE_PAYLOAD, "offerId": 123456789}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}


class Return400Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_missing_end_datetime(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id}
        del stock_payload["endDatetime"]
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["Ce champ est obligatoire"]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_number_of_tickets_to_be_negative_on_creation(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "numberOfTickets": -1,
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Saisissez un nombre supérieur ou égal à 0"]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_price_to_be_negative_on_creation(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "price": -1500,
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"price": ["Saisissez un nombre supérieur ou égal à 0"]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_price_to_be_too_high(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "price": settings.EAC_OFFER_PRICE_LIMIT + 1,
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"price": [f"Saisissez un nombre inférieur ou égal à {settings.EAC_OFFER_PRICE_LIMIT}"]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_too_many_tickets(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "numberOfTickets": settings.EAC_NUMBER_OF_TICKETS_LIMIT + 1,
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {
            "numberOfTickets": [f"Saisissez un nombre inférieur ou égal à {settings.EAC_NUMBER_OF_TICKETS_LIMIT}"]
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_accept_payload_with_bookingLimitDatetime_after_startDatetime(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-18T20:00:00Z",
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_accept_payload_with_price_details_with_more_than_1000_caracters(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "priceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"priceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_multiple_stocks(self, client):
        _create_educational_year()
        offer = factories.CollectiveStockFactory().collectiveOffer
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_invalid_stock_for_collective_offer(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "startDatetime": "1970-12-01T00:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "1970-01-31T20:00:00Z",
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"startDatetime": ["L'évènement ne peut commencer dans le passé."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_accept_payload_with_startDatetime_after_endDatetime(self, client):
        _create_educational_year()
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "startDatetime": "2022-01-18T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2022-01-16T20:00:00Z",
        }
        response = client.with_session_auth("user@example.com").post("/collective/stocks", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_missing_educational_year(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"code": "START_EDUCATIONAL_YEAR_MISSING"}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_accept_payload_with_startDatetime_endDatetime_in_different_educational_year(self, client):
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        factories.EducationalYearFactory(
            beginningDate="2021-09-01T22:00:00Z", expirationDate="2022-07-31T22:00:00Z", id=1
        )
        factories.EducationalYearFactory(
            beginningDate="2022-09-01T22:00:00Z", expirationDate="2023-07-31T22:00:00Z", id=2
        )

        stock_payload = {
            **BASE_PAYLOAD,
            "offerId": offer.id,
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2023-01-18T18:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
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

    def test_should_not_accept_payload_with_dates_in_the_past(self, client):
        past = (date_utils.get_naive_utc_now() - datetime.timedelta(days=1)).isoformat() + "Z"
        offer = factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {
            **BASE_PAYLOAD,
            "bookingLimitDatetime": past,
            "endDatetime": past,
            "offerId": offer.id,
            "startDatetime": past,
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
    def test_should_not_accept_stock_creation_for_pending_and_rejected_offer(self, status, client):
        _create_educational_year()
        offer = factories.CollectiveOfferFactory(validation=status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]}

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    def test_price_detail_not_allowed(self, client):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"priceDetail": ["Ce champ ne peut pas être présent"]}

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=False)
    def test_price_detail_required(self, client):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD_NO_DETAIL, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"priceDetail": ["Ce champ est requis"]}

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    def test_number_of_teachers_required(self, client):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD_NO_DETAIL, "offerId": offer.id}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"numberOfTeachers": ["Ce champ est requis"]}

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    @pytest.mark.parametrize(
        "number_of_teachers,error",
        (
            (None, "Ce champ est requis"),
            (-1, "Saisissez un nombre supérieur ou égal à 0"),
            (60, "Saisissez un nombre inférieur ou égal à 50"),
        ),
    )
    def test_number_of_teachers_required_none(self, client, number_of_teachers, error):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD_NO_DETAIL, "offerId": offer.id, "numberOfTeachers": number_of_teachers}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {"numberOfTeachers": [error]}

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=False)
    @pytest.mark.parametrize(
        "field,value", (("numberOfTeachers", 10), ("servicePrice", 10), ("collectiveAdditionalFees", []))
    )
    def test_price_fields_not_allowed(self, client, field, value):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD, "offerId": offer.id, field: value}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == {field: ["Ce champ ne peut pas être présent"]}

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    @pytest.mark.parametrize(
        "payload,error",
        (
            # missing collectiveAdditionalFees
            ({"price": 10, "servicePrice": 10}, {"collectiveAdditionalFees": ["Ce champ est requis"]}),
            # missing servicePrice
            (
                {
                    "price": 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 10}
                    ],
                },
                {"servicePrice": ["Ce champ est requis"]},
            ),
            # servicePrice = None
            (
                {"price": 10, "servicePrice": None, "collectiveAdditionalFees": []},
                {"servicePrice": ["Ce champ est requis"]},
            ),
            # collectiveAdditionalFees = None
            (
                {"price": 10, "servicePrice": 10, "collectiveAdditionalFees": None},
                {"collectiveAdditionalFees": ["Ce champ est requis"]},
            ),
            # collectiveAdditionalFees invalid label
            (
                {
                    "price": 20,
                    "servicePrice": 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": "hello", "amount": 10}
                    ],
                },
                {"collectiveAdditionalFees.0.label": ["Le label ne peut pas être rempli pour ce type"]},
            ),
            # collectiveAdditionalFees missing label
            (
                {
                    "price": 20,
                    "servicePrice": 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.OTHER.name, "label": None, "amount": 10}
                    ],
                },
                {"collectiveAdditionalFees.0.label": ["Le label doit être rempli pour ce type"]},
            ),
            # collectiveAdditionalFees type duplicate
            (
                {
                    "price": 20,
                    "servicePrice": 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 5},
                        {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 5},
                    ],
                },
                {"collectiveAdditionalFees.root": ["Un type est en doublon"]},
            ),
            # collectiveAdditionalFees label duplicate
            (
                {
                    "price": 20,
                    "servicePrice": 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "hello", "amount": 5},
                        {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "hello", "amount": 5},
                    ],
                },
                {"collectiveAdditionalFees.root": ["Un label est en doublon"]},
            ),
            # collectiveAdditionalFees negative amount
            (
                {
                    "price": 20,
                    "servicePrice": 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "hello", "amount": -5},
                        {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "hello", "amount": 15},
                    ],
                },
                {"collectiveAdditionalFees.0.amount": ["Saisissez un nombre supérieur ou égal à 0"]},
            ),
            # servicePrice too low
            (
                {
                    "price": 20,
                    "servicePrice": -1,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 19}
                    ],
                },
                {"servicePrice": ["Saisissez un nombre supérieur ou égal à 0"]},
            ),
            # price total does not match
            (
                {
                    "price": 20,
                    "servicePrice": 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 10},
                        {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "hello", "amount": 5},
                    ],
                },
                {"price": ["Le prix total ne correspond pas à la somme du prix de la prestation et des frais annexes"]},
            ),
            # price too high
            (
                {
                    "price": settings.EAC_OFFER_PRICE_LIMIT + 5,
                    "servicePrice": settings.EAC_OFFER_PRICE_LIMIT - 10,
                    "collectiveAdditionalFees": [
                        {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 10},
                        {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "hello", "amount": 5},
                    ],
                },
                {"price": [f"Saisissez un nombre inférieur ou égal à {settings.EAC_OFFER_PRICE_LIMIT}"]},
            ),
        ),
    )
    def test_price_errors(self, client, payload, error):
        _create_educational_year()
        offer = factories.DraftCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        stock_payload = {**BASE_PAYLOAD_NO_DETAIL, "offerId": offer.id, "numberOfTeachers": 10, **payload}
        response = client.with_session_auth("user@example.com").post("/collective/stocks/", json=stock_payload)

        assert response.status_code == 400
        assert response.json == error
