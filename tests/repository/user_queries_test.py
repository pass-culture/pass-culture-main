from datetime import MINYEAR
from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.model_creators.generic_creators import create_beneficiary_import
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import BeneficiaryImportSources
from pcapi.models import ImportStatus
from pcapi.repository import repository
from pcapi.repository.user_queries import find_by_civility
from pcapi.repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from pcapi.repository.user_queries import get_all_users_wallet_balances


class GetAllUsersWalletBalancesTest:
    @pytest.mark.usefixtures("db_session")
    def test_users_are_sorted_by_user_id(self, app):
        # given
        user1 = create_user(email="user1@example.com")
        user2 = create_user(email="user2@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer, price=20)
        stock2 = create_stock(offer=offer, price=30)
        stock3 = create_stock(offer=offer, price=40)
        repository.save(stock1, stock2, stock3, user1, user2)

        _create_balances_for_user2(stock3, user2, venue)
        _create_balances_for_user1(stock1, stock2, stock3, user1, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert len(balances) == 2
        assert balances[0].user_id < balances[1].user_id

    @pytest.mark.usefixtures("db_session")
    def test_users_with_no_deposits_are_ignored(self, app):
        # given
        user1 = create_user(email="user1@example.com")
        user2 = create_user(email="user2@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock3 = create_stock(offer=offer, price=40)
        repository.save(stock3, user1, user2)

        _create_balances_for_user2(stock3, user2, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert len(balances) == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_current_balances(self, app):
        # given
        user1 = create_user(email="user1@example.com")
        user2 = create_user(email="user2@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer, price=20)
        stock2 = create_stock(offer=offer, price=30)
        stock3 = create_stock(offer=offer, price=40)
        repository.save(stock1, stock2, stock3, user1, user2)

        _create_balances_for_user1(stock1, stock2, stock3, user1, venue)
        _create_balances_for_user2(stock3, user2, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert balances[0].current_balance == 50
        assert balances[1].current_balance == 80

    @pytest.mark.usefixtures("db_session")
    def test_returns_real_balances(self, app):
        # given
        user1 = create_user(email="user1@example.com")
        user2 = create_user(email="user2@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer, price=20)
        stock2 = create_stock(offer=offer, price=30)
        stock3 = create_stock(offer=offer, price=40)
        repository.save(stock1, stock2, stock3, user1, user2)

        _create_balances_for_user1(stock1, stock2, stock3, user1, venue)
        _create_balances_for_user2(stock3, user2, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert balances[0].real_balance == 90
        assert balances[1].real_balance == 200


class FindByCivilityTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_case(self, app):
        # given
        user1 = create_user(
            date_of_birth=datetime(2000, 5, 1), email="john@example.com", first_name="john", last_name="DOe"
        )
        user2 = create_user(
            date_of_birth=datetime(2000, 3, 20), email="jane@example.com", first_name="jaNE", last_name="DOe"
        )
        repository.save(user1, user2)

        # when
        users = find_by_civility("john", "doe", datetime(2000, 5, 1))

        # then
        assert len(users) == 1
        assert users[0].email == "john@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_dash(self, app):
        # given
        user2 = create_user(
            date_of_birth=datetime(2000, 3, 20), email="jane@example.com", first_name="jaNE", last_name="DOe"
        )
        user1 = create_user(
            date_of_birth=datetime(2000, 5, 1), email="john.b@example.com", first_name="john-bob", last_name="doe"
        )
        repository.save(user1, user2)

        # when
        users = find_by_civility("johnbob", "doe", datetime(2000, 5, 1))

        # then
        assert len(users) == 1
        assert users[0].email == "john.b@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_spaces(self, app):
        # given
        user2 = create_user(
            date_of_birth=datetime(2000, 3, 20), email="jane@example.com", first_name="jaNE", last_name="DOe"
        )
        user1 = create_user(
            date_of_birth=datetime(2000, 5, 1), email="john.b@example.com", first_name="john bob", last_name="doe"
        )
        repository.save(user1, user2)

        # when
        users = find_by_civility("johnbob", "doe", datetime(2000, 5, 1))

        # then
        assert len(users) == 1
        assert users[0].email == "john.b@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_accents(self, app):
        # given
        user2 = create_user(
            date_of_birth=datetime(2000, 3, 20), email="jane@example.com", first_name="jaNE", last_name="DOe"
        )
        user1 = create_user(
            date_of_birth=datetime(2000, 5, 1), email="john.b@example.com", first_name="john bob", last_name="doe"
        )
        repository.save(user1, user2)

        # when
        users = find_by_civility("jöhn bób", "doe", datetime(2000, 5, 1))

        # then
        assert len(users) == 1
        assert users[0].email == "john.b@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_nothing_if_one_criteria_does_not_match(self, app):
        # given
        user = create_user(date_of_birth=datetime(2000, 5, 1), first_name="Jean", last_name="DOe")
        repository.save(user)

        # when
        users = find_by_civility("john", "doe", datetime(2000, 5, 1))

        # then
        assert not users

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_first_and_last_names_and_birthdate_and_invalid_email(self, app):
        # given
        user1 = create_user(
            date_of_birth=datetime(2000, 5, 1), email="john@example.com", first_name="john", last_name="DOe"
        )
        user2 = create_user(
            date_of_birth=datetime(2000, 3, 20), email="jane@example.com", first_name="jaNE", last_name="DOe"
        )
        repository.save(user1, user2)

        # when
        users = find_by_civility("john", "doe", datetime(2000, 5, 1))

        # then
        assert len(users) == 1
        assert users[0].email == "john@example.com"


class FindMostRecentBeneficiaryCreationDateByProcedureIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_created_at_date_of_most_recent_beneficiary_import_with_created_status_for_one_procedure(self, app):
        # given
        source_id = 1
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        three_days_ago = now - timedelta(days=3)

        user1 = create_user(date_created=yesterday, email="user1@example.com")
        user2 = create_user(date_created=two_days_ago, email="user2@example.com")
        user3 = create_user(date_created=three_days_ago, email="user3@example.com")
        beneficiary_import = [
            create_beneficiary_import(
                user=user2, status=ImportStatus.ERROR, date=two_days_ago, application_id=1, source_id=source_id
            ),
            create_beneficiary_import(
                user=user3, status=ImportStatus.CREATED, date=three_days_ago, application_id=3, source_id=source_id
            ),
        ]

        repository.save(user1, *beneficiary_import)

        # when
        most_recent_creation_date = find_most_recent_beneficiary_creation_date_for_source(
            BeneficiaryImportSources.demarches_simplifiees, source_id
        )

        # then
        assert most_recent_creation_date == three_days_ago

    @pytest.mark.usefixtures("db_session")
    def test_returns_min_year_if_no_beneficiary_import_exist_for_given_source_id(self, app):
        # given
        old_source_id = 1
        new_source_id = 2
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        user = create_user(date_created=yesterday, email="user@example.com")
        beneficiary_import = create_beneficiary_import(
            user=user, status=ImportStatus.CREATED, date=yesterday, application_id=3, source_id=old_source_id
        )

        repository.save(beneficiary_import)

        # when
        most_recent_creation_date = find_most_recent_beneficiary_creation_date_for_source(
            BeneficiaryImportSources.demarches_simplifiees, new_source_id
        )

        # then
        assert most_recent_creation_date == datetime(MINYEAR, 1, 1)

    @pytest.mark.usefixtures("db_session")
    def test_returns_min_year_if_no_beneficiary_import_exist(self, app):
        # given
        yesterday = datetime.utcnow() - timedelta(days=1)
        user = create_user(date_created=yesterday)
        repository.save(user)

        # when
        most_recent_creation_date = find_most_recent_beneficiary_creation_date_for_source(
            BeneficiaryImportSources.demarches_simplifiees, 1
        )

        # then
        assert most_recent_creation_date == datetime(MINYEAR, 1, 1)


def _create_balances_for_user2(stock3, user2, venue):
    deposit3 = create_deposit(user2, amount=200)
    booking4 = create_booking(user=user2, is_cancelled=False, is_used=False, quantity=3, stock=stock3, venue=venue)
    repository.save(deposit3, booking4)


def _create_balances_for_user1(stock1, stock2, stock3, user1, venue):
    deposit1 = create_deposit(user1, amount=100)
    deposit2 = create_deposit(user1, amount=50)
    booking1 = create_booking(user=user1, is_cancelled=True, is_used=False, quantity=1, stock=stock1, venue=venue)
    booking2 = create_booking(user=user1, is_cancelled=False, is_used=True, quantity=2, stock=stock2, venue=venue)
    booking3 = create_booking(user=user1, is_cancelled=False, is_used=False, quantity=1, stock=stock3, venue=venue)
    repository.save(deposit1, deposit2, booking1, booking2, booking3)
