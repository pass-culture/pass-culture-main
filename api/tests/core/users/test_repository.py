from datetime import date
from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import repository
from pcapi.core.users.models import UserRole
from pcapi.core.users.repository import get_users_with_validated_attachment_by_offerer


pytestmark = pytest.mark.usefixtures("db_session")


class CheckUserAndCredentialsTest:
    def test_unknown_user(self):
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(None, "doe")

    def test_user_with_invalid_password(self):
        user = users_factories.UserFactory.build(isActive=True)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_inactive_user_with_invalid_password(self):
        user = users_factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_user_pending_validation_wrong_password(self):
        user = users_factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_user_pending_email_validation_wrong_password(self):
        user = users_factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_with_inactive_user(self):
        user = users_factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, settings.TEST_DEFAULT_PASSWORD)

    def test_user_pending_validation(self):
        user = users_factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, settings.TEST_DEFAULT_PASSWORD)

    def test_user_pending_email_validation(self):
        user = users_factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, settings.TEST_DEFAULT_PASSWORD)

    def test_user_with_valid_password(self):
        user = users_factories.UserFactory.build(isActive=True)
        repository.check_user_and_credentials(user, settings.TEST_DEFAULT_PASSWORD)


class GetNewlyEligibleUsersTest:
    @freeze_time("2018-01-01")
    def test_eligible_user(self):
        user_already_18 = users_factories.UserFactory(
            dateOfBirth=datetime(1999, 12, 31), dateCreated=datetime(2017, 12, 1)
        )
        user_just_18 = users_factories.UserFactory(
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 31),
        )
        user_just_18_ex_underage_beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 1),
            roles=[UserRole.UNDERAGE_BENEFICIARY],
        )
        # Possible beneficiary that registered too late
        users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        # Admin
        users_factories.AdminFactory(dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        # Pro
        pro_user = users_factories.ProFactory(dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        offerers_factories.UserOffererFactory(user=pro_user)
        # User not yet 18
        users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 2), dateCreated=datetime(2017, 12, 1))

        # Users 18 on the day `since` should not appear, nor those that are not 18 yet
        users = repository.get_newly_eligible_age_18_users(since=date(2017, 12, 31))
        assert set(users) == {user_just_18, user_just_18_ex_underage_beneficiary}
        users = repository.get_newly_eligible_age_18_users(since=date(2017, 12, 30))
        assert set(users) == {user_just_18, user_just_18_ex_underage_beneficiary, user_already_18}


class GetApplicantOfOffererUnderValidationTest:
    def test_return_user_with_validated_attachment(self):
        # Given
        applicant = users_factories.UserFactory()
        user_who_asked_for_attachment = users_factories.UserFactory()
        applied_offerer = offerers_factories.OffererFactory(validationToken="TOKEN")
        offerers_factories.UserOffererFactory(offerer=applied_offerer, user=applicant)
        offerers_factories.UserOffererFactory(
            offerer=applied_offerer, user=user_who_asked_for_attachment, validationToken="OTHER_TOKEN"
        )

        # When
        applicants_found = get_users_with_validated_attachment_by_offerer(applied_offerer)

        # Then
        assert len(applicants_found) == 1
        assert applicants_found[0].id == applicant.id
