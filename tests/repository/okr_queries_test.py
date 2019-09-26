from datetime import datetime

import pandas

from models import PcObject, ThingType
from models.db import db
from repository.okr_queries import get_all_beneficiary_users_details, get_experimentation_session_column, \
    get_department_column, get_activation_date_column, get_typeform_filling_date, get_first_connection, \
    get_first_booking
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
        experimentation_users = get_all_beneficiary_users_details()
        # Then
        assert experimentation_users.empty

    @clean_database
    def test_should_return_values_for_users_who_can_book_free_offers(self, app):
        # Given
        beginning_test_date = datetime.now()
        user1 = create_user(can_book_free_offers=True, departement_code='93', date_created=datetime(2019, 1, 1, 12, 0, 0), needs_to_fill_cultural_survey=True)
        user2 = create_user(can_book_free_offers=True, departement_code='08', email='em@a.il', needs_to_fill_cultural_survey=True)
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock_activation = create_stock(offer=activation_offer, price=0)
        booking_activation = create_booking(user2, stock_activation, is_used=False)
        offer = create_offer_with_thing_product(venue)
        recommendation = create_recommendation(offer, user2, date_created=datetime(2019, 2, 3))
        stock = create_stock(price=0, offer=offer)
        booking = create_booking(user2, stock, date_created=datetime(2019, 3, 7))
        PcObject.save(user1, booking_activation, recommendation, booking)
        booking_activation.isUsed = True
        user2.needsToFillCulturalSurvey = False
        PcObject.save(booking_activation, user2)
        date_after_changes = datetime.utcnow()

        # When
        experimentation_users = get_all_beneficiary_users_details()

        # Then
        assert experimentation_users.shape == (2, 6)

        assert experimentation_users.loc[0].equals(
            pandas.Series(
                data=[2, "93", user1.dateCreated, pandas.NaT, pandas.NaT, pandas.NaT],
                index=["Vague d'expérimentation", "Département", "Date d'activation", "Date de remplissage du typeform", "Date de première connection", "Date de première réservation"]
            )
        )
        assert experimentation_users.loc[1, ["Vague d'expérimentation", "Département", "Date de première connection", "Date de première réservation"]].equals(
            pandas.Series(
                data=[1, "08", datetime(2019, 2, 3), datetime(2019, 3, 7)],
                index=["Vague d'expérimentation", "Département", "Date de première connection", "Date de première réservation"]
            )
        )
        assert beginning_test_date < experimentation_users.loc[1, "Date d'activation"] < date_after_changes
        assert beginning_test_date < experimentation_users.loc[1, "Date de remplissage du typeform"] < date_after_changes


class GetExperimentationSessionColumnTest:
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
        experimentation_users = get_experimentation_session_column(connection)
        # Then
        assert experimentation_users["Vague d'expérimentation"].equals(
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
        experimentation_users = get_experimentation_session_column(connection)
        # Then
        assert experimentation_users["Vague d'expérimentation"].equals(
            pandas.Series(data=[2], name="Vague d'expérimentation", index=[user.id]))

    @clean_database
    def test_should_be_a_dataframe_with_2_if_user_does_not_have_activation_booking(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_experimentation_session_column(connection)

        # Then
        assert experimentation_users["Vague d'expérimentation"].equals(
            pandas.Series(data=[2], name="Vague d'expérimentation", index=[user.id]))

    @clean_database
    def test_should_return_an_empty_dataframe_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_experimentation_session_column(connection)

        # Then
        assert experimentation_users["Vague d'expérimentation"].empty


class GetDepartmentColumnTest:
    @clean_database
    def test_should_return_user_departement_code_when_user_can_book_free_offer(self, app):
        # Given
        user = create_user(departement_code='01')
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_department_column(connection)
        # Then
        assert experimentation_users['Département'].equals(
            pandas.Series(data=['01'], name='Département', index=[user.id]))

    @clean_database
    def test_should_return_empty_dataframe_when_user_cannot_book_free_offer(self, app):
        # Given
        user = create_user(departement_code='01', can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_department_column(connection)
        # Then
        assert experimentation_users['Département'].empty


class GetActivationDateColumnTest:
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
        experimentation_users = get_activation_date_column(connection)

        # Then
        assert beginning_test_date < experimentation_users.loc[user.id, 'Date d\'activation'] < date_after_used

    @clean_database
    def test_should_return_date_created_for_user_when_no_activation_booking(self, app):
        # Given
        user = create_user(date_created=datetime(2019, 8, 31))
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_activation_date_column(connection)

        # Then
        assert experimentation_users['Date d\'activation'].equals(
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
        experimentation_users = get_activation_date_column(connection)

        # Then
        assert experimentation_users['Date d\'activation'].equals(
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
        experimentation_users = get_activation_date_column(connection)

        # Then
        assert experimentation_users['Date d\'activation'].empty

class GetTypeformFillingDateTest:
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
        experimentation_users = get_typeform_filling_date(connection)

        # Then
        assert beginning_test_date < experimentation_users.loc[
            user.id, 'Date de remplissage du typeform'] < date_after_used

    @clean_database
    def test_returns_none_when_has_filled_cultural_survey_never_updated_to_false(self, app):
        # Given
        user = create_user(needs_to_fill_cultural_survey=True)
        PcObject.save(user)
        connection = db.engine.connect()


        # When
        experimentation_users = get_typeform_filling_date(connection)

        # Then
        assert experimentation_users.loc[user.id, 'Date de remplissage du typeform'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()


        # When
        experimentation_users = get_typeform_filling_date(connection)

        # Then
        assert experimentation_users.empty


class GetFirstConnectionTest:
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
        experimentation_users = get_first_connection(connection)

        # Then
        assert experimentation_users.loc[user.id, 'Date de première connection'] == datetime(2019, 1, 1)

    @clean_database
    def test_returns_none_if_no_recommendation(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_first_connection(connection)

        # Then
        assert experimentation_users.loc[user.id, 'Date de première connection'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_first_connection(connection)

        # Then
        assert experimentation_users.empty

class GetFirstBookingTest:
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
        experimentation_users = get_first_booking(connection)

        # Then
        assert experimentation_users.loc[user.id, 'Date de première réservation'] == first_booking_date

    @clean_database
    def test_returns_none_if_user_has_not_booked(self, app):
        # Given
        user = create_user()
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_first_booking(connection)

        # Then
        print(experimentation_users)
        assert experimentation_users.loc[user.id, 'Date de première réservation'] is None

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
        experimentation_users = get_first_booking(connection)

        # Then
        assert experimentation_users.loc[user.id, 'Date de première réservation'] is None

    @clean_database
    def test_returns_empty_series_if_user_cannot_book_free_offers(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        PcObject.save(user)
        connection = db.engine.connect()

        # When
        experimentation_users = get_first_booking(connection)

        # Then
        assert experimentation_users.empty
