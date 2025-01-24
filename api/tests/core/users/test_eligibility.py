import datetime

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import eligibility_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
class DecideEligibilityTest:
    def test_19yo_is_eligible_if_application_at_18_yo(self):
        today = datetime.date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=today - relativedelta(years=1),
        )

        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime.combine(today, datetime.datetime.min.time()), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result == users_models.EligibilityType.AGE18

    def test_19yo_not_eligible(self):
        today = datetime.date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()

        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime.combine(today, datetime.datetime.min.time()), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result is None

    def test_19yo_ex_underage_not_eligible(self):
        today = datetime.date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            dateCreated=today - relativedelta(years=3, days=1),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime.combine(today, datetime.datetime.min.time()), birth_date=birth_date
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, resultContent=dms_content
        )

        result = eligibility_api.decide_eligibility(
            user, dms_content.get_birth_date(), dms_content.get_registration_datetime()
        )
        assert result is None

    def test_18yo_eligible(self):
        today = datetime.date.today()
        birth_date = today - relativedelta(years=19, days=1)
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=today - relativedelta(years=1),
        )
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime.combine(
                today - relativedelta(years=1, days=-1), datetime.datetime.min.time()
            ),
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
        today = datetime.date.today()
        birth_date = today - relativedelta(years=18, days=1)
        user = users_factories.UserFactory()
        dms_content = fraud_factories.DMSContentFactory(
            registration_datetime=datetime.datetime.combine(
                today - relativedelta(years=1, days=-1), datetime.datetime.min.time()
            ),
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
            user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age))
            birth_date = user.dateOfBirth
            registration_datetime = datetime.datetime.today()

            assert (
                eligibility_api.decide_eligibility(user, birth_date, registration_datetime)
                == users_models.EligibilityType.UNDERAGE
            )

    @time_machine.travel("2022-03-01 13:45:00")  # 2022-03-02 00:45 in Noumea timezone
    def test_decide_underage_eligibility_with_timezone(self):
        today = datetime.date.today()
        march_2nd_fifteen_years_ago = today - relativedelta(years=15, days=-1)
        new_caledonian_user = users_factories.UserFactory(
            dateOfBirth=march_2nd_fifteen_years_ago, departementCode="988"
        )

        eligibility = eligibility_api.decide_eligibility(new_caledonian_user, march_2nd_fifteen_years_ago, today)

        assert eligibility == users_models.EligibilityType.UNDERAGE

    @time_machine.travel("2022-01-01")
    def test_decide_eligibility_for_18_yo_users_is_always_age_18(self):
        # 18 users are always eligible
        birth_date = datetime.datetime.utcnow() - relativedelta(years=18)
        user = users_factories.UserFactory()

        assert (
            eligibility_api.decide_eligibility(user, birth_date, datetime.datetime.today())
            == users_models.EligibilityType.AGE18
        )
        assert eligibility_api.decide_eligibility(user, birth_date, None) == users_models.EligibilityType.AGE18
        assert (
            eligibility_api.decide_eligibility(user, birth_date, datetime.datetime.utcnow() - relativedelta(years=1))
            == users_models.EligibilityType.AGE18
        )

    @time_machine.travel("2022-07-01")
    @pytest.mark.parametrize(
        "first_registration_datetime,expected_eligibility",
        [
            (None, None),
            (datetime.datetime(year=2022, month=1, day=15), None),
            (
                datetime.datetime(year=2021, month=12, day=1),
                users_models.EligibilityType.AGE18,
            ),
        ],
    )
    # 19yo users are eligible if they have started registration before turning 19
    def test_decide_eligibility_for_19_yo_users(self, first_registration_datetime, expected_eligibility):
        birth_date = datetime.datetime(year=2003, month=1, day=1)
        user = users_factories.UserFactory()

        if first_registration_datetime:
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.DMS,
                resultContent=fraud_factories.DMSContentFactory(
                    registration_datetime=first_registration_datetime, birth_date=birth_date
                ),
            )

        assert eligibility_api.decide_eligibility(user, birth_date, datetime.datetime.today()) == expected_eligibility

    def test_decide_eligibility_for_19_yo_users_with_no_registration_datetime(self):
        today = datetime.date.today()
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


class GetEligibilityTest:
    def test_get_eligibility_at_date_timezones_tolerance(self):
        date_of_birth = datetime.datetime(2000, 2, 1, 0, 0)

        specified_date = datetime.datetime(2019, 2, 1, 8, 0)
        assert (
            eligibility_api.get_eligibility_at_date(date_of_birth, specified_date) == users_models.EligibilityType.AGE18
        )

        specified_date = datetime.datetime(2019, 2, 1, 12, 0)
        assert eligibility_api.get_eligibility_at_date(date_of_birth, specified_date) is None
