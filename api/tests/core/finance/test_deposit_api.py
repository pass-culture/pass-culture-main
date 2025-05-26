import datetime
import json
import logging
from decimal import Decimal
from unittest import mock

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.mails.testing as mails_testing
from pcapi import settings as pcapi_settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.finance import conf
from pcapi.core.finance import deposit_api as api
from pcapi.core.finance import exceptions
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications.push import testing as push_testing

from tests.core.subscription.test_factories import IdentificationState
from tests.core.subscription.test_factories import UbbleIdentificationIncludedDocumentsFactory
from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.test_utils import json_default


pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


class UpsertDepositTest:
    @time_machine.travel("2021-02-05 09:00:00")
    @pytest.mark.parametrize("age,expected_amount", [(15, Decimal(20)), (16, Decimal(30)), (17, Decimal(30))])
    def test_create_underage_deposit(self, age, expected_amount):
        with time_machine.travel(
            datetime.datetime.combine(datetime.datetime.utcnow(), datetime.time(0, 0))
            - relativedelta(years=age, months=2)
        ):
            beneficiary = users_factories.UserFactory(validatedBirthDate=datetime.datetime.utcnow())
        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(month=1)):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=beneficiary,
                status=fraud_models.FraudCheckStatus.OK,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=fraud_factories.EduconnectContentFactory(
                    age=age, registration_datetime=datetime.datetime.utcnow()
                ),
            )

        deposit = api.upsert_deposit(beneficiary, "created by test", beneficiary.eligibility)

        assert deposit.type == models.DepositType.GRANT_15_17
        assert deposit.version == 1
        assert deposit.amount == expected_amount
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime.datetime(2021 - (age + 1) + 21, 12, 5, 11, 0, 0)

    @time_machine.travel("2025-03-03")
    def test_create_underage_deposit_with_two_birthdays_since_registration(self):
        seventeen_years_ago = datetime.datetime.utcnow() - relativedelta(years=17, months=1)
        beneficiary = users_factories.UserFactory(validatedBirthDate=seventeen_years_ago.date())

        when_user_is_15_years_and_11_months_old = datetime.datetime.utcnow() - relativedelta(years=1, months=2)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=beneficiary,
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(
                registration_datetime=when_user_is_15_years_and_11_months_old
            ),
        )

        # Registration is completed 1 year and 2 months later, when user is 17 years and 1 month old
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=beneficiary,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.datetime.utcnow()),
        )

        # Deposit is created right after the validation of the registration
        deposit = api.upsert_deposit(beneficiary, "created by test", users_models.EligibilityType.UNDERAGE)

        assert deposit.type == models.DepositType.GRANT_17_18
        assert deposit.version == 1
        assert deposit.user.id == beneficiary.id
        assert deposit.amount == 20 + 0 + 50

    @time_machine.travel("2025-03-03")
    def test_create_underage_deposit_with_birthday_since_registration(self):
        sixteen_years_ago = datetime.datetime.utcnow() - relativedelta(years=16)
        beneficiary = users_factories.UserFactory(
            dateOfBirth=sixteen_years_ago, validatedBirthDate=sixteen_years_ago.date()
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=beneficiary,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(
                registration_datetime=datetime.datetime.utcnow() - relativedelta(years=1)
            ),
        )

        deposit = api.upsert_deposit(beneficiary, "created by test", users_models.EligibilityType.UNDERAGE)

        assert deposit.type == models.DepositType.GRANT_15_17
        assert deposit.amount == 20

    def test_create_18_years_old_pre_decree_deposit(self):
        beneficiary = users_factories.UserFactory(age=18)

        deposit = api.upsert_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert deposit.type == models.DepositType.GRANT_18
        assert deposit.version == 2
        assert deposit.amount == Decimal(300)
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate.date() == (beneficiary.dateOfBirth + relativedelta(years=21)).date()

    @time_machine.travel("2025-03-03")
    def test_create_18_years_old_post_decree_deposit(self):
        user = users_factories.HonorStatementValidatedUserFactory(validatedBirthDate=datetime.date(2007, 1, 1))

        deposit = api.upsert_deposit(user, "created by test", users_models.EligibilityType.AGE17_18)

        assert deposit.type == models.DepositType.GRANT_17_18
        assert deposit.amount == 150
        assert deposit.expirationDate.date() == datetime.date(2028, 1, 1)
        assert deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_18
        assert deposit.recredits[0].amount == 150

    @time_machine.travel("2025-03-03")
    def test_create_17_years_old_post_decree_deposit(self):
        user = users_factories.HonorStatementValidatedUserFactory(validatedBirthDate=datetime.date(2008, 1, 1))

        deposit = api.upsert_deposit(user, "created by test", users_models.EligibilityType.AGE17_18)

        assert deposit.type == models.DepositType.GRANT_17_18
        assert deposit.amount == 50
        assert deposit.expirationDate.date() == datetime.date(2029, 1, 1)
        assert deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_17
        assert deposit.recredits[0].amount == 50

    def test_create_free_grant_deposit(self):
        current_year = datetime.date.today().year
        sixteen_years_ago = datetime.date(current_year - 16, 1, 1)
        user = users_factories.HonorStatementValidatedUserFactory(validatedBirthDate=sixteen_years_ago)

        deposit = api.upsert_deposit(user, "created by test", users_models.EligibilityType.FREE)

        assert deposit.type == models.DepositType.GRANT_FREE
        assert deposit.amount == 0
        assert deposit.expirationDate.date() == sixteen_years_ago + relativedelta(years=21)
        assert not deposit.recredits

    def test_cannot_upsert_grant_18_deposit(self):
        AGE18_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - relativedelta(years=18, months=2)
        beneficiary = users_factories.BeneficiaryGrant18Factory(validatedBirthDate=AGE18_ELIGIBLE_BIRTH_DATE)

        with pytest.raises(exceptions.UserCannotBeRecredited):
            api.upsert_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert db.session.query(models.Deposit).filter(models.Deposit.userId == beneficiary.id).count() == 1

    def test_upsert_deposit_age_18_expires_underage_deposit(self):
        before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = users_factories.BeneficiaryFactory(age=17, dateCreated=before_decree)

        deposit = api.upsert_deposit(user, "created by test", users_models.EligibilityType.AGE18)

        assert deposit.type == models.DepositType.GRANT_18
        assert len(user.deposits) == 2
        underage_deposit = min(*user.deposits, key=lambda d: d.id)
        assert underage_deposit.expirationDate < datetime.datetime.utcnow()

    def test_compute_deposit_expiration_date(self):
        user = users_models.User(validatedBirthDate=datetime.date(2007, 1, 1))
        assert user.age == 18

        expiration_date = api.compute_deposit_expiration_date(user)

        assert expiration_date.date() == datetime.date(2028, 1, 1)


class UserRecreditTest:
    def test_cannot_be_recredited_for_deposit_using_identity_provider_checks(self):
        user = users_factories.UnderageBeneficiaryFactory(subscription_age=17)

        sixteen_years_ago = datetime.datetime.utcnow() - relativedelta(years=16)
        users_api.update_user_info(
            user, author=users_factories.UserFactory(roles=["ADMIN"]), validated_birth_date=sixteen_years_ago.date()
        )

        next_year = datetime.datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(next_year):
            can_be_recredited_for_17 = api._can_be_recredited(user)
            assert not can_be_recredited_for_17

    def test_cannot_be_recredited_for_deposit_using_support_actions(self, ubble_mocker):
        yesterday = datetime.datetime.utcnow() - relativedelta(days=1)
        with time_machine.travel(yesterday):
            # for some reason, the Ubble fraud check is created after the action history below, so we create the user yesterday
            user = users_factories.HonorStatementValidatedUserFactory()
        seventeen_years_ago = datetime.datetime.utcnow() - relativedelta(years=17)
        users_api.update_user_info(
            user, author=users_factories.UserFactory(roles=["ADMIN"]), validated_birth_date=seventeen_years_ago.date()
        )
        users_factories.DepositGrantFactory(user=user)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=datetime.datetime.utcnow() + relativedelta(days=1),
        )

        sixteen_years_ago = datetime.datetime.utcnow() - relativedelta(years=16)
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=fraud_check.thirdPartyId,
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=sixteen_years_ago.date().isoformat()
                ),
            ],
        )
        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        next_year = datetime.datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(next_year):
            can_be_recredited_for_17 = api._can_be_recredited(user)
            assert not can_be_recredited_for_17

    def test_cannot_be_recredited_when_recredit_was_already_given(self):
        user = users_factories.BeneficiaryFactory(age=15)
        factories.RecreditFactory(deposit=user.deposit, recreditType=models.RecreditType.RECREDIT_16)
        factories.RecreditFactory(deposit=user.deposit, recreditType=models.RecreditType.RECREDIT_17)

        next_year = datetime.datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(next_year):
            can_be_recredited_for_16 = api._can_be_recredited(user)
            assert not can_be_recredited_for_16

    def test_can_be_recredited_no_registration_datetime(self):
        with time_machine.travel("2020-05-02"):
            user = users_factories.UnderageBeneficiaryFactory(
                subscription_age=15, dateOfBirth=datetime.date(2005, 5, 1)
            )
            # I voluntarily don't use the EduconnectContentFactory to be allowed to omit registration_datetime
            content = {
                "birth_date": "2020-05-02",
                "educonnect_id": "educonnect_id",
                "first_name": "first_name",
                "ine_hash": "ine_hash",
                "last_name": "last_name",
                "school_uai": "school_uai",
                "student_level": "student_level",
            }
            fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent={},
                dateCreated=datetime.datetime(2020, 5, 1),  # first fraud check created
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            fraud_check.resultContent = content
        with time_machine.travel("2022-05-02"):
            assert api._can_be_recredited(user) is True

    def test_can_be_recredited_no_identity_fraud_check(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.date(2005, 5, 1))
        with time_machine.travel("2020-05-02"):
            assert api._can_be_recredited(user) is False

    def test_can_be_recredited_legacy_educonnect_fraud_check(self):
        user = users_factories.BeneficiaryFactory(age=15)
        fraud_factories.BeneficiaryFraudCheckFactory(
            dateCreated=datetime.datetime(2020, 5, 2),
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            resultContent=None,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        assert api._has_pre_decree_deposit_been_recredited(user)

    @mock.patch("pcapi.core.finance.deposit_api._has_pre_decree_deposit_been_recredited")
    def should_not_check_recredits_on_age_18(self, mock_has_been_recredited):
        user = users_factories.BeneficiaryFactory(age=18)
        assert api._can_be_recredited(user) is False
        assert mock_has_been_recredited.call_count == 0

    @pytest.mark.parametrize("user_age", [16, 17])
    def test_has_not_been_recredited(self, user_age):
        user = users_factories.UnderageBeneficiaryFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=user_age)
        )

        assert not api._has_pre_decree_deposit_been_recredited(user)

    @pytest.mark.parametrize("user_age", [15, 16, 17])
    def test_has_been_recredited_with_current_recredit(self, user_age):
        user = users_factories.UnderageBeneficiaryFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=user_age)
        )
        factories.RecreditFactory(
            deposit=user.deposit,
            recreditType=conf.RECREDIT_TYPE_AGE_MAPPING[user_age],
            dateCreated=datetime.datetime(2020, 1, 1),
        )

        assert api._has_pre_decree_deposit_been_recredited(user)

    def test_has_not_been_recredited_for_current_age(self):
        user_age = 17
        user = users_factories.UnderageBeneficiaryFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=user_age)
        )
        factories.RecreditFactory(
            deposit=user.deposit,
            recreditType=models.RecreditType.RECREDIT_16,
            dateCreated=datetime.datetime(2020, 1, 1),
        )

        assert not api._has_pre_decree_deposit_been_recredited(user)

    def test_has_been_recredited_logs_error_if_no_age(self, caplog):
        user = users_factories.BaseUserFactory(dateOfBirth=None)
        assert user.age is None

        with caplog.at_level(logging.ERROR):
            assert api._has_pre_decree_deposit_been_recredited(user) is False
            assert caplog.records[0].extra["user_id"] == user.id

    def test_recredit_when_account_activated_on_the_birthday(self):
        with time_machine.travel("2020-05-01"):
            user = users_factories.UnderageBeneficiaryFactory(
                subscription_age=16, dateOfBirth=datetime.date(2004, 5, 1)
            )
            assert user.deposit.amount == 30
            assert user.recreditAmountToShow is None

            # Should not recredit if the account was created the same day as the birthday
            api.recredit_users()
            assert user.deposit.amount == 30
            assert user.recreditAmountToShow is None

    def test_notify_user_on_recredit(self):
        last_year = datetime.datetime.utcnow() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)

        api.recredit_users()

        push_data = push_testing.requests[-1]
        assert push_data["can_be_asynchronously_retried"] is True
        assert push_data["event_name"] == "recredited_account"
        assert push_data["user_id"] == user.id
        payload = push_data["event_payload"]
        assert payload["deposit_amount"] == 30 + 50
        assert payload["deposit_type"] == "GRANT_17_18"
        assert payload["deposits_count"] == 2
        assert payload["deposit_expiration_date"] == user.deposit.expirationDate.isoformat()

    def test_user_with_finished_age_18_process_is_credited_with_correct_role(self):
        """
        This test is inspired from real life data, and aims to reproduce a bug

        We generate a user that:
        - Tried to start at 18yo in the past (this gives them some correct fraud checks for the future 18yo real process)
        - Them get their underage deposit
        - Finish the 18yo steps, but are not yet activated (happens rarely)
        They are then processed in the recredit_users function, and should be correctly credited with a role BENEFICIARY
        """
        declared_birthdate = datetime.datetime(2004, 3, 18)  # tried to start at 18yo
        real_birthdate = datetime.date(2007, 3, 18)  # was not 18 at the time. Is 18 now
        today = datetime.datetime(2025, 3, 19)

        user = users_factories.EmailValidatedUserFactory(
            dateCreated=datetime.datetime(2022, 12, 5, 13, 41, 0),
            dateOfBirth=declared_birthdate,
        )

        # The user first tried a AGE18 activation, but cancelled it.
        fraud_factories.PhoneValidationFraudCheckFactory(
            user=user,
            dateCreated=datetime.datetime(2022, 12, 5, 13, 42, 00),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        user.phoneNumber = "0693949596"
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            dateCreated=datetime.datetime(2022, 12, 5, 13, 43, 00),
            status=fraud_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.AGE18,
            reason="Completed in application step ; Eligibility type changed by the identity provider",
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime.datetime(2023, 5, 13, 16, 39, 00),
            status=fraud_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.UBBLE,
            reason="Eligibility type changed by the identity provider",
            resultContent=fraud_factories.UbbleContentFactory(birth_date=real_birthdate),
        )
        # Ubble updates the birth date
        user.validatedBirthDate = real_birthdate

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime.datetime(2023, 5, 13, 16, 43, 00),
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            reason="statement from /subscription/honor_statement endpoint",
            resultContent=None,
        )

        # Then they try an UNDERAGE activation (because they are in fact not 18yo)
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            dateCreated=datetime.datetime(2023, 5, 13, 16, 59, 00),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            reason="Completed in application step",
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime.datetime(2023, 5, 13, 16, 59, 00),
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.UBBLE,
            reason="",
            resultContent=fraud_factories.UbbleContentFactory(birth_date=real_birthdate),
        )
        fraud_factories.HonorStatementFraudCheckFactory(
            user=user,
            dateCreated=datetime.datetime(2023, 5, 14, 00, 9, 00),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            reason="statement from /subscription/honor_statement endpoint",
            resultContent=None,
        )
        # And had their deposit UNDERAGE granted
        deposit = users_factories.DepositGrantFactory(
            user=user,
            type=models.DepositType.GRANT_15_17,
            dateCreated=datetime.datetime(2023, 5, 14, 00, 9, 00),
            amount=60,
        )
        user.roles = [users_models.UserRole.UNDERAGE_BENEFICIARY]
        # one year after they get recredited
        factories.RecreditFactory(
            deposit=deposit,
            dateCreated=datetime.datetime(2024, 3, 18, 8, 19, 00),
            amount=30,
            recreditType=models.RecreditType.RECREDIT_17,
            comment="Recredit 17",
        )

        # Another year after they start their 18yo application
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=datetime.datetime(2025, 3, 18, 11, 10, 00),
        )

        with time_machine.travel(today):
            api.recredit_users()
        assert user.deposit.type == models.DepositType.GRANT_17_18
        assert user.roles == [users_models.UserRole.BENEFICIARY]

    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def test_user_already_recredited(self, age):
        before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        users_factories.BeneficiaryFactory(age=age, dateCreated=before_decree)

        before_recredit_number = db.session.query(models.Recredit.id).count()
        api.recredit_users()
        after_recredit_number = db.session.query(models.Recredit.id).count()

        assert before_recredit_number == after_recredit_number

    def test_user_recredited_at_18(self):
        user = users_factories.BeneficiaryFactory(age=17, phoneNumber="0123456789")
        with time_machine.travel(datetime.datetime.utcnow() + relativedelta(years=1)):
            assert user.age == 18
            fraud_factories.PhoneValidationFraudCheckFactory(user=user)
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
            )
            fraud_factories.HonorStatementFraudCheckFactory(user=user)
            fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

            api.recredit_users()

            assert len(user.deposits) == 1
            assert len(user.deposit.recredits) == 2

    def test_user_not_recredited_at_18_if_missing_step(self):
        user = users_factories.BeneficiaryFactory(age=17, phoneNumber="0123456789")
        with time_machine.travel(datetime.datetime.utcnow() + relativedelta(years=1)):
            assert user.age == 18
            # user has not finished their subscription for the 18 year old recredit

            api.recredit_users()
            assert len(user.deposit.recredits) == 1

    def test_users_recredited_once(self):
        user = users_factories.BeneficiaryFactory(age=17, phoneNumber="0123456789")
        with time_machine.travel(datetime.datetime.utcnow() + relativedelta(years=1)):
            assert user.age == 18
            fraud_factories.PhoneValidationFraudCheckFactory(user=user)
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
            )
            fraud_factories.HonorStatementFraudCheckFactory(user=user)
            fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

            api.recredit_users()

            assert len(user.deposits) == 1
            assert len(user.deposit.recredits) == 2

            api.recredit_users()
            assert len(user.deposits) == 1
            assert len(user.deposit.recredits) == 2

    def test_user_with_missing_steps_is_not_recredited(self):
        user = users_factories.BeneficiaryFactory(age=17, deposit__type=models.DepositType.GRANT_17_18)

        next_year = datetime.datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(next_year):
            # User cannot be recredited because of missing steps
            api.recredit_users()
            assert len(user.deposits) == 1
            assert len(user.deposit.recredits) == 1

            # Finish missing steps
            fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
            fraud_factories.PhoneValidationFraudCheckFactory(user=user)
            user.phoneNumber = "+33600000000"
            fraud_factories.HonorStatementFraudCheckFactory(user=user)

            # User can be recredited
            api.recredit_users()

        assert len(user.deposits) == 1
        assert len(user.deposit.recredits) == 2

    def test_create_new_deposit_when_recrediting_underage_deposit(self):
        one_year_before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(years=1)
        next_week = datetime.datetime.utcnow() + relativedelta(weeks=1)
        with time_machine.travel(one_year_before_decree):
            user_1 = users_factories.BeneficiaryFactory(
                age=16, phoneNumber="+33600000000", deposit__amount=12, deposit__expirationDate=next_week
            )
            user_2 = users_factories.BeneficiaryFactory(age=17, deposit__expirationDate=next_week)

        # finish steps for user 2
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user_2)
        fraud_factories.PhoneValidationFraudCheckFactory(user=user_2)
        user_2.phoneNumber = "+33610000000"
        fraud_factories.HonorStatementFraudCheckFactory(user=user_2)

        api.recredit_users()

        # User 1 is 17, and was recredited with RECREDIT_17 on its new deposit
        assert len(user_1.deposits) == 2
        assert user_1.deposit.type == models.DepositType.GRANT_17_18
        assert user_1.deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_17
        assert (
            user_1.deposit.amount == 12 + 50
        )  #  12 (remaining credit 16 before decree) + 50 (for 17 year old after decree)

        # User 2 is 18, and was recredited with RECREDIT_18 on its new deposit
        assert len(user_2.deposits) == 2
        assert user_2.deposit.type == models.DepositType.GRANT_17_18
        assert user_2.deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_18
        assert user_2.deposit.amount == 30 + 150  #  30 (credit 17 before decree) + 150 (for 18 year old after decree)

    def test_booking_transfer_when_recrediting_underage_deposit(self):
        one_year_before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(years=1)
        next_week = datetime.datetime.utcnow() + relativedelta(weeks=1)
        with time_machine.travel(one_year_before_decree):
            user = users_factories.BeneficiaryFactory(
                age=16, phoneNumber="+33600000000", deposit__amount=30, deposit__expirationDate=next_week
            )
            # Bookings that can still be cancelled
            bookings_factories.BookingFactory(deposit=user.deposit, amount=1)
            bookings_factories.UsedBookingFactory(deposit=user.deposit, amount=2)
            # Bookings in a 'terminal' state, cannot be cancelled outside of a finance incident
            bookings_factories.CancelledBookingFactory(deposit=user.deposit, amount=12)
            bookings_factories.ReimbursedBookingFactory(deposit=user.deposit, amount=13)

        api.recredit_users()

        # User is 17, and was recredited with RECREDIT_17 on its new deposit
        assert len(user.deposits) == 2
        assert user.deposit.type == models.DepositType.GRANT_17_18
        assert user.deposit.recredits[0].recreditType == models.RecreditType.RECREDIT_17

        assert len(user.deposit.bookings) == 2
        newly_credited_amount = 50
        remaining_credit_amount = 30 - 13 - 2 - 1  # sum of the amounts of all the non-cancelled bookings
        amount_transferred_alongside_the_bookings = 1 + 2
        assert (
            user.deposit.amount
            == newly_credited_amount + remaining_credit_amount + amount_transferred_alongside_the_bookings
        )

    def test_recredit_only_if_identity_fraud_check_is_ok(self):
        last_year = datetime.datetime.utcnow() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = users_factories.BeneficiaryFactory(
                age=17,
                beneficiaryFraudChecks__type=fraud_models.FraudCheckType.EDUCONNECT,
            )
        user.phoneNumber = "+33610000000"
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )
        fraud_factories.HonorStatementFraudCheckFactory(user=user)

        api.recredit_users()

        assert models.RecreditType.RECREDIT_18 not in [recredit.recreditType for recredit in user.deposit.recredits]

    @pytest.mark.skip(
        reason="This test is very long and must be executed in a flask shell, outside of db_session fixture"
    )
    def test_recredit_users_does_not_crash_on_big_pages(self):
        one_year_before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(years=1)
        next_week = datetime.datetime.utcnow() + relativedelta(weeks=1)
        with time_machine.travel(one_year_before_decree):
            users_factories.BeneficiaryFactory.create_batch(
                1000, age=16, phoneNumber="+33600000000", deposit__amount=12, deposit__expirationDate=next_week
            )

        assert api.recredit_users() is None

    def test_recredit_email_is_sent_to_18_years_old_users(self):
        last_year = datetime.datetime.utcnow() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = users_factories.BeneficiaryFactory(age=17, deposit__type=models.DepositType.GRANT_17_18)

        # Finish missing steps
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.PhoneValidationFraudCheckFactory(user=user)
        user.phoneNumber = "+33600000000"
        fraud_factories.HonorStatementFraudCheckFactory(user=user)

        # User can be recredited
        api.recredit_users()
        assert len(user.deposits) == 1
        assert len(user.deposit.recredits) == 2

        outbox = mails_testing.outbox
        assert len(outbox) == 1
        assert outbox[0]["To"] == user.email
        assert outbox[0]["template"]["id_prod"] == 1509


class CanBeRecreditedTest:
    @pytest.mark.parametrize("age", (14, 15, 16, 19))
    def test_users_not_eligible_cannot_be_recredited(self, age):
        user = users_factories.BaseUserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age, months=1)
        )
        assert not api._can_be_recredited(user)

    def test_user_18_yo_can_be_recredited_with_post_decree_deposit(self):
        user = users_factories.BeneficiaryFactory(age=17)

        year_when_user_is_18 = datetime.datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(year_when_user_is_18):
            assert api._can_be_recredited(user)

    def test_users_with_no_deposit_cannot_be_recredited(self):
        user = users_factories.BaseUserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=1)
        )
        assert not api._can_be_recredited(user)

    @pytest.mark.parametrize("age", [17, 18])
    def test_beneficiary_can_be_recredited_with_pre_decree_deposit(self, age):
        before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        with time_machine.travel(before_decree):
            user = users_factories.BeneficiaryFactory(age=age - 1)

        next_year = datetime.datetime.utcnow() + relativedelta(years=1)
        with time_machine.travel(next_year):
            assert api._can_be_recredited(user)

    def test_user_18_yo_can_not_be_recredited_twice(self):
        user = users_factories.BaseUserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=1)
        )
        deposit = users_factories.DepositGrantFactory(user=user)
        factories.RecreditFactory(deposit=deposit, amount=150, recreditType=models.RecreditType.RECREDIT_18)

        assert not api._can_be_recredited(user)

    def test_user_17_yo_cannot_be_recredited_twice(self):
        before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        with time_machine.travel(before_decree):
            user = users_factories.BaseUserFactory(
                dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=16, months=1)
            )
            deposit = users_factories.DepositGrantFactory(user=user)
            # user already received the 17 year old pre-decree recredit
            factories.RecreditFactory(deposit=deposit, recreditType=models.RecreditType.RECREDIT_17)

        after_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1)
        with time_machine.travel(after_decree):
            assert user.age == 17
            # user can not receive the 17 year old post-decree recredit
            assert not api._can_be_recredited(user)

    def test_user_16_yo_cannot_be_recredited(self):
        after_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME + relativedelta(days=1)
        with time_machine.travel(after_decree):
            user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)

        assert not api._can_be_recredited(user)


class LastAgeRelatedRecreditTest:
    def test_last_recredit_17(self):
        user = users_factories.BeneficiaryFactory(age=17)

        last_recredit = api.get_latest_age_related_user_recredit(user)

        assert last_recredit.recreditType == models.RecreditType.RECREDIT_17

    def test_last_recredit_18(self):
        user = users_factories.BeneficiaryFactory(age=17)
        factories.RecreditFactory(
            deposit=user.deposit,
            amount=Decimal("150"),
            recreditType=models.RecreditType.RECREDIT_18,
            dateCreated=datetime.datetime.utcnow() - relativedelta(weeks=1),
        )

        last_recredit = api.get_latest_age_related_user_recredit(user)

        assert last_recredit.recreditType == models.RecreditType.RECREDIT_18

    def test_last_recredit_15_17_deposit(self):
        before_decree = pcapi_settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = users_factories.BeneficiaryFactory(age=17, dateCreated=before_decree)
        factories.RecreditFactory(
            deposit=user.deposit,
            amount=Decimal("30"),
            recreditType=models.RecreditType.RECREDIT_17,
            dateCreated=datetime.datetime.utcnow() - relativedelta(weeks=1),
        )
        factories.RecreditFactory(
            deposit=user.deposit,
            amount=Decimal("30"),
            recreditType=models.RecreditType.RECREDIT_16,
            dateCreated=datetime.datetime.utcnow() - relativedelta(weeks=1),
        )

        last_recredit = api.get_latest_age_related_user_recredit(user)

        assert last_recredit.recreditType == models.RecreditType.RECREDIT_17
