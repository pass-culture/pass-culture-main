from datetime import datetime

import pandas

from models import PcObject, ThingType
from models.db import db
from repository.dashboard_queries.offerer_queries import get_first_stock_creation_dates, \
    get_first_booking_creation_dates, get_creation_dates, get_number_of_offers, \
    get_number_of_bookings_not_cancelled, get_offerers_details
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_venue, create_offer_with_thing_product, create_stock, \
    create_booking


class GetOffererCreationDatesTest:
    @clean_database
    def test_should_return_offerer_s_creation_date(self, app):
        # Given
        creation_date = datetime(2019, 9, 20, 12, 0, 0)
        offerer = create_offerer(date_created=creation_date)
        PcObject.save(offerer)
        connection = db.engine.connect()

        # When
        creation_dates = get_creation_dates(connection)

        # Then
        assert creation_dates.loc[offerer.id, "Date de création"] == creation_date


class GetFirstStockCreationDatesTest:
    @clean_database
    def test_should_return_the_creation_date_of_the_offer_s_first_stock(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock_1 = create_stock(offer=offer, price=0)
        date_before_first_save = datetime.utcnow()
        PcObject.save(stock_1)
        date_before_second_save = datetime.utcnow()
        stock_2 = create_stock(offer=offer, price=0)
        PcObject.save(stock_2)
        connection = db.engine.connect()

        # When
        first_stock_dates = get_first_stock_creation_dates(connection)

        # Then
        assert date_before_first_save < first_stock_dates.loc[offerer.id, "Date de création du premier stock"] < date_before_second_save

    @clean_database
    def test_should_return_None_if_the_offerer_has_no_stock(self, app):
        # Given
        offerer = create_offerer()
        PcObject.save(offerer)
        connection = db.engine.connect()

        # When
        first_stock_dates = get_first_stock_creation_dates(connection)

        # Then
        assert first_stock_dates.loc[offerer.id, "Date de création du premier stock"] is None


class GetFirstBookingCreationDatesTest:
    @clean_database
    def test_should_return_the_creation_date_of_the_offer_s_first_booking(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        first_booking_date = datetime(2019, 9, 20, 12, 0, 0)
        second_booking_date = datetime(2019, 9, 22, 12, 0, 0)
        booking_1 = create_booking(user, stock, date_created=first_booking_date)
        booking_2 = create_booking(user, stock, date_created=second_booking_date)
        PcObject.save(booking_1, booking_2)
        connection = db.engine.connect()

        # When
        first_booking_dates = get_first_booking_creation_dates(connection)

        # Then
        assert first_booking_dates.loc[offerer.id, "Date de première réservation"] == first_booking_date

    @clean_database
    def test_should_return_None_if_the_offerer_has_no_booking(self, app):
        # Given
        offerer = create_offerer()
        PcObject.save(offerer)
        connection = db.engine.connect()

        # When
        first_booking_dates = get_first_booking_creation_dates(connection)

        # Then
        assert first_booking_dates.loc[offerer.id, "Date de première réservation"] is None


class GetNumberOfOffersTest:
    @clean_database
    def test_should_return_the_number_of_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_1 = create_offer_with_thing_product(venue)
        offer_2 = create_offer_with_thing_product(venue)
        PcObject.save(offer_1, offer_2)
        connection = db.engine.connect()

        # When
        number_of_offers = get_number_of_offers(connection)

        # Then
        assert number_of_offers.loc[offerer.id, "Nombre d’offres"] == 2


    @clean_database
    def test_should_return_zero_if_the_offerer_has_no_offer(self, app):
        # Given
        offerer = create_offerer()
        PcObject.save(offerer)
        connection = db.engine.connect()

        # When
        number_of_offers = get_number_of_offers(connection)

        # Then
        assert number_of_offers.loc[offerer.id, "Nombre d’offres"] == 0


class GetNumberOfBookingsNotCancelledTest:
    @clean_database
    def test_should_return_the_number_of_bookings_not_cancelled(self, app):
        # Given
        user_1 = create_user()
        user_2 = create_user(email='user+plus@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking_1 = create_booking(user_1, stock)
        booking_2 = create_booking(user_2, stock)
        booking_3 = create_booking(user_2, stock, is_cancelled=True)
        PcObject.save(booking_1, booking_2, booking_3)
        connection = db.engine.connect()

        # When
        number_of_bookings_not_cancelled = get_number_of_bookings_not_cancelled(connection)

        # Then
        assert number_of_bookings_not_cancelled.loc[offerer.id, "Nombre de réservations non annulées"] == 2


    @clean_database
    def test_should_return_zero_if_the_offerer_has_no_booking(self, app):
        # Given
        offerer = create_offerer()
        PcObject.save(offerer)
        connection = db.engine.connect()

        # When
        number_of_bookings_not_cancelled = get_number_of_bookings_not_cancelled(connection)

        # Then
        assert number_of_bookings_not_cancelled.loc[offerer.id, "Nombre de réservations non annulées"] == 0


class GetOfferersDetailsTest:
    @clean_database
    def test_should_return_values_for_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=True, departement_code="93",
                            date_created=datetime(2019, 1, 1, 12, 0, 0), needs_to_fill_cultural_survey=True)
        date_creation_offerer_1 = datetime(2019, 1, 1, 12, 0, 0)
        date_creation_offerer_2 = datetime(2019, 1, 2, 12, 0, 0)
        offerer_1 = create_offerer(date_created=date_creation_offerer_1)
        offerer_2 = create_offerer(siren='987654321',date_created=date_creation_offerer_2)
        venue = create_venue(offerer_1)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO)
        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.AUDIOVISUEL)
        offer3 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock1 = create_stock(price=0, offer=offer1)
        stock2 = create_stock(price=0, offer=offer2)
        stock3 = create_stock(price=0, offer=offer3)
        date_creation_booking_1 = datetime(2019, 3, 7)
        booking1 = create_booking(user, stock1, date_created=date_creation_booking_1)
        date_before_first_save = datetime.utcnow()
        PcObject.save(booking1, offerer_2)
        booking2 = create_booking(user, stock2, date_created=datetime(2019, 4, 7))
        booking3 = create_booking(user, stock3, date_created=datetime(2019, 5, 7), is_cancelled=True)
        date_before_second_save = datetime.utcnow()
        PcObject.save(booking2, booking3)

        # When
        offerers_details = get_offerers_details()

        # Then
        assert offerers_details.shape == (2, 5)
        assert offerers_details.loc[offerer_1.id, "Date de création"] == date_creation_offerer_1
        assert offerers_details.loc[offerer_2.id, "Date de création"] == date_creation_offerer_2
        assert date_before_first_save < offerers_details.loc[offerer_1.id, "Date de création du premier stock"] < date_before_second_save
        assert pandas.isnull(offerers_details.loc[offerer_2.id, "Date de création du premier stock"])
        assert offerers_details.loc[offerer_1.id, "Date de première réservation"] == date_creation_booking_1
        assert pandas.isnull(offerers_details.loc[offerer_2.id, "Date de première réservation"])
        assert offerers_details.loc[offerer_1.id, "Nombre d’offres"] == 3
        assert offerers_details.loc[offerer_2.id, "Nombre d’offres"] == 0
        assert offerers_details.loc[offerer_1.id, "Nombre de réservations non annulées"] == 2
        assert offerers_details.loc[offerer_2.id, "Nombre de réservations non annulées"] == 0
