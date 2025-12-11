from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
import time_machine

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import testing as adage_api_testing
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.schemas import EducationalBookingEdition
from pcapi.core.educational.serialization.collective_booking import serialize_collective_booking
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_edit_collective_stock(self, client):
        # Given
        _educational_year_2021_2022 = educational_factories.EducationalYearFactory(
            beginningDate=datetime(2021, 9, 1), expirationDate=datetime(2022, 8, 31)
        )

        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Nouvelle description du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.startDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 31, 20)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 38
        assert edited_stock.priceDetail == "Nouvelle description du prix"

        assert response.json == {
            "startDatetime": "2022-01-17T22:00:00Z",
            "endDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "id": stock.id,
            "price": 1500.0,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Nouvelle description du prix",
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def test_edit_collective_stock_start_datetime_same_day(self, client):
        # Given
        _educational_year_2021_2022 = educational_factories.EducationalYearFactory(
            beginningDate=datetime(2021, 9, 1), expirationDate=datetime(2022, 8, 31)
        )
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18, 18, 22, 12),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 18, 18, 22, 11),
            priceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2021-12-18T00:00:00Z",
            "endDatetime": "2021-12-18T00:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.startDatetime == datetime(2021, 12, 18, 00)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 18, 00)

        assert response.json == {
            "startDatetime": "2021-12-18T00:00:00Z",
            "endDatetime": "2021-12-18T00:00:00Z",
            "bookingLimitDatetime": "2021-12-18T00:00:00Z",
            "id": stock.id,
            "price": 1200.0,
            "numberOfTickets": 32,
            "educationalPriceDetail": "Détail du prix",
        }

    @time_machine.travel("2020-11-17 15:00:00")
    def test_edit_collective_stock_partially(self, client):
        _educational_year_2021_2022 = educational_factories.EducationalYearFactory(
            beginningDate=datetime(2021, 9, 1), expirationDate=datetime(2022, 8, 31)
        )
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            endDatetime=datetime(2022, 1, 25),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        stock_edition_payload = {
            "startDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        assert response.status_code == 200
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.startDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 1)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 32
        assert edited_stock.priceDetail == "Détail du prix"

        assert len(adage_api_testing.adage_requests) == 0

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
    def test_edit_collective_stock_with_pending_booking(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        booking = educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Nouvelle description du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = db.session.get(CollectiveStock, stock.id)
        edited_booking = db.session.get(CollectiveBooking, booking.id)
        assert edited_stock.startDatetime == datetime(2021, 12, 18)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 1)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 38
        assert edited_stock.priceDetail == "Nouvelle description du prix"
        assert edited_booking.confirmationLimitDate is not None

        expected_payload = EducationalBookingEdition(
            **serialize_collective_booking(edited_booking).dict(),
            updatedFields=["price", "numberOfTickets", "educationalPriceDetail"],
        )
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-edit"

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
    def test_edit_collective_stock_does_not_send_notification_when_no_modification(self, client):
        # patch_offer_test

        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {}

        client.with_session_auth("user@example.com")
        client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert len(adage_api_testing.adage_requests) == 0

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
    def test_edit_collective_stock_update_booking_educational_year(self, client):
        # Given
        educational_year_2021_2022 = educational_factories.EducationalYearFactory(
            beginningDate=datetime(2021, 9, 1), expirationDate=datetime(2022, 8, 31)
        )
        educational_year_2022_2023 = educational_factories.EducationalYearFactory(
            beginningDate=datetime(2022, 9, 1), expirationDate=datetime(2023, 8, 31)
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        collective_booking = educational_factories.CollectiveBookingFactory(
            educationalYear=educational_year_2021_2022,
            collectiveStock=collective_stock,
            status=CollectiveBookingStatus.PENDING,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=collective_stock.collectiveOffer.venue.managingOfferer
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2023-01-17T22:00:00Z",
            "endDatetime": "2023-01-17T22:00:00Z",
        }

        client.with_session_auth("user@example.com")
        client.patch(f"/collective/stocks/{collective_stock.id}", json=stock_edition_payload)

        # Then
        edited_collective_booking = db.session.get(CollectiveBooking, collective_booking.id)
        assert edited_collective_booking.educationalYearId == educational_year_2022_2023.adageId

    def test_edit_collective_stock_update_booking_limit_date_with_expired_booking(self, client):
        now = date_utils.get_naive_utc_now()
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=now + timedelta(days=5), bookingLimitDatetime=now - timedelta(days=2)
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationReason=CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=now - timedelta(days=1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        new_limit = now + timedelta(days=1)
        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json={"bookingLimitDatetime": new_limit.isoformat()})
        assert response.status_code == 200

        db.session.refresh(stock)
        db.session.refresh(booking)
        assert stock.bookingLimitDatetime == new_limit
        assert booking.status == CollectiveBookingStatus.PENDING
        assert booking.cancellationReason == None
        assert booking.cancellationDate == None


class Return403Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_edit_collective_stocks_should_not_be_possible_when_user_not_linked_to_offerer(self, client):
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }

    def test_edit_collective_stocks_should_not_be_possible_when_offer_created_by_public_api(self, client):
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=providers_factories.ProviderFactory()
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        stock_edition_payload = {"totalPrice": 1500}

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        assert response.status_code == 403
        assert response.json == {"global": ["Cette action n'est pas autorisée sur l'offre collective liée à ce stock."]}


class Return400Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_number_of_tickets_to_be_negative_on_edition(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2022-01-17T22:00:00Z",
            "numberOfTickets": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.numberOfTickets == 32

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_price_to_be_negative_on_creation(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.price == 1200

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_bookingLimitDatetime_after_startDatetime(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2021-12-20T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T22:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_stock_edition_when_numberOfTickets_has_been_set_to_none(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "numberOfTickets": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut pas être nul."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_stock_edition_when_totalPrice_has_been_set_to_none(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "totalPrice": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut pas être nul."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_stock_edition_when_startDatetime_has_been_set_to_none(self, client):
        stock = educational_factories.CollectiveStockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        stock_edition_payload = {"startDatetime": None}

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        assert response.status_code == 400
        assert response.json == {"startDatetime": ["La date de début de l'évènement ne peut pas être nulle."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_allow_stock_edition_when_endDatetime_has_been_set_to_none(self, client):
        stock = educational_factories.CollectiveStockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        stock_edition_payload = {"endDatetime": None}

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["La date de fin de l'évènement ne peut pas être nulle."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_raise_error_when_educational_price_detail_length_is_greater_than_1000(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def test_create_valid_stock_for_collective_offer(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "startDatetime": "1970-12-01T00:00:00Z",
            "bookingLimitDatetime": "1970-01-31T20:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"startDatetime": ["L'évènement ne peut commencer dans le passé."]}

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_startDatetime_after_endDatetime(self, client):
        # Given
        startDatetime = datetime(2021, 12, 18)
        endDatetime = datetime(2021, 12, 19)
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=startDatetime,
            endDatetime=endDatetime,
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "startDatetime": "2021-12-20T22:00:00Z",
            "endDatetime": "2021-12-19T22:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.startDatetime == startDatetime
        assert edited_stock.endDatetime == endDatetime

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_startDatetime_endDatetime_in_different_educational_year(self, client):
        # Given
        educational_factories.EducationalYearFactory(
            beginningDate="2021-09-01T22:00:00Z", expirationDate="2022-07-31T22:00:00Z"
        )
        educational_factories.EducationalYearFactory(
            beginningDate="2022-09-01T22:00:00Z", expirationDate="2023-07-31T22:00:00Z"
        )

        startDatetime = datetime(2021, 12, 18)
        endDatetime = datetime(2021, 12, 19)

        stock = educational_factories.CollectiveStockFactory(
            startDatetime=startDatetime,
            endDatetime=endDatetime,
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "endDatetime": "2022-12-19T22:00:00Z",
        }

        client.with_session_auth("user@example.com")

        stock_id = stock.id

        with assert_num_queries(8):
            # query += 1 -> load session + user
            # query += 1 -> load existing stock
            # query += 1 -> ensure the offerer is VALIDATED
            # query += 1 -> check the number of existing stock for the offer id
            # query += 1 -> find education year for start date
            # query += 1 -> find education year for end date
            # query += 1 -> rollback
            # query += 1 -> rollback

            response = client.patch(f"/collective/stocks/{stock_id}", json=stock_edition_payload)

            # Then
            assert response.status_code == 400
            assert response.json == {"code": "START_AND_END_EDUCATIONAL_YEAR_DIFFERENT"}

        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.startDatetime == startDatetime
        assert edited_stock.endDatetime == endDatetime

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_startDatetime_with_no_educational_year(self, client):
        # Given
        startDatetime = datetime(2021, 12, 18)
        endDatetime = datetime(2021, 12, 19)

        stock = educational_factories.CollectiveStockFactory(
            startDatetime=startDatetime,
            endDatetime=endDatetime,
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "endDatetime": "2022-12-19T22:00:00Z",
        }

        client.with_session_auth("user@example.com")

        stock_id = stock.id

        with assert_num_queries(8):
            # query += 1 -> load session + user
            # query += 1 -> load existing stock
            # query += 1 -> load existing offerer
            # query += 1 -> ensure the offerer is VALIDATED
            # query += 1 -> find education year for start date
            # query += 1 -> rollback
            # query += 1 -> rollback
            # query += 1 -> load existing stock after rollback

            response = client.patch(f"/collective/stocks/{stock_id}", json=stock_edition_payload)

            # Then
            assert response.status_code == 400
            assert response.json == {"code": "START_EDUCATIONAL_YEAR_MISSING"}
            edited_stock = db.session.get(CollectiveStock, stock.id)
            assert edited_stock.startDatetime == startDatetime
            assert edited_stock.endDatetime == endDatetime

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_endDatetime_with_no_educational_year(self, client):
        # Given
        educational_factories.EducationalYearFactory(
            beginningDate="2021-09-01T22:00:00Z", expirationDate="2022-07-31T22:00:00Z"
        )
        startDatetime = datetime(2021, 12, 18)
        endDatetime = datetime(2022, 12, 19)

        stock = educational_factories.CollectiveStockFactory(
            startDatetime=startDatetime,
            endDatetime=endDatetime,
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "endDatetime": "2022-12-19T22:00:00Z",
        }

        client.with_session_auth("user@example.com")

        stock_id = stock.id

        with assert_num_queries(9):
            # query += 1 -> load session + user
            # query += 1 -> load existing stock
            # query += 1 -> load offerer
            # query += 1 -> ensure the offerer is VALIDATED
            # query += 1 -> find education year for start date
            # query += 1 -> find education year for end date
            # query += 1 -> rollback
            # query += 1 -> rollback
            # query += 1 -> load existing stock after rollback

            response = client.patch(f"/collective/stocks/{stock_id}", json=stock_edition_payload)

            # Then
            assert response.status_code == 400
            assert response.json == {"code": "END_EDUCATIONAL_YEAR_MISSING"}
            edited_stock = db.session.get(CollectiveStock, stock.id)
            assert edited_stock.startDatetime == startDatetime
            assert edited_stock.endDatetime == endDatetime

    @time_machine.travel("2020-11-17 15:00:00")
    def should_not_accept_payload_with_endDatetime_before_stock_startDatetime(self, client):
        start = datetime.now(timezone.utc) + timedelta(days=10)
        educational_factories.create_educational_year(date_time=start)
        stock = educational_factories.CollectiveStockFactory(startDatetime=start, endDatetime=start)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        new_end = start - timedelta(days=1)
        stock_edition_payload = {"endDatetime": new_end.isoformat()}
        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        assert response.status_code == 400
        assert response.json == {
            "educationalStock": ["La date de fin de l'évènement ne peut précéder la date de début."]
        }
        edited_stock = db.session.get(CollectiveStock, stock.id)
        assert edited_stock.startDatetime == start.replace(tzinfo=None)
        assert edited_stock.endDatetime == start.replace(tzinfo=None)

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.parametrize(
        "price_value,error",
        (
            (None, "Le prix ne peut pas être nul."),
            (-1, "Le prix ne peut pas être négatif."),
            (settings.EAC_OFFER_PRICE_LIMIT + 1, "Le prix est trop élevé."),
        ),
    )
    def should_not_accept_payload_with_price_error(self, client, price_value, error):
        stock = educational_factories.CollectiveStockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        stock_edition_payload = {"totalPrice": price_value}
        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        assert response.status_code == 400
        assert response.json == {"totalPrice": [error]}

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.parametrize(
        "number_of_tickets_value,error",
        (
            (None, "Le nombre de places ne peut pas être nul."),
            (-1, "Le nombre de places ne peut pas être négatif."),
            (settings.EAC_NUMBER_OF_TICKETS_LIMIT + 1, "Le nombre de places est trop élevé."),
        ),
    )
    def should_not_accept_payload_with_number_of_tickets_error(self, client, number_of_tickets_value, error):
        stock = educational_factories.CollectiveStockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com", offerer=stock.collectiveOffer.venue.managingOfferer
        )

        stock_edition_payload = {"numberOfTickets": number_of_tickets_value}
        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{stock.id}", json=stock_edition_payload)

        assert response.status_code == 400
        assert response.json == {"numberOfTickets": [error]}
