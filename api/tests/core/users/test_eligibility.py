from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi import settings
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.users import api as users_api
from pcapi.core.users import eligibility_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
class DecideEligibilityTest:
    @pytest.mark.parametrize("age", [17, 18])
    def test_eligible_age(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)

        eligibility = eligibility_api.decide_eligibility(user, birth_date, datetime.utcnow())

        assert eligibility == users_models.EligibilityType.AGE17_18

    @time_machine.travel("2025-03-01 13:45:00")  # 2025-03-02 00:45 in Noumea timezone
    def test_decide_underage_eligibility_with_timezone(self):
        today = date.today()
        march_2nd_seventeen_years_ago = today - relativedelta(years=17, days=-1)
        new_caledonian_user = users_factories.UserFactory(
            dateOfBirth=march_2nd_seventeen_years_ago, departementCode="988"
        )

        eligibility = eligibility_api.decide_eligibility(new_caledonian_user, march_2nd_seventeen_years_ago, None)

        assert eligibility == users_models.EligibilityType.AGE17_18

    @pytest.mark.parametrize("age", [14, 19, 20, 21])
    def test_not_eligible_age(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)

        eligibility = eligibility_api.decide_eligibility(user, birth_date, datetime.utcnow())

        assert eligibility is None

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=2))
    @pytest.mark.parametrize("age", [19, 20])
    def test_old_user_still_eligible_with_early_first_registration(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        date_when_user_was_eighteen = birth_date + relativedelta(years=18, months=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=date_when_user_was_eighteen,
        )

        eligibility = eligibility_api.decide_eligibility(user, birth_date, None)

        assert eligibility == users_models.EligibilityType.AGE17_18

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=2))
    @pytest.mark.parametrize("age", [19, 20])
    def test_old_user_still_eligible_with_early_registration_datetime(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        date_when_user_was_eighteen = birth_date + relativedelta(years=18, months=1)

        datetime_when_user_was_eighteen = datetime.combine(date_when_user_was_eighteen, datetime.min.time())
        eligibility = eligibility_api.decide_eligibility(user, birth_date, datetime_when_user_was_eighteen)

        assert eligibility == users_models.EligibilityType.AGE17_18

    @pytest.mark.parametrize("age", [19, 20])
    def test_old_user_not_eligible_with_first_registration_before_fourteen(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        date_when_user_was_fourteen = birth_date + relativedelta(years=14, months=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=date_when_user_was_fourteen,
        )

        eligibility = eligibility_api.decide_eligibility(user, birth_date, None)

        assert eligibility is None

    @pytest.mark.parametrize("age", [19, 20])
    def test_old_user_not_eligible_with_registration_datetime_before_fourteen(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        date_when_user_was_fourteen = birth_date + relativedelta(years=14, months=1)

        datetime_when_user_was_fourteen = datetime.combine(date_when_user_was_fourteen, datetime.min.time())
        eligibility = eligibility_api.decide_eligibility(user, birth_date, datetime_when_user_was_fourteen)

        assert eligibility is None

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
    @pytest.mark.parametrize("age", [15, 16])
    def test_user_underage_eligibility_when_registered_before_decree(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1),
        )

        eligibility = eligibility_api.decide_eligibility(user, birth_date, None)

        assert eligibility == users_models.EligibilityType.UNDERAGE

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
    @pytest.mark.parametrize("age", [15, 16, 17])
    def test_user_underage_eligibility_with_registration_datetime_before_decree(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        day_before_decree = datetime.utcnow() - relativedelta(days=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=day_before_decree,
        )

        eligibility = eligibility_api.decide_eligibility(user, birth_date, day_before_decree)

        assert eligibility == users_models.EligibilityType.UNDERAGE

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
    def test_user_eighteen_eligibility_with_registration_datetime_before_decree(self):
        birth_date = date.today() - relativedelta(years=18, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)

        yesterday = datetime.utcnow() - relativedelta(days=1)
        eligibility = eligibility_api.decide_eligibility(user, birth_date, yesterday)

        assert eligibility == users_models.EligibilityType.AGE18

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
    def test_user_21_ineligibility_when_registered_before_decree(self):
        birth_date = date.today() - relativedelta(years=21, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        year_when_user_was_eighteen = datetime.utcnow() - relativedelta(years=user.age - 18)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=year_when_user_was_eighteen,
        )

        eligibility = eligibility_api.decide_eligibility(user, birth_date, year_when_user_was_eighteen)

        assert eligibility is None

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
    def test_user_21_ineligibility_with_registration_date_before_decree(self):
        birth_date = date.today() - relativedelta(years=21, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)

        year_when_user_was_eighteen = datetime.utcnow() - relativedelta(years=user.age - 18)
        eligibility = eligibility_api.decide_eligibility(user, birth_date, year_when_user_was_eighteen)

        assert eligibility is None

    def test_19yo_is_eligible_if_application_at_18_yo(self):
        today = date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=today - relativedelta(years=1),
        )

        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.combine(today, datetime.min.time()), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result == users_models.EligibilityType.AGE18

    def test_19yo_not_eligible(self):
        birth_date = date.today() - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        dms_content = fraud_factories.DMSContentFactory(birth_date=birth_date)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result is None

    def test_19yo_ex_underage_not_eligible(self):
        today = date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            dateCreated=today - relativedelta(years=3, days=1),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.combine(today, datetime.min.time()), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result is None

    def test_18yo_eligible(self):
        today = date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=today - relativedelta(years=1),
        )
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.combine(today - relativedelta(years=1, days=-1), datetime.min.time()),
            birth_date=birth_date,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result == users_models.EligibilityType.AGE18

    @pytest.mark.settings(CREDIT_V3_DECREE_DATETIME=datetime.utcnow() - relativedelta(years=1))
    def test_18yo_underage_eligible(self):
        today = date.today()
        birth_date = today - relativedelta(years=18, days=1)
        user = users_factories.UserFactory()
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.combine(today - relativedelta(years=1, days=-1), datetime.min.time()),
            birth_date=birth_date,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result == users_models.EligibilityType.AGE17_18

    @time_machine.travel("2022-03-01")
    def test_decide_eligibility_for_underage_users(self):
        # All 15-17 users are eligible after 2022-01-01
        for age in range(15, 18):
            user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=age))
            birth_date = user.dateOfBirth
            registration_datetime = datetime.today()

            assert (
                eligibility_api.decide_eligibility(user, birth_date, registration_datetime)
                == users_models.EligibilityType.UNDERAGE
            )

    @time_machine.travel("2022-07-01")
    @pytest.mark.parametrize(
        "first_registration_datetime,expected_eligibility",
        [
            (None, None),
            (datetime(year=2022, month=1, day=15), None),
            (
                datetime(year=2021, month=12, day=1),
                users_models.EligibilityType.AGE18,
            ),
        ],
    )
    # 19yo users are eligible if they have started registration before turning 19
    def test_decide_eligibility_for_19_yo_users(self, first_registration_datetime, expected_eligibility):
        birth_date = datetime(year=2003, month=1, day=1)
        user = users_factories.UserFactory()

        if first_registration_datetime:
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.DMS,
                resultContent=fraud_factories.DMSContentFactory(
                    registration_datetime=first_registration_datetime, birth_date=birth_date
                ),
            )

        assert eligibility_api.decide_eligibility(user, birth_date, datetime.today()) == expected_eligibility

    def test_decide_eligibility_for_19_yo_users_with_no_registration_datetime(self):
        today = date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=fraud_factories.DMSContentFactory(
                registration_datetime=None,
                birth_date=birth_date,
            ),
            dateCreated=datetime.utcnow() - relativedelta(days=3),
        )

        assert eligibility_api.decide_eligibility(user, birth_date, None) == users_models.EligibilityType.AGE17_18


@pytest.mark.usefixtures("db_session")
class EligibilityForNextRecreditActivationStepsTest:
    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
    @pytest.mark.parametrize("age", [15, 16])
    def test_user_underage_activation_when_registered_before_decree(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1),
        )

        can_do_next_activation_steps = eligibility_api.is_eligible_for_next_recredit_activation_steps(user)

        assert can_do_next_activation_steps


class EligibilityDatesTest:
    @pytest.mark.features(WIP_FREE_ELIGIBILITY=False)
    def test_eligibility_start_after_decree(self):
        birth_date = datetime(2008, 1, 1)

        eligibility_start = eligibility_api.get_eligibility_start_datetime(birth_date, datetime.utcnow())

        assert eligibility_start == datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Paris"))

    def test_eligibility_start(self):
        birth_date = datetime(2008, 1, 1)

        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        eligibility_start = eligibility_api.get_eligibility_start_datetime(birth_date, before_decree)

        assert eligibility_start == datetime(2023, 1, 1, tzinfo=ZoneInfo("Europe/Paris"))

    def test_eligibility_end(self):
        birth_date = datetime(2008, 1, 1)

        eligibility_end = eligibility_api.get_eligibility_end_datetime(birth_date, datetime.utcnow())

        assert eligibility_end == datetime(2027, 1, 1, tzinfo=ZoneInfo("Europe/Paris"))

    def test_get_eligibility_at_date_timezones_tolerance(self):
        date_of_birth = datetime(2000, 2, 1, 0, 0)

        specified_date = date_of_birth + relativedelta(years=19, hours=8)
        eligibility = eligibility_api.get_eligibility_at_date(date_of_birth, specified_date, "987")  # utc-10

        assert eligibility == users_models.EligibilityType.AGE18

        specified_date = date_of_birth + relativedelta(years=19, hours=12)
        eligibility = eligibility_api.get_eligibility_at_date(date_of_birth, specified_date, "75")  # utc+1

        assert eligibility is None


@pytest.mark.usefixtures("db_session")
class GetFirstRegistrationDateTest:
    def test_get_first_registration_date_no_check(self):
        user = users_factories.UserFactory()
        assert (
            eligibility_api.get_first_eligible_registration_date(
                user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE
            )
            is None
        )

    def test_get_first_registration_date_underage(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2002, 1, 15))
        d1 = datetime(2018, 1, 1)
        d2 = datetime(2018, 2, 1)
        d3 = datetime(2018, 3, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            dateCreated=d2,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=d2,
            resultContent=None,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=d3,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d1),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        assert (
            eligibility_api.get_first_eligible_registration_date(
                user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE
            )
            == d1
        )

    def test_get_first_registration_date_underage_with_timezone(self):
        user = users_factories.UserFactory(age=17)
        today_in_utc = date.today() - relativedelta(minutes=15)  # 23:45 in UTC, so 00:45 today in Europe/Paris
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=today_in_utc,
            resultContent=None,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        first_registration_date = eligibility_api.get_first_eligible_registration_date(
            user, user.birth_date, users_models.EligibilityType.AGE17_18
        )

        assert first_registration_date == today_in_utc

    @pytest.mark.parametrize("age", [19, 20])
    def test_get_first_registration_barely_too_late_with_timezone(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        # 23:45 in UTC, so 00:45 today in Europe/Paris, meaning the user is now 19
        after_19th_birthday = birth_date + relativedelta(years=19) - relativedelta(minutes=15)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=after_19th_birthday,
            resultContent=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        first_registration_date = eligibility_api.get_first_eligible_registration_date(
            user, user.birth_date, users_models.EligibilityType.AGE18
        )

        assert first_registration_date is None

    def test_get_first_registration_date_age_18(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2002, 1, 15))
        d1 = datetime(2018, 1, 1)
        d2 = datetime(2020, 2, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=d1,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d1),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=d2,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d2),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        assert (
            eligibility_api.get_first_eligible_registration_date(
                user, user.dateOfBirth, users_models.EligibilityType.AGE18
            )
            == d2
        )

    def test_with_uneligible_age_try(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2005, 1, 15))
        d1 = datetime(2020, 1, 1)
        d2 = datetime(2020, 2, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=d1,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            dateCreated=d2,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d2),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert (
            eligibility_api.get_first_eligible_registration_date(
                user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE
            )
            == d2
        )

    def test_with_registration_before_opening_try(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2005, 1, 15))
        d1 = datetime(2020, 1, 1)
        d2 = datetime(2020, 2, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.INTERNAL_REVIEW,  # this happened with jouve results saying when the age is <18
            dateCreated=d1,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=None,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            dateCreated=d2,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d2),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert (
            eligibility_api.get_first_eligible_registration_date(
                user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE
            )
            == d2
        )

    def test_without_eligible_try(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2005, 1, 15))
        d1 = datetime(2020, 1, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=d1,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert (
            eligibility_api.get_first_eligible_registration_date(
                user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE
            )
            is None
        )


@pytest.mark.usefixtures("db_session")
class GetKnownBirthdateAtDateTest:
    def test_last_age_change_before_date_by_identity_provider(self):
        identity_check_known_birthday = date.today() - relativedelta(years=27)
        last_week = datetime.utcnow() - relativedelta(weeks=1)
        user = users_factories.IdentityValidatedUserFactory(
            validatedBirthDate=identity_check_known_birthday, beneficiaryFraudChecks__dateCreated=last_week
        )
        # support action that should be ignored
        users_api.update_user_info(
            user, author=users_factories.UserFactory(roles=["ADMIN"]), validated_birth_date=date(9999, 1, 1)
        )

        yesterday = datetime.utcnow() - relativedelta(days=1)
        yesterday_known_birthday = eligibility_api.get_known_birthday_at_date(user, yesterday)

        assert yesterday_known_birthday == identity_check_known_birthday

    def test_last_age_change_before_date_by_support_actions(self):
        identity_check_known_birth_date = date.today() - relativedelta(years=27)
        last_week = datetime.utcnow() - relativedelta(weeks=1)
        user = users_factories.IdentityValidatedUserFactory(
            validatedBirthDate=identity_check_known_birth_date, beneficiaryFraudChecks__dateCreated=last_week
        )

        support_known_birthday = date.today() - relativedelta(years=18)
        users_api.update_user_info(
            user, author=users_factories.UserFactory(roles=["ADMIN"]), validated_birth_date=support_known_birthday
        )

        # identity provider check that should be ignored
        tomorrow = datetime.utcnow() + relativedelta(days=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            user=user,
            dateCreated=tomorrow,
        )

        currently_known_birthday = eligibility_api.get_known_birthday_at_date(user, datetime.utcnow())

        assert currently_known_birthday == support_known_birthday

    @pytest.mark.parametrize("falsy_value", [None, {}])
    def test_does_not_crash_on_empty_action(self, falsy_value):
        user = users_factories.UserFactory()
        history_factories.ActionHistoryFactory(
            user=user, actionType=history_models.ActionType.INFO_MODIFIED, extraData=falsy_value
        )

        birthday = eligibility_api.get_known_birthday_at_date(user, datetime.utcnow())

        assert birthday == user.dateOfBirth.date()
