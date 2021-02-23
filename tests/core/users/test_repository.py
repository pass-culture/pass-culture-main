from datetime import date
from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import exceptions
from pcapi.core.users import factories
from pcapi.core.users import repository


class CheckUserAndCredentialsTest:
    def test_unknown_user(self):
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(None, "doe")

    def test_user_with_invalid_password(self):
        user = factories.UserFactory.build(isActive=True)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_inactive_user_with_invalid_password(self):
        user = factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_user_pending_validation_wrong_password(self):
        user = factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_user_pending_email_validation_wrong_password(self):
        user = factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_with_inactive_user(self):
        user = factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)

    def test_user_pending_validation(self):
        user = factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)

    def test_user_pending_email_validation(self):
        user = factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)

    def test_user_with_valid_password(self):
        user = factories.UserFactory.build(isActive=True)
        repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)


@pytest.mark.usefixtures("db_session")
class GetNewlyEligibleUsersTest:
    @freeze_time("2018-01-01 ")
    def test_eligible_user(self):
        user_already_18 = factories.UserFactory(
            isBeneficiary=False, dateOfBirth=datetime(1999, 12, 31), dateCreated=datetime(2017, 12, 1)
        )
        user_just_18 = factories.UserFactory(
            isBeneficiary=False, dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2017, 12, 1)
        )
        # Possible beneficiary that registered too late
        factories.UserFactory(isBeneficiary=False, dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        # Admin
        factories.UserFactory(
            isBeneficiary=False, dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1), isAdmin=True
        )
        # Pro
        pro_user = factories.UserFactory(
            isBeneficiary=False, dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1)
        )
        offers_factories.UserOffererFactory(user=pro_user)
        # User not yet 18
        factories.UserFactory(isBeneficiary=False, dateOfBirth=datetime(2000, 1, 2), dateCreated=datetime(2017, 12, 1))

        # Users 18 on the day `since` should not appear, nor those that are not 18 yet
        users = repository.get_newly_eligible_users(since=date(2017, 12, 31))
        assert set(users) == {user_just_18}
        users = repository.get_newly_eligible_users(since=date(2017, 12, 30))
        assert set(users) == {user_just_18, user_already_18}
