from datetime import MINYEAR
from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import BeneficiaryImportSources
from pcapi.models import ImportStatus
from pcapi.repository import repository
from pcapi.repository.user_queries import beneficiary_by_civility_query
from pcapi.repository.user_queries import find_beneficiary_by_civility
from pcapi.repository.user_queries import find_most_recent_beneficiary_creation_date_for_source
from pcapi.repository.user_queries import find_pro_users_by_email_provider
from pcapi.repository.user_queries import get_all_users_wallet_balances


class GetAllUsersWalletBalancesTest:
    @pytest.mark.usefixtures("db_session")
    def test_users_are_sorted_by_user_id(self):
        # given
        user1 = users_factories.BeneficiaryGrant18Factory()
        user2 = users_factories.BeneficiaryGrant18Factory()

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert len(balances) == 2
        assert [b.user_id for b in balances] == [user1.id, user2.id]

    @pytest.mark.usefixtures("db_session")
    def test_users_with_no_deposits_are_ignored(self):
        # given
        user1 = users_factories.BeneficiaryGrant18Factory()
        user2 = users_factories.BeneficiaryGrant18Factory()
        repository.delete(user2.deposit)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert len(balances) == 1
        assert balances[0].user_id == user1.id

    @pytest.mark.usefixtures("db_session")
    def test_returns_both_current_and_real_balances(self):
        # given
        offer = offers_factories.OfferFactory()
        stock1 = offers_factories.StockFactory(offer=offer, price=20)
        stock2 = offers_factories.StockFactory(offer=offer, price=30)
        stock3 = offers_factories.StockFactory(offer=offer, price=40)
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1)

        bookings_factories.IndividualBookingFactory(individualBooking__user=user, stock=stock1)
        bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=user, stock=stock2)
        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, stock=stock3, quantity=2)

        # when
        balances = get_all_users_wallet_balances()

        # then
        balance = balances[0]
        assert balance.current_balance == 500 - (20 + 40 * 2)
        assert balance.real_balance == 500 - (40 * 2)


class FindProUsersByEmailProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_pro_users_with_matching_email_provider(self):
        pro_user_with_matching_email = users_factories.ProFactory(email="pro_user@suspect.com", isActive=True)
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user_with_matching_email, offerer=offerer)

        pro_user_with_not_matching_email = users_factories.ProFactory(email="pro_user@example.com", isActive=True)
        offerer2 = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user_with_not_matching_email, offerer=offerer2)

        users = find_pro_users_by_email_provider("suspect.com")

        assert len(users) == 1
        assert users[0] == pro_user_with_matching_email

    @pytest.mark.usefixtures("db_session")
    def test_returns_only_pro_users_with_matching_email_provider(self):
        pro_user_with_matching_email = users_factories.ProFactory(
            email="pro_user_with_matching_email@suspect.com", isActive=True
        )
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user_with_matching_email, offerer=offerer)

        users_factories.UserFactory(email="not_pro_with_matching_email@suspect.com", isActive=True)

        users = find_pro_users_by_email_provider("suspect.com")

        assert len(users) == 1
        assert users[0] == pro_user_with_matching_email


class FindByCivilityTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_case(self, app):
        john = users_factories.BeneficiaryGrant18Factory(email="john@example.com", firstName="john", lastName="DOe")
        users_factories.BeneficiaryGrant18Factory(email="jane@example.com", firstName="jaNE", lastName="DOe")

        users = find_beneficiary_by_civility("john", "doe", john.dateOfBirth)

        assert len(users) == 1
        assert users[0].email == "john@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_dash(self, app):
        users_factories.BeneficiaryGrant18Factory(email="jane@example.com", firstName="jaNE", lastName="DOe")
        john = users_factories.BeneficiaryGrant18Factory(
            email="john.b@example.com", firstName="john-bob", lastName="doe"
        )

        users = find_beneficiary_by_civility("johnbob", "doe", john.dateOfBirth)

        assert len(users) == 1
        assert users[0].email == "john.b@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_spaces(self, app):
        users_factories.BeneficiaryGrant18Factory(email="jane@example.com", firstName="jaNE", lastName="DOe")
        john = users_factories.BeneficiaryGrant18Factory(
            email="john.b@example.com", firstName="john bob", lastName="doe"
        )

        users = find_beneficiary_by_civility("johnbob", "doe", john.dateOfBirth)

        assert len(users) == 1
        assert users[0].email == "john.b@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_ignoring_accents(self, app):
        users_factories.BeneficiaryGrant18Factory(email="jane@example.com", firstName="jaNE", lastName="DOe")
        john = users_factories.BeneficiaryGrant18Factory(
            email="john.b@example.com", firstName="john bob", lastName="doe"
        )

        users = find_beneficiary_by_civility("jöhn bób", "doe", john.dateOfBirth)

        assert len(users) == 1
        assert users[0].email == "john.b@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_returns_nothing_if_one_criteria_does_not_match(self, app):
        john = users_factories.BeneficiaryGrant18Factory(firstName="Jean", lastName="DOe")

        users = find_beneficiary_by_civility("john", "doe", john.dateOfBirth)

        assert not users

    @pytest.mark.usefixtures("db_session")
    def test_returns_users_with_matching_criteria_first_and_last_names_and_birthdate_and_invalid_email(self, app):
        john = users_factories.BeneficiaryGrant18Factory(email="john@example.com", firstName="john", lastName="DOe")
        users_factories.BeneficiaryGrant18Factory(email="jane@example.com", firstName="jaNE", lastName="DOe")

        # when
        users = find_beneficiary_by_civility("john", "doe", john.dateOfBirth)

        # then
        assert len(users) == 1
        assert users[0].email == "john@example.com"


@pytest.mark.usefixtures("db_session")
class BeneficiaryByCivilityQueryTest:
    def test_exclude_oneself(self, app):
        # given
        email = "john@example.com"
        john = users_factories.BeneficiaryGrant18Factory(email=email, firstName="john", lastName="doe")

        # when
        user_found = beneficiary_by_civility_query("john", "doe", john.dateOfBirth).all()
        user_not_found = beneficiary_by_civility_query(
            "john", "doe", john.dateOfBirth, exclude_email=email
        ).one_or_none()

        # then
        assert len(user_found) == 1
        assert user_found[0].email == email
        assert user_not_found is None

    def test_exclude_interval(self):
        users_factories.BeneficiaryGrant18Factory(
            firstName="john", lastName="doe", dateCreated=datetime.now() - timedelta(days=50)
        )
        john = users_factories.BeneficiaryGrant18Factory(
            firstName="john", lastName="doe", dateCreated=datetime.now() - timedelta(days=30)
        )

        users_found = beneficiary_by_civility_query("john", "doe", interval=timedelta(days=40)).all()

        assert len(users_found) == 1
        assert users_found[0] == john

        users_found = beneficiary_by_civility_query("john", "doe", interval=timedelta(days=60)).all()
        assert len(users_found) == 2


class FindMostRecentBeneficiaryCreationDateByProcedureIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_created_at_date_of_most_recent_beneficiary_import_with_created_status_for_one_procedure(self, app):
        # given
        source_id = 1
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        three_days_ago = now - timedelta(days=3)

        users_factories.BeneficiaryGrant18Factory(dateCreated=yesterday, email="user1@example.com")
        user2 = users_factories.BeneficiaryGrant18Factory(dateCreated=two_days_ago, email="user2@example.com")
        user3 = users_factories.BeneficiaryGrant18Factory(dateCreated=three_days_ago, email="user3@example.com")
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user2,
            applicationId=1,
            sourceId=source_id,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
        )
        users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport=beneficiary_import, status=ImportStatus.ERROR, date=two_days_ago
        )

        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user3,
            applicationId=3,
            sourceId=source_id,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
        )
        users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport=beneficiary_import, status=ImportStatus.CREATED, date=three_days_ago
        )
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

        user = users_factories.BeneficiaryGrant18Factory(dateCreated=yesterday, email="user@example.com")
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            applicationId=3,
            sourceId=old_source_id,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
        )
        users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport=beneficiary_import, status=ImportStatus.CREATED, date=yesterday
        )

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
        users_factories.BeneficiaryGrant18Factory(dateCreated=yesterday)

        # when
        most_recent_creation_date = find_most_recent_beneficiary_creation_date_for_source(
            BeneficiaryImportSources.demarches_simplifiees, 1
        )

        # then
        assert most_recent_creation_date == datetime(MINYEAR, 1, 1)
