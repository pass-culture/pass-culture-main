from datetime import datetime

import pandas

from models import PcObject, ThingType
from models.db import db
from repository.okr_queries import get_all_beneficiary_users_details, get_experimentation_sessions, \
    get_departments, get_activation_dates, get_typeform_filling_dates, get_first_connection_dates, \
    get_number_of_first_bookings, get_number_of_second_bookings, get_number_of_bookings_on_third_product_type, get_last_recommendation_date, \
    get_number_of_bookings, get_number_of_non_cancelled_bookings
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_venue, create_offer_with_thing_product, create_stock, \
    create_booking, create_recommendation


class GetAllExperimentationUsersDetailsTest:
    @clean_database
    def test_should_not_return_details_for_users_who_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)

        # When
        experimentation_users_details = get_all_beneficiary_users_details()
        # Then
        assert experimentation_users_details.empty

    @clean_database
    def test_should_return_values_for_users_who_can_book_free_offers(self, app):
        # Given
        beginning_test_date = datetime.now()
        user1 = create_user(can_book_free_offers=True, departement_code='93',
                            date_created=datetime(2019, 1, 1, 12, 0, 0), needs_to_fill_cultural_survey=True)
        user2 = create_user(can_book_free_offers=True, departement_code='08', email='em@a.il',
                            needs_to_fill_cultural_survey=True)
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock_activation = create_stock(offer=activation_offer, price=0)
        booking_activation = create_booking(user2, stock_activation, is_used=False)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO)
        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.AUDIOVISUEL)
        offer3 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        recommendation = create_recommendation(offer1, user2, date_created=datetime(2019, 2, 3))
        stock1 = create_stock(price=0, offer=offer1)
        stock2 = create_stock(price=0, offer=offer2)
        stock3 = create_stock(price=0, offer=offer3)
        booking1 = create_booking(user2, stock1, date_created=datetime(2019, 3, 7))
        booking2 = create_booking(user2, stock2, date_created=datetime(2019, 4, 7))
        booking3 = create_booking(user2, stock3, date_created=datetime(2019, 5, 7), is_cancelled=True)
        PcObject.save(user1, booking_activation, recommendation, booking1, booking2, booking3)
        booking_activation.isUsed = True
        user2.needsToFillCulturalSurvey = False
        recommendation = create_recommendation(offer3, user2)
        PcObject.save(booking_activation, user2, recommendation)
        date_after_changes = datetime.utcnow()

        expected_first_row = pandas.Series(
            data=[2, "93", user1.dateCreated, pandas.NaT, pandas.NaT, pandas.NaT, pandas.NaT, pandas.NaT, pandas.NaT, 0,
                  0],
            index=["Vague d'expérimentation", "Département", "Date d'activation", "Date de remplissage du typeform",
                   "Date de première connection", "Date de première réservation", "Date de deuxième réservation",
                   "Date de première réservation dans 3 catégories différentes", "Date de dernière recommandation",
                   "Nombre de réservations totales", "Nombre de réservations non annulées"])
        columns_to_check_for_exact_values_in_second_row = ["Vague d'expérimentation", "Département",
                                                           "Date de première connection",
                                                           "Date de première réservation",
                                                           "Date de deuxième réservation",
                                                           "Date de première réservation dans 3 catégories différentes",
                                                           "Date de dernière recommandation",
                                                           "Nombre de réservations totales",
                                                           "Nombre de réservations non annulées"]
        expected_second_row = pandas.Series(
            data=[1, "08", datetime(2019, 2, 3), datetime(2019, 3, 7), datetime(2019, 4, 7), datetime(2019, 5, 7),
                  recommendation.dateCreated, 3, 2], index=columns_to_check_for_exact_values_in_second_row)

        # When
        experimentation_users_details = get_all_beneficiary_users_details()

        # Then
        assert experimentation_users_details.shape == (2, 11)
        assert experimentation_users_details.loc[0].equals(expected_first_row)
        assert experimentation_users_details.loc[
            1, columns_to_check_for_exact_values_in_second_row].equals(
            expected_second_row
        )
        assert beginning_test_date < experimentation_users_details.loc[1, "Date d'activation"] < date_after_changes
        assert beginning_test_date < experimentation_users_details.loc[
            1, "Date de remplissage du typeform"] < date_after_changes


class GetExperimentationSessionsTest:
    @clean_database
    def test_should_be_a_series_with_1_if_user_has_used_activation_booking(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking = create_booking(user, stock, is_used=True)
        PcObject.save(booking)
        connection = db.engine.connect()

        # When
        experimentation_sessions = get_experimentation_sessions(connection)
        # Then
        assert experimentation_sessions["Vague d'expérimentation"].equals(
            pandas.Series(data=[1], name="Vague d'expérimentation", index=[user.id]))

    @clean_database
    def test_should_be_a_series_with_2_if_user_has_unused_activation_booking(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking = create_booking(user, stock, is_used=False)
        PcObject.save(booking)
        connection = db.engine.connect()

        # When
        experimentation_sessions = get_experimentation_sessions(connection)
        # Then
        assert experimentation_sessions["Vague d'expérimentation"].equals(
            pandas.Series(data=[2], name="Vague d'expérimentation", index=[user.id]))

    @clean_database
    def test_should_be_a_dataframe_with_2_if_user_does_not_have_activation_booking(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_sessions = get_experimentation_sessions(connection)

        # Then
        assert experimentation_sessions["Vague d'expérimentation"].equals(
            pandas.Series(data=[2], name="Vague d'expérimentation", index=[user.id]))

    @clean_database
    def test_should_return_an_empty_dataframe_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_sessions = get_experimentation_sessions(connection)

        # Then
        assert experimentation_sessions["Vague d'expérimentation"].empty


class GetDepartmentsTest:
    @clean_database
    def test_should_return_user_departement_code_when_user_can_book_free_offer(self, app):
        # Given
        user = create_user(departement_code='01')
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        departements = get_departments(connection)
        # Then
        assert departements['Département'].equals(
            pandas.Series(data=['01'], name='Département', index=[user.id]))

    @clean_database
    def test_should_return_empty_dataframe_when_user_cannot_book_free_offer(self, app):
        # Given
        user = create_user(departement_code='01', can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        departements = get_departments(connection)
        # Then
        assert departements['Département'].empty


class GetActivationDateTest:
    @clean_database
    def test_should_return_date_when_activation_booking_was_used_if_it_is_used(self, app):
        # Given
        beginning_test_date = datetime.utcnow()
        user = create_user(date_created=datetime(2019, 8, 31))
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking = create_booking(user, stock)
        PcObject.save(booking)
        booking.isUsed = True
        PcObject.save(booking)
        date_after_used = datetime.utcnow()
        connection = db.engine.connect()

        # When
        activation_dates = get_activation_dates(connection)

        # Then
        assert beginning_test_date < activation_dates.loc[user.id, 'Date d\'activation'] < date_after_used

    @clean_database
    def test_should_return_date_created_for_user_when_no_activation_booking(self, app):
        # Given
        user = create_user(date_created=datetime(2019, 8, 31))
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        activation_dates = get_activation_dates(connection)

        # Then
        assert activation_dates['Date d\'activation'].equals(
            pandas.Series(data=[datetime(2019, 8, 31)], name='Date d\'activation', index=[user.id]))

    @clean_database
    def test_should_return_date_created_for_user_when_non_used_activation_booking(self, app):
        # Given
        user = create_user(date_created=datetime(2019, 8, 31))
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking = create_booking(user, stock)
        PcObject.save(booking)
        connection = db.engine.connect()

        # When
        activation_dates = get_activation_dates(connection)

        # Then
        assert activation_dates['Date d\'activation'].equals(
            pandas.Series(data=[datetime(2019, 8, 31)], name='Date d\'activation', index=[user.id]))

    @clean_database
    def test_should_return_empty_dataframe_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(date_created=datetime(2019, 8, 31), can_book_free_offers=False)
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking = create_booking(user, stock)
        PcObject.save(booking)
        connection = db.engine.connect()

        # When
        activation_dates = get_activation_dates(connection)

        # Then
        assert activation_dates['Date d\'activation'].empty


class GetTypeformFillingDatesTest:
    @clean_database
    def test_returns_date_when_has_filled_cultural_survey_was_updated_to_false(self, app):
        # Given
        beginning_test_date = datetime.utcnow()
        user = create_user(needs_to_fill_cultural_survey=True)
        PcObject.save(user)
        user.needsToFillCulturalSurvey = False
        PcObject.save(user)
        date_after_used = datetime.utcnow()
        connection = db.engine.connect()

        # When
        typeform_filling_dates = get_typeform_filling_dates(connection)

        # Then
        assert beginning_test_date < typeform_filling_dates.loc[
            user.id, 'Date de remplissage du typeform'] < date_after_used

    @clean_database
    def test_returns_none_when_has_filled_cultural_survey_never_updated_to_false(self, app):
        # Given
        user = create_user(needs_to_fill_cultural_survey=True)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        typeform_filling_dates = get_typeform_filling_dates(connection)

        # Then
        assert typeform_filling_dates.loc[user.id, 'Date de remplissage du typeform'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        typeform_filling_dates = get_typeform_filling_dates(connection)

        # Then
        assert typeform_filling_dates.empty


class GetFirstConnectionDatesTest:
    @clean_database
    def test_returns_min_recommandation_dateCreated_for_a_user_if_has_any_recommendation(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        recommendation = create_recommendation(offer, user, date_created=datetime(2019, 1, 1))
        PcObject.save(recommendation)
        connection = db.engine.connect()

        # When
        first_connections = get_first_connection_dates(connection)

        # Then
        assert first_connections.loc[user.id, 'Date de première connection'] == datetime(2019, 1, 1)

    @clean_database
    def test_returns_none_if_no_recommendation(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        first_connections = get_first_connection_dates(connection)

        # Then
        assert first_connections.loc[user.id, 'Date de première connection'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        first_connections = get_first_connection_dates(connection)

        # Then
        assert first_connections.empty


class GetNumberOfFirstBookingsTest:
    @clean_database
    def test_returns_booking_date_created_if_user_has_booked(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        first_booking_date = datetime(2019, 9, 19, 12, 0, 0)
        booking = create_booking(user, stock, date_created=first_booking_date)
        PcObject.save(booking)
        connection = db.engine.connect()

        # When
        first_bookings = get_number_of_first_bookings(connection)

        # Then
        assert first_bookings.loc[user.id, 'Date de première réservation'] == first_booking_date

    @clean_database
    def test_returns_none_if_user_has_not_booked(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        first_bookings = get_number_of_first_bookings(connection)

        # Then
        print(first_bookings)
        assert first_bookings.loc[user.id, 'Date de première réservation'] is None

    @clean_database
    def test_returns_none_if_booking_on_activation_offer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing_type='ThingType.ACTIVATION')
        stock = create_stock(offer=offer, price=0)
        first_booking_date = datetime(2019, 9, 19, 12, 0, 0)
        booking = create_booking(user, stock, date_created=first_booking_date)
        PcObject.save(booking)
        connection = db.engine.connect()

        # When
        firts_bookings = get_number_of_first_bookings(connection)

        # Then
        assert firts_bookings.loc[user.id, 'Date de première réservation'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        first_bookings = get_number_of_first_bookings(connection)

        # Then
        assert first_bookings.empty


class GetNumberOfSecondBookingsTest:
    @clean_database
    def test_returns_date_created_of_second_booking_if_exists(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        first_booking_date = datetime(2019, 9, 19, 12, 0, 0)
        second_booking_date = datetime(2019, 9, 22, 12, 0, 0)
        first_booking = create_booking(user, stock, date_created=first_booking_date)
        second_booking = create_booking(user, stock, date_created=second_booking_date)
        PcObject.save(first_booking, second_booking)
        connection = db.engine.connect()

        # When
        second_bookings = get_number_of_second_bookings(connection)

        # Then
        assert second_bookings.loc[user.id, 'Date de deuxième réservation'] == second_booking_date

    @clean_database
    def test_returns_None_if_user_has_only_one_booking(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        first_booking_date = datetime(2019, 9, 19, 12, 0, 0)
        booking = create_booking(user, stock, date_created=first_booking_date)
        PcObject.save(booking)
        connection = db.engine.connect()

        # When
        second_bookings = get_number_of_second_bookings(connection)

        # Then
        assert second_bookings.loc[user.id, 'Date de deuxième réservation'] is None

    @clean_database
    def test_returns_None_if_booking_on_activation_offer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type='ThingType.ACTIVATION')
        activation_stock = create_stock(offer=activation_offer, price=0)
        first_booking_date = datetime(2019, 9, 19, 12, 0, 0)
        activation_booking = create_booking(user, activation_stock, date_created=first_booking_date)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        first_booking_date = datetime(2019, 9, 20, 12, 0, 0)
        booking = create_booking(user, stock, date_created=first_booking_date)
        PcObject.save(activation_booking, booking)
        connection = db.engine.connect()

        # When
        second_bookings = get_number_of_second_bookings(connection)

        # Then
        assert second_bookings.loc[user.id, 'Date de deuxième réservation'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        second_bookings = get_number_of_second_bookings(connection)

        # Then
        assert second_bookings.empty


class GetNumberOfBookingsOnThirdProductTypeTest:
    @clean_database
    def test_returns_date_created_of_first_booking_on_more_than_three_types(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_cinema = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock_cinema = create_stock(offer=offer_cinema, price=0)
        booking_date_cinema = datetime(2019, 9, 19, 12, 0, 0)
        booking_cinema = create_booking(user, stock_cinema, date_created=booking_date_cinema)
        offer_audiovisuel = create_offer_with_thing_product(venue, thing_type=ThingType.AUDIOVISUEL)
        stock_audiovisuel = create_stock(offer=offer_audiovisuel, price=0)
        booking_date_audiovisuel = datetime(2019, 9, 20, 12, 0, 0)
        booking_audiovisuel = create_booking(user, stock_audiovisuel, date_created=booking_date_audiovisuel)
        offer_jeux_video1 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO)
        stock_jeux_video1 = create_stock(offer=offer_jeux_video1, price=0)
        booking_date_jeux_video1 = datetime(2019, 9, 21, 12, 0, 0)
        booking_jeux_video1 = create_booking(user, stock_jeux_video1, date_created=booking_date_jeux_video1)
        offer_jeux_video2 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO)
        stock_jeux_video2 = create_stock(offer=offer_jeux_video2, price=0)
        booking_date_jeux_video2 = datetime(2019, 9, 21, 12, 0, 0)
        booking_jeux_video2 = create_booking(user, stock_jeux_video2, date_created=booking_date_jeux_video2)
        PcObject.save(booking_cinema, booking_audiovisuel, booking_jeux_video1, booking_jeux_video2)
        connection = db.engine.connect()

        # When
        bookings_on_third_product_type = get_number_of_bookings_on_third_product_type(connection)

        # Then
        assert bookings_on_third_product_type.loc[
                   user.id, 'Date de première réservation dans 3 catégories différentes'] == booking_date_jeux_video1

    @clean_database
    def test_does_not_count_type_activation(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_cinema = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock_cinema = create_stock(offer=offer_cinema, price=0)
        booking_date_cinema = datetime(2019, 9, 19, 12, 0, 0)
        booking_cinema = create_booking(user, stock_cinema, date_created=booking_date_cinema)
        offer_audiovisuel = create_offer_with_thing_product(venue, thing_type=ThingType.AUDIOVISUEL)
        stock_audiovisuel = create_stock(offer=offer_audiovisuel, price=0)
        booking_date_audiovisuel = datetime(2019, 9, 20, 12, 0, 0)
        booking_audiovisuel = create_booking(user, stock_audiovisuel, date_created=booking_date_audiovisuel)
        offer_activation = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock_activation = create_stock(offer=offer_activation, price=0)
        booking_date_activation = datetime(2019, 9, 21, 12, 0, 0)
        booking_activation = create_booking(user, stock_activation, date_created=booking_date_activation)
        PcObject.save(booking_cinema, booking_audiovisuel, booking_activation)
        connection = db.engine.connect()

        # When
        bookings_on_third_product_type = get_number_of_bookings_on_third_product_type(connection)

        # Then
        assert bookings_on_third_product_type.loc[user.id, 'Date de première réservation dans 3 catégories différentes'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        bookings_on_third_product_type = get_number_of_bookings_on_third_product_type(connection)

        # Then
        assert bookings_on_third_product_type.empty


class GetLastRecommendationDateTest:
    @clean_database
    def test_returns_max_recommandation_dateCreated_for_a_user_if_has_any_recommendation(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        recommendation1 = create_recommendation(offer, user)
        PcObject.save(recommendation1)
        date_after_first_recommendation = datetime.utcnow()
        recommendation2 = create_recommendation(offer, user)
        PcObject.save(recommendation2)
        date_after_second_recommendation = datetime.utcnow()
        connection = db.engine.connect()

        # When
        last_recommendation_dates = get_last_recommendation_date(connection)

        # Then
        assert date_after_first_recommendation < last_recommendation_dates.loc[
            user.id, 'Date de dernière recommandation'] < date_after_second_recommendation

    @clean_database
    def test_returns_none_if_no_recommendation(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        last_recommendation_dates = get_last_recommendation_date(connection)

        # Then
        assert last_recommendation_dates.loc[user.id, 'Date de dernière recommandation'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        last_recommendation_dates = get_last_recommendation_date(connection)

        # Then
        assert last_recommendation_dates.empty


class GetNumberOfBookingsTest:
    @clean_database
    def test_returns_number_of_bookings_for_user_ignoring_activation_for_cancelled_or_non_cancelled_bookings(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_cinema = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock_cinema = create_stock(offer=offer_cinema, price=0)
        booking_cinema = create_booking(user, stock_cinema)
        offer_audiovisuel = create_offer_with_thing_product(venue, thing_type=ThingType.AUDIOVISUEL)
        stock_audiovisuel = create_stock(offer=offer_audiovisuel, price=0)
        booking_audiovisuel = create_booking(user, stock_audiovisuel, is_cancelled=True)
        offer_activation = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock_activation = create_stock(offer=offer_activation, price=0)
        booking_activation = create_booking(user, stock_activation)
        PcObject.save(booking_cinema, booking_audiovisuel, booking_activation)
        connection = db.engine.connect()

        # When
        bookings = get_number_of_bookings(connection)

        # Then
        assert bookings.loc[user.id, 'Nombre de réservations totales'] == 2

    @clean_database
    def test_returns_None_if_no_booking(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        bookings = get_number_of_bookings(connection)

        # Then
        assert bookings.loc[user.id, 'Nombre de réservations totales'] == 0

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        bookings = get_number_of_bookings(connection)

        # Then
        assert bookings.empty


class GetNumberOfNonCancelledBookingsTest:
    @clean_database
    def test_returns_number_of_bookings_for_user_ignoring_activation_for_cancelled_bookings(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_non_cancelled = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock_non_cancelled = create_stock(offer=offer_non_cancelled, price=0)
        booking_non_cancelled = create_booking(user, stock_non_cancelled)
        offer_cancelled = create_offer_with_thing_product(venue, thing_type=ThingType.AUDIOVISUEL)
        stock_cancelled = create_stock(offer=offer_cancelled, price=0)
        booking_cancelled = create_booking(user, stock_cancelled, is_cancelled=True)
        offer_cancelled2 = create_offer_with_thing_product(venue, thing_type=ThingType.AUDIOVISUEL)
        stock_cancelled2 = create_stock(offer=offer_cancelled2, price=0)
        booking_cancelled2 = create_booking(user, stock_cancelled2, is_cancelled=True)
        offer_activation = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock_activation = create_stock(offer=offer_activation, price=0)
        booking_activation = create_booking(user, stock_activation)
        PcObject.save(booking_non_cancelled, booking_cancelled, booking_activation, booking_cancelled2)
        connection = db.engine.connect()

        # When
        non_cancelled_bookings = get_number_of_non_cancelled_bookings(connection)

        # Then
        assert non_cancelled_bookings.loc[user.id, 'Nombre de réservations non annulées'] == 1

    @clean_database
    def test_returns_0_if_no_booking(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        non_cancelled_bookings = get_number_of_non_cancelled_bookings(connection)

        # Then
        assert non_cancelled_bookings.loc[user.id, 'Nombre de réservations non annulées'] == 0

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        non_cancelled_bookings = get_number_of_non_cancelled_bookings(connection)

        # Then
        assert non_cancelled_bookings.empty
