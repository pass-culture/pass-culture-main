from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.offers import factories as offer_factories
from pcapi.core.offers.models import Stock
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2020-11-17 15:00:00")
class Return200Test:
    def test_edit_educational_stock(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            educationalPriceDetail="Détail du prix",
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T20:00:00Z",
            "totalPrice": 1500,
            "numberOfTickets": 38,
            "educationalPriceDetail": "Nouvelle description du prix",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 204
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.beginningDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == datetime(2021, 12, 31, 20)
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 38
        assert edited_stock.educationalPriceDetail == "Nouvelle description du prix"

    def test_edit_educational_stock_partially(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            educationalPriceDetail="Détail du prix",
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 204
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.beginningDatetime == datetime(2022, 1, 17, 22)
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime
        assert edited_stock.price == 1500
        assert edited_stock.numberOfTickets == 32
        assert edited_stock.educationalPriceDetail == "Détail du prix"


@freeze_time("2020-11-17 15:00:00")
class Return403Test:
    def test_edit_educational_stocks_should_not_be_possible_when_user_not_linked_to_offerer(self, app, client):
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
        )
        offer_factories.UserOffererFactory(
            user__email="user@example.com",
        )

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


@freeze_time("2020-11-17 15:00:00")
class Return400Test:
    def should_not_allow_number_of_tickets_to_be_negative_on_edition(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "numberOfTickets": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.numberOfTickets == 32

    def should_not_allow_price_to_be_negative_on_creation(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2022-01-17T22:00:00Z",
            "totalPrice": -10,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.price == 1200

    def should_not_accept_payload_with_bookingLimitDatetime_after_beginningDatetime(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": "2021-12-20T22:00:00Z",
            "bookingLimitDatetime": "2021-12-31T22:00:00Z",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        edited_stock = Stock.query.get(stock.id)
        assert edited_stock.bookingLimitDatetime == stock.bookingLimitDatetime

    def should_not_edit_stock_when_event_expired(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(beginningDatetime=datetime.utcnow() - timedelta(minutes=1))
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400

    def should_not_allow_stock_edition_when_numberOfTickets_has_been_set_to_none(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory()
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "numberOfTickets": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"numberOfTickets": ["Le nombre de places ne peut être nul"]}

    def should_not_allow_stock_edition_when_totalPrice_has_been_set_to_none(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory()
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "totalPrice": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"totalPrice": ["Le prix ne peut être nul"]}

    def should_not_allow_stock_edition_when_beginnningDatetime_has_been_set_to_none(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory()
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "beginningDatetime": None,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"beginningDatetime": ["La date d’évènement ne peut être nulle"]}

    def should_raise_error_when_more_than_one_non_cancelled_bookings_associated_with_stock(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(price=1200, quantity=2, dnBookedQuantity=2)
        booking_factories.EducationalBookingFactory(stock=stock)
        booking_factories.EducationalBookingFactory(stock=stock)

        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "totalPrice": 1500,
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {
            "educationalStockEdition": [
                "Plusieurs réservations non annulées portent sur ce stock d'une offre éducationnelle"
            ]
        }

    def should_raise_error_when_educational_price_detail_length_is_greater_than_1000(self, app, client):
        # Given
        stock = offer_factories.EducationalEventStockFactory(
            beginningDatetime=datetime(2021, 12, 18),
            price=1200,
            numberOfTickets=32,
            bookingLimitDatetime=datetime(2021, 12, 1),
            educationalPriceDetail="Détail du prix",
        )
        offer_factories.UserOffererFactory(user__email="user@example.com", offerer=stock.offer.venue.managingOfferer)

        # When
        stock_edition_payload = {
            "educationalPriceDetail": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer sodales commodo tellus, at dictum odio vulputate nec. Donec iaculis rutrum nunc. Nam euismod, odio vel iaculis tincidunt, enim ante iaculis purus, ac vehicula ex lacus sit amet nisl. Aliquam et diam tellus. Curabitur in pharetra augue. Nunc scelerisque lectus non diam efficitur, eu porta neque vestibulum. Nullam elementum purus ac ligula viverra tincidunt. Etiam tincidunt metus nec nibh tempor tincidunt. Pellentesque ac ipsum purus. Duis vestibulum mollis nisi a vulputate. Nullam malesuada eros eu convallis rhoncus. Maecenas eleifend ex at posuere maximus. Suspendisse faucibus egestas dolor, sit amet dignissim odio condimentum vitae. Pellentesque ultricies eleifend nisi, quis pellentesque nisi faucibus finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Aliquam convallis diam nisl, eget ullamcorper odio convallis ac. Ut quis nulla fringilla, commodo tellus ut.",
        }

        client.with_session_auth("user@example.com")
        response = client.patch(f"/stocks/educational/{humanize(stock.id)}", json=stock_edition_payload)

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalPriceDetail": ["Le détail du prix ne doit pas excéder 1000 caractères."]}
