from datetime import date
from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi import settings
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import eligibility_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
@pytest.mark.features(WIP_ENABLE_CREDIT_V3=True)
class DecideV3CreditEligibilityTest:
    @pytest.mark.parametrize("age", [17, 18])
    def test_eligible_age(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)

        eligibility = eligibility_api.decide_eligibility(user, birth_date, None)

        assert eligibility == users_models.EligibilityType.AGE17_18

    @time_machine.travel("2022-03-01 13:45:00")  # 2022-03-02 00:45 in Noumea timezone
    def test_decide_underage_eligibility_with_timezone(self):
        today = date.today()
        march_2nd_seventeen_years_ago = today - relativedelta(years=17, days=-1)
        new_caledonian_user = users_factories.UserFactory(
            dateOfBirth=march_2nd_seventeen_years_ago, departementCode="988"
        )

        eligibility = eligibility_api.decide_eligibility(new_caledonian_user, march_2nd_seventeen_years_ago, None)

        assert eligibility == users_models.EligibilityType.AGE17_18

    @pytest.mark.parametrize("age", [14, 15, 16, 19, 20, 21])
    def test_not_eligible_age(self, age):
        birth_date = date.today() - relativedelta(years=age, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)

        eligibility = eligibility_api.decide_eligibility(user, birth_date, None)

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
    @pytest.mark.parametrize("age", [15, 16, 17])
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
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1),
        )

        yesterday = datetime.utcnow() - relativedelta(days=1)
        eligibility = eligibility_api.decide_eligibility(user, birth_date, yesterday)

        assert eligibility == users_models.EligibilityType.UNDERAGE

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
    def test_user_eighteen_eligibility_when_registered_before_decree(self):
        birth_date = date.today() - relativedelta(years=18, months=1)
        user = users_factories.UserFactory(dateOfBirth=birth_date)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1),
        )

        eligibility = eligibility_api.decide_eligibility(user, birth_date, None)

        assert eligibility == users_models.EligibilityType.AGE18

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


@pytest.mark.usefixtures("db_session")
@pytest.mark.features(WIP_ENABLE_CREDIT_V3=False)
class DecideEligibilityTest:
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
        today = date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()

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
        assert result == users_models.EligibilityType.AGE18

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

    @time_machine.travel("2022-03-01 13:45:00")  # 2022-03-02 00:45 in Noumea timezone
    def test_decide_underage_eligibility_with_timezone(self):
        today = date.today()
        march_2nd_fifteen_years_ago = today - relativedelta(years=15, days=-1)
        new_caledonian_user = users_factories.UserFactory(
            dateOfBirth=march_2nd_fifteen_years_ago, departementCode="988"
        )

        eligibility = eligibility_api.decide_eligibility(new_caledonian_user, march_2nd_fifteen_years_ago, today)

        assert eligibility == users_models.EligibilityType.UNDERAGE

    @time_machine.travel("2022-01-01")
    def test_decide_eligibility_for_18_yo_users_is_always_age_18(self):
        # 18 users are always eligible
        birth_date = datetime.utcnow() - relativedelta(years=18)
        user = users_factories.UserFactory()

        assert (
            eligibility_api.decide_eligibility(user, birth_date, datetime.today()) == users_models.EligibilityType.AGE18
        )
        assert eligibility_api.decide_eligibility(user, birth_date, None) == users_models.EligibilityType.AGE18
        assert (
            eligibility_api.decide_eligibility(user, birth_date, datetime.utcnow() - relativedelta(years=1))
            == users_models.EligibilityType.AGE18
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
            dateCreated=today - relativedelta(days=3),
        )

        assert eligibility_api.decide_eligibility(user, birth_date, None) == users_models.EligibilityType.AGE18


class GetExtendedEligibilityTest:
    def test_get_eligibility_at_date_timezones_tolerance(self):
        date_of_birth = datetime(2000, 2, 1, 0, 0)

        specified_date = date_of_birth + relativedelta(years=19, hours=8)
        eligibility = eligibility_api.get_extended_eligibility_at_date(date_of_birth, specified_date)

        assert eligibility == users_models.EligibilityType.AGE18

        specified_date = date_of_birth + relativedelta(years=19, hours=12)
        eligibility = eligibility_api.get_extended_eligibility_at_date(date_of_birth, specified_date)

        assert eligibility is None
