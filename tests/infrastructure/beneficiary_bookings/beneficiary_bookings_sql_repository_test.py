from datetime import datetime, timedelta

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBookings
from infrastructure.repository.beneficiary_bookings.beneficiary_bookings_sql_repository import \
    BeneficiaryBookingsSQLRepository, _get_stocks_information
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_stock, \
    create_booking, create_deposit, create_recommendation
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product


class BeneficiaryBookingsSQLRepositoryTest:
    @clean_database
    def should_return_beneficiary_bookings_with_expected_information(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, url='http://url.com')
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock, token='ABCDEF',
                                 date_created=datetime(2020, 4, 22, 0, 0),
                                 date_used=datetime(2020, 5, 5, 0, 0),
                                 is_used=True,
                                 quantity=2)
        repository.save(booking)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert isinstance(result, BeneficiaryBookings)
        assert len(result.bookings) == 1
        expected_booking = result.bookings[0]
        assert expected_booking.amount == 0.0
        assert expected_booking.cancellationDate is None
        assert expected_booking.dateCreated == datetime(2020, 4, 22, 0, 0)
        assert expected_booking.dateUsed == datetime(2020, 5, 5, 0, 0)
        assert expected_booking.id == booking.id
        assert expected_booking.isCancelled is False
        assert expected_booking.isUsed is True
        assert expected_booking.quantity == 2
        assert expected_booking.recommendationId is None
        assert expected_booking.stockId == stock.id
        assert expected_booking.token == booking.token
        assert expected_booking.userId == user.id
        assert expected_booking.offerId == offer.id
        assert expected_booking.name == offer.name
        assert expected_booking.type == offer.type
        assert expected_booking.url == offer.url
        assert expected_booking.email == user.email
        assert expected_booking.beginningDatetime == stock.beginningDatetime
        assert expected_booking.venueId == venue.id
        assert expected_booking.departementCode == venue.departementCode

    @clean_database
    def should_return_bookings_by_beneficiary_id(self, app):
        # Given
        user1 = create_user()
        create_deposit(user1)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        user2 = create_user(email='fa@example.com')
        create_deposit(user2)
        booking1 = create_booking(user=user1, stock=stock)
        booking2 = create_booking(user=user2, stock=stock)
        repository.save(booking1, booking2)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user1.id)

        # Then
        assert len(result.bookings) == 1
        assert result.bookings[0].id == booking1.id

    @clean_database
    def should_not_return_activation_bookings(self, app):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_event_product(
            venue, event_type='ThingType.ACTIVATION')
        offer2 = create_offer_with_event_product(
            venue, event_type='EventType.ACTIVATION')
        offer3 = create_offer_with_event_product(
            venue, event_type='ThingType.ANY')
        stock1 = create_stock(offer=offer1)
        stock2 = create_stock(offer=offer2)
        stock3 = create_stock(offer=offer3)
        booking1 = create_booking(user=user, stock=stock1)
        booking2 = create_booking(user=user, stock=stock2)
        booking3 = create_booking(user=user, stock=stock3)
        repository.save(booking1, booking2, booking3)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert len(result.bookings) == 1
        assert result.bookings[0].id == booking3.id

    @clean_database
    def should_return_only_most_recent_booking_when_two_cancelled_on_same_stock(self, app):
        # Given
        now = datetime.utcnow()
        two_days_ago = now - timedelta(days=2)
        three_days_ago = now - timedelta(days=3)
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        booking1 = create_booking(user=user, date_created=two_days_ago, is_cancelled=True, stock=stock)
        booking2 = create_booking(user=user, date_created=three_days_ago, is_cancelled=True, stock=stock)
        repository.save(booking1, booking2)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert len(result.bookings) == 1
        assert result.bookings[0].id == booking1.id

    @clean_database
    def should_return_most_recent_bookings_first(self, app):
        # Given
        now = datetime.utcnow()
        two_days = now + timedelta(days=2, hours=10)
        two_days_bis = now + timedelta(days=2, hours=20)
        three_days = now + timedelta(days=3)
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_event_product(venue)
        stock1 = create_stock(booking_limit_datetime=now, beginning_datetime=three_days, offer=offer1)
        offer2 = create_offer_with_event_product(venue)
        stock2 = create_stock(booking_limit_datetime=now, beginning_datetime=two_days, offer=offer2)
        offer3 = create_offer_with_event_product(venue)
        stock3 = create_stock(booking_limit_datetime=now, beginning_datetime=two_days_bis, offer=offer3)
        booking1 = create_booking(user=user, stock=stock1,
                                  recommendation=create_recommendation(user=user, offer=offer1))
        booking2 = create_booking(user=user, stock=stock2,
                                  recommendation=create_recommendation(user=user, offer=offer2))
        booking3 = create_booking(user=user, stock=stock3,
                                  recommendation=create_recommendation(user=user, offer=offer3))
        repository.save(booking1, booking2, booking3)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert len(result.bookings) == 3
        assert result.bookings[0].id == booking1.id
        assert result.bookings[1].id == booking3.id
        assert result.bookings[2].id == booking2.id


class GetStocksInformationTest:
    @clean_database
    def should_return_get_stocks_information(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, url='http://url.com')
        stock1 = create_stock(offer=offer, price=0,
                              date_created=datetime(2020, 1, 4),
                              beginning_datetime=datetime(2020, 3, 5),
                              booking_limit_datetime=datetime(2020, 1, 6),
                              date_modified=datetime(2020, 1, 7))
        stock2 = create_stock(offer=offer, price=12,
                              date_created=datetime(2020, 2, 4),
                              beginning_datetime=datetime(2020, 4, 5),
                              booking_limit_datetime=datetime(2020, 2, 6),
                              date_modified=datetime(2020, 2, 7))

        repository.save(stock1, stock2)

        # When
        results = _get_stocks_information(offers_ids=[offer.id])

        # Then
        assert set(results) == {
            (datetime(2020, 1, 4, 0, 0),
             datetime(2020, 3, 5, 0, 0),
             datetime(2020, 1, 6, 0, 0),
             datetime(2020, 1, 7, 0, 0),
             offer.id,
             None,
             0.00,
             stock1.id,
             False,
             True),
            (datetime(2020, 2, 4, 0, 0),
             datetime(2020, 4, 5, 0, 0),
             datetime(2020, 2, 6, 0, 0),
             datetime(2020, 2, 7, 0, 0),
             offer.id,
             None,
             12.00,
             stock2.id,
             False,
             True)
        }
