from datetime import datetime

import pandas

from models import PcObject, ThingType
from models.db import db
from repository.okr_queries import get_all_beneficiary_users_details, get_experimentation_session_column, \
    get_department_column, get_activation_date_column
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_venue, create_offer_with_thing_product, create_stock, \
    create_booking


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
        user1 = create_user(can_book_free_offers=True, departement_code='93', date_created=datetime(2019, 1, 1, 12, 0, 0))
        user2 = create_user(can_book_free_offers=True, departement_code='08', email='em@a.il')
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking = create_booking(user2, stock, is_used=False)
        PcObject.save(user1, booking)
        booking.isUsed = True
        PcObject.save(booking)
        date_after_used = datetime.utcnow()

        # When
        experimentation_users = get_all_beneficiary_users_details()

        # Then
        assert experimentation_users.shape == (2, 3)

        assert experimentation_users.loc[0].equals(
            pandas.Series(data=[2, "93", user1.dateCreated], index=["Vague d'expérimentation", "Département", "Date d'activation"]))
        assert experimentation_users.loc[1, ["Vague d'expérimentation", "Département"]].equals(
            pandas.Series(data=[1, "08"], index=["Vague d'expérimentation", "Département"]))
        assert beginning_test_date < experimentation_users.loc[1, "Date d'activation"] < date_after_used


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
