from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_settings
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2020-11-17 15:00:00")
class Return200Test:
    def test_edit_collective_stock(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Nouvelle description du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = CollectiveStock.query.get(stock.id)
        assert edited_stock.beginningDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 31, 20)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 38
        assert edited_stock.priceDetail == "Nouvelle description du prix"

        assert response.json == {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "id": humanize(stock.id),
            "price": 1500.0,
            "numberOfTickets": 38,
            "isEducationalStockEditable": True,
            "educationalPriceDetail": "Nouvelle description du prix",
            "stockId": None,
        }

    def test_edit_collective_stock_begining_datedame_same_day(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18, 18, 22, 12),
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
            "beginningDatetime": "2021-12-18T00:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = CollectiveStock.query.get(stock.id)
        assert edited_stock.beginningDatetime == datetime(2021, 12, 18, 00)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 18, 00)

        assert response.json == {
            "beginningDatetime": "2021-12-18T00:00:00Z",
            "bookingLimitDatetime": "2021-12-18T00:00:00Z",
            "id": humanize(stock.id),
            "price": 1200.0,
            "numberOfTickets": 32,
            "isEducationalStockEditable": True,
            "educationalPriceDetail": "Détail du prix",
            "stockId": None,
        }

    def test_edit_collective_stock_partially(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            priceDetail="Détail du prix",
        )
        educational_factories.CancelledCollectiveBookingFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = CollectiveStock.query.get(stock.id)
        assert edited_stock.beginningDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 1)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 32
        assert edited_stock.priceDetail == "Détail du prix"

        assert len(adage_api_testing.adage_requests) == 0

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_edit_collective_stock_with_pending_booking(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 200
        edited_stock = CollectiveStock.query.get(stock.id)
        edited_booking = CollectiveBooking.query.get(booking.id)
        assert edited_stock.beginningDatetime == datetime(2021, 12, 18)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 1)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 38
        assert edited_stock.priceDetail == "Nouvelle description du prix"
        assert edited_booking.amount == 1500
        assert edited_booking.confirmationLimitDate is not None

        expected_payload = EducationalBookingEdition(
            **serialize_collective_booking(edited_booking).dict(),
            updatedFields=["price", "numberOfTickets", "educationalPriceDetail"],
        )
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation-edit"

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_edit_collective_stock_does_not_send_notification_when_no_modification(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
        client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert len(adage_api_testing.adage_requests) == 0

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_edit_collective_stock_update_booking_educational_year(self, client):
        # Given
        educational_year_2021_2022 = educational_factories.EducationalYearFactory(
            beginningDate=datetime(2021, 9, 1), expirationDate=datetime(2022, 8, 31)
        )
        educational_year_2022_2023 = educational_factories.EducationalYearFactory(
            beginningDate=datetime(2022, 9, 1), expirationDate=datetime(2023, 8, 31)
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
            "beginningDatetime": "2023-01-17T22:00:00Z",
        }

        client.with_session_auth("user@example.com")
        client.patch(f"/collective/stocks/{humanize(collective_stock.id)}", json=stock_edition_payload)

        # Then
        edited_collective_booking = CollectiveBooking.query.get(collective_booking.id)
        assert edited_collective_booking.educationalYearId == educational_year_2022_2023.adageId


@freeze_time("2020-11-17 15:00:00")
class Return403Test:
    def test_edit_collective_stocks_should_not_be_possible_when_user_not_linked_to_offerer(self, client):
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


@freeze_time("2020-11-17 15:00:00")
class Return400Test:
    def should_not_allow_number_of_tickets_to_be_negative_on_edition(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "numberOfTickets": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = CollectiveStock.query.get(stock.id)
        assert edited_stock.numberOfTickets == 32

    def should_not_allow_price_to_be_negative_on_creation(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = CollectiveStock.query.get(stock.id)
        assert edited_stock.price == 1200

    def should_not_accept_payload_with_bookingLimitDatetime_after_beginningDatetime(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
            "beginningDatetime": "2021-12-20T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T22:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = CollectiveStock.query.get(stock.id)
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime

    def should_not_edit_stock_when_event_expired(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(beginningDatetime=datetime.utcnow() - timedelta(minutes=1))
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400

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
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut pas être nul."]}

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
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut pas être nul."]}

    def should_not_allow_stock_edition_when_beginnningDatetime_has_been_set_to_none(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.collectiveOffer.venue.managingOfferer,
        )

        # When
        stock_edition_payload = {
            "beginningDatetime": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"beginningDatetime": ["La date de début de l'événement ne peut pas être nulle."]}

    def should_raise_error_when_educational_price_detail_length_is_greater_than_1000(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}

    def test_create_valid_stock_for_collective_offer(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
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
            "beginningDatetime": "1970-12-01T00:00:00Z",
            "bookingLimitDatetime": "1970-01-31T20:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/collective/stocks/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"beginningDatetime": ["L'évènement ne peut commencer dans le passé."]}
