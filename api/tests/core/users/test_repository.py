from datetime import datetime

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import repository
from pcapi.core.users.models import UserRole
from pcapi.core.users.repository import get_users_with_validated_attachment_by_offerer
from pcapi.core.users.repository import has_access_to_venues


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
        user = users_factories.UserFactory.build(isActive=False, isEmailValidated=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_user_pending_validation_wrong_password(self):
        user = users_factories.UserFactory.build(isActive=True)
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
        user = users_factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, settings.TEST_DEFAULT_PASSWORD)

    def test_user_pending_email_validation(self):
        user = users_factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, settings.TEST_DEFAULT_PASSWORD)

    def test_user_with_valid_password(self):
        user = users_factories.UserFactory.build(isActive=True)
        repository.check_user_and_credentials(user, settings.TEST_DEFAULT_PASSWORD)


class CheckUserHasAccessToOfferersVenues:
    def test_user_has_access_to_multiple_venues(self):
        pro_user = users_factories.ProFactory()
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer1)
        venues_1 = offerers_factories.VenueFactory.create_batch(3, managingOffererId=offerer1.id)
        venues_2 = offerers_factories.VenueFactory.create_batch(2, managingOffererId=offerer2.id)
        assert has_access_to_venues(pro_user, venues_1)
        assert not has_access_to_venues(pro_user, venues_2)
        assert not has_access_to_venues(pro_user, venues_1 + venues_2)


class GetNewlyEligibleUsersTest:
    def test_fetch_users_that_had_birthday(self):
        today = datetime.today()
        already_18_birthday = today - relativedelta(years=18, days=1)
        created_one_month_ago = today - relativedelta(months=1)
        just_18_birthday = today - relativedelta(years=18)
        not_yet_18 = today - relativedelta(years=17, days=364)
        created_yesterday = today - relativedelta(days=1)
        one_day_ago = today - relativedelta(days=1)
        two_days_ago = today - relativedelta(days=2)

        user_already_18 = users_factories.BaseUserFactory(
            dateOfBirth=already_18_birthday, dateCreated=created_one_month_ago
        )
        user_just_18 = users_factories.BaseUserFactory(dateOfBirth=just_18_birthday, dateCreated=created_yesterday)
        user_just_18_ex_underage_beneficiary = users_factories.BaseUserFactory(
            dateOfBirth=just_18_birthday,
            dateCreated=created_one_month_ago,
            roles=[UserRole.UNDERAGE_BENEFICIARY],
        )
        # Possible beneficiary that registered too late
        users_factories.BaseUserFactory(dateOfBirth=just_18_birthday, dateCreated=today)
        # Admin
        users_factories.AdminFactory(dateOfBirth=just_18_birthday, dateCreated=today)
        # Pro
        pro_user = users_factories.ProFactory(dateOfBirth=just_18_birthday, dateCreated=today)
        offerers_factories.UserOffererFactory(user=pro_user)
        # User not yet 18
        users_factories.BaseUserFactory(dateOfBirth=not_yet_18, dateCreated=created_one_month_ago)

        # Users 18 on the day `since` should not appear, nor those that are not 18 yet
        users = repository.get_users_that_had_birthday_since(since=one_day_ago, age=18)
        assert set(users) == {user_just_18, user_just_18_ex_underage_beneficiary}
        users = repository.get_users_that_had_birthday_since(since=two_days_ago, age=18)
        assert set(users) == {user_just_18, user_just_18_ex_underage_beneficiary, user_already_18}

    def test_eligible_user_with_discordant_dates_on_declared_one(self):
        date_to_check = datetime.utcnow() - relativedelta(days=1)
        users_factories.BaseUserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            validatedBirthDate=datetime.utcnow() - relativedelta(years=17, months=11),
            dateCreated=datetime.utcnow() - relativedelta(months=1),
            roles=[UserRole.UNDERAGE_BENEFICIARY],
        )
        users = repository.get_users_that_had_birthday_since(since=date_to_check, age=18)
        assert set(users) == set()

    @time_machine.travel("2024-02-01")
    def test_eligible_user_with_discordant_dates_on_validated_one(self):
        date_to_check = datetime.utcnow() - relativedelta(days=1)
        user_just_18_discordant_dates = users_factories.BaseUserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=1),
            validatedBirthDate=datetime.utcnow() - relativedelta(years=18),
            dateCreated=datetime.utcnow() - relativedelta(months=2),
            roles=[UserRole.UNDERAGE_BENEFICIARY],
        )

        users = repository.get_users_that_had_birthday_since(since=date_to_check, age=18)
        assert set(users) == {user_just_18_discordant_dates}


class GetApplicantOfOffererUnderValidationTest:
    def test_return_user_with_validated_attachment(self):
        # Given
        applicant = users_factories.UserFactory()
        user_who_asked_for_attachment = users_factories.UserFactory()
        applied_offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(offerer=applied_offerer, user=applicant)
        offerers_factories.NotValidatedUserOffererFactory(offerer=applied_offerer, user=user_who_asked_for_attachment)

        # When
        applicants_found = get_users_with_validated_attachment_by_offerer(applied_offerer)

        # Then
        assert len(applicants_found) == 1
        assert applicants_found[0].id == applicant.id
