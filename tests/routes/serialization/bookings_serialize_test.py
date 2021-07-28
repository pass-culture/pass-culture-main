from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offers.factories import StockWithActivationCodesFactory
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.routes.serialization import serialize_booking
from pcapi.routes.serialization.bookings_serialize import serialize_booking_minimal
from pcapi.utils.human_ids import humanize


# FIXME: We already check (or should check) the JSON output of routes
# that use these serializers. These tests are probably not very useful
# and could be removed.


class SerializeBookingTest:
    @freeze_time("2019-11-26 18:29:20.891028")
    def test_should_return_dict_when_offer_is_a_cinema(self):
        # Given
        user = users_factories.BeneficiaryFactory.build(email="user@example.com", publicName="John Doe")
        offerer = create_offerer()
        venue = create_venue(offerer, name="Venue name", address="Venue address")
        offer = create_offer_with_event_product(venue=venue, event_name="Event Name", event_type=EventType.CINEMA)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response == {
            "bookingId": humanize(booking.id),
            "dateOfBirth": "",
            "datetime": "2019-11-26T18:29:20.891028Z",
            "ean13": "",
            "email": "user@example.com",
            "formula": "PLACE",
            "isUsed": False,
            "offerId": offer.id,
            "publicOfferId": humanize(offer.id),
            "offerName": "Event Name",
            "offerType": "EVENEMENT",
            "phoneNumber": "",
            "price": 12,
            "quantity": 3,
            "theater": {},
            "userName": "John Doe",
            "venueAddress": "Venue address",
            "venueDepartementCode": "93",
            "venueName": "Venue name",
        }

    @freeze_time("2019-11-26 18:29:20.891028")
    def test_should_humanize_ids(self):
        # Given
        user = users_factories.BeneficiaryFactory.build(email="user@example.com", publicName="John Doe")
        offerer = create_offerer()
        venue = create_venue(offerer, name="Venue name", address="Venue address")
        offer = create_offer_with_event_product(
            venue=venue, event_name="Event Name", event_type=EventType.CINEMA, idx=999
        )
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response["bookingId"] == humanize(booking.id)
        assert response["offerId"] == offer.id
        assert response["publicOfferId"] == humanize(offer.id)

    def test_should_return_dict_when_offer_is_a_subscription_cinema(self):
        # Given
        user = users_factories.BeneficiaryFactory.build(email="user@example.com", publicName="John Doe")
        offerer = create_offerer()
        venue = create_venue(offerer, name="Venue name", address="Venue address")
        product = create_product_with_thing_type(
            thing_name="Event Name", thing_type=ThingType.CINEMA_ABO, extra_data={"isbn": "123456789"}
        )
        offer = create_offer_with_thing_product(
            venue,
            product=product,
            idx=999,
            extra_data={
                "theater": {
                    "allocine_movie_id": 165,
                    "allocine_room_id": 987,
                },
                "isbn": "123456789",
            },
        )
        stock = create_stock(offer=offer, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response == {
            "bookingId": humanize(booking.id),
            "dateOfBirth": "",
            "datetime": "",
            "ean13": "123456789",
            "email": "user@example.com",
            "formula": "ABO",
            "isUsed": False,
            "offerId": 999,
            "publicOfferId": "APTQ",
            "offerName": "Event Name",
            "offerType": "BIEN",
            "phoneNumber": "",
            "price": 12,
            "quantity": 3,
            "theater": {
                "allocine_movie_id": 165,
                "allocine_room_id": 987,
            },
            "userName": "John Doe",
            "venueAddress": "Venue address",
            "venueDepartementCode": "93",
            "venueName": "Venue name",
        }

    def test_should_return_empty_isbn_when_product_does_not_contain_isbn(self):
        # Given
        user = users_factories.BeneficiaryFactory.build(email="user@example.com", publicName="John Doe")
        offerer = create_offerer()
        venue = create_venue(offerer, name="Venue name", address="Venue address")
        product = create_product_with_thing_type(
            thing_name="Event Name", thing_type=ThingType.CINEMA_ABO, extra_data={}
        )
        offer = create_offer_with_thing_product(venue, product=product, idx=999)
        stock = create_stock(offer=offer, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response["ean13"] == ""

    @freeze_time("2019-11-26 18:29:20.891028")
    def test_should_return_empty_formula_when_offer_is_not_a_cinema(self):
        # Given
        user = users_factories.BeneficiaryFactory.build(email="user@example.com", publicName="John Doe")
        offerer = create_offerer()
        venue = create_venue(offerer, name="Venue name", address="Venue address")
        offer = create_offer_with_event_product(venue=venue, event_name="Event Name", event_type=EventType.JEUX)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response["formula"] == ""

    @freeze_time("2019-11-26 18:29:20.891028")
    def test_should_return_date_of_birth_and_phone_number_when_offer_is_an_activation(self):
        # Given
        user = users_factories.BeneficiaryFactory.build(
            dateOfBirth=datetime(2001, 1, 1),
            email="user@example.com",
            phoneNumber="0612345678",
            publicName="John Doe",
        )
        offerer = create_offerer()
        venue = create_venue(offerer, name="Venue name", address="Venue address")
        offer = create_offer_with_event_product(venue=venue, event_name="Event Name", event_type=EventType.ACTIVATION)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response["dateOfBirth"] == "2001-01-01T00:00:00Z"
        assert response["phoneNumber"] == "0612345678"


@pytest.mark.usefixtures("db_session")
class SerializeBookingMinimalTest:
    def test_should_return_booking_with_expected_information(self):
        # Given
        booking = BookingFactory(
            amount=1,
            quantity=1,
            token="GQTQR9",
            stock__price=10,
        )

        # When
        serialized = serialize_booking_minimal(booking)

        # Then
        assert serialized == {
            "amount": 1.0,
            "isCancelled": booking.isCancelled,
            "id": humanize(booking.id),
            "stockId": humanize(booking.stockId),
            "quantity": 1,
            "stock": {
                "price": 10,
            },
            "token": "GQTQR9",
            "completedUrl": None,
            "activationCode": None,
            "qrCode": booking.qrCode,
        }

    def test_should_return_booking_with_activation_code(self):
        # Given
        stocks = StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2030, 2, 5, 9, 0, 0))
        activation_code = stocks.activationCodes[0]
        booking = BookingFactory(amount=1, quantity=1, token="GQTQR9", stock__price=10, activationCode=activation_code)

        # When
        serialized = serialize_booking_minimal(booking)

        # Then
        assert serialized == {
            "amount": 1.0,
            "isCancelled": booking.isCancelled,
            "id": humanize(booking.id),
            "stockId": humanize(booking.stockId),
            "quantity": 1,
            "stock": {
                "price": 10,
            },
            "token": "GQTQR9",
            "completedUrl": None,
            "activationCode": {"code": activation_code.code, "expirationDate": activation_code.expirationDate},
            "qrCode": booking.qrCode,
        }
