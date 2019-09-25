from datetime import datetime

import pandas

from models import PcObject, ThingType
from models.db import db
from repository.okr_queries import get_all_beneficiary_users_details, get_experimentation_session_column, \
    get_department_column
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
        user1 = create_user(can_book_free_offers=True, departement_code='93', date_created=datetime(2019, 1, 1,))
        user2 = create_user(can_book_free_offers=True, departement_code='08', email='em@a.il')
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking = create_booking(user2, stock, is_used=True)
        PcObject.save(user1, booking)

        # When
        experimentation_users = get_all_beneficiary_users_details()
        # Then
        assert experimentation_users.shape == (2, 2)

        assert experimentation_users.loc[1, "Vague d'expérimentation"] == 1
        assert experimentation_users.loc[1, "Département"] == "08"

        assert experimentation_users.loc[0, "Vague d'expérimentation"] == 2
        assert experimentation_users.loc[0, "Département"] == "93"


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
