import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.payments import factories as payments_factories
from pcapi.core.payments import models as payments_models
from pcapi.core.users import factories as user_factories
from pcapi.scripts.payment.user_recredit import can_be_recredited
from pcapi.scripts.payment.user_recredit import has_been_recredited
from pcapi.scripts.payment.user_recredit import has_celebrated_birthday_since_registration
from pcapi.scripts.payment.user_recredit import recredit_underage_users


@pytest.mark.usefixtures("db_session")
class UserRecreditTest:
    @freeze_time("2021-07-01")
    @pytest.mark.parametrize(
        "birth_date,registration_datetime,expected_result",
        [
            ("2006-01-01", datetime.datetime(2021, 5, 1), False),
            ("2005-01-01", datetime.datetime(2020, 5, 1), True),
            ("2005-07-01", datetime.datetime(2021, 5, 1), True),
        ],
    )
    def test_has_celebrated_birthday_since_registration(self, birth_date, registration_datetime, expected_result):
        user = user_factories.BeneficiaryGrant18Factory(
            dateOfBirth=birth_date,
        )
        fraud_check_result_content = fraud_factories.UbbleContentFactory(registration_datetime=registration_datetime)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            resultContent=fraud_check_result_content,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=registration_datetime,
        )
        assert has_celebrated_birthday_since_registration(user) == expected_result

    def test_can_be_recredited(self):
        with freeze_time("2020-05-02"):
            user = user_factories.UnderageBeneficiaryFactory(subscription_age=15, dateOfBirth=datetime.date(2005, 5, 1))

            # User turned 15. They are credited a first time
            content = fraud_factories.UbbleContentFactory(
                user=user, birth_date="2005-05-01", registration_datetime=datetime.datetime.utcnow()
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=content,
                dateCreated=datetime.datetime(2020, 5, 1),
            )
            assert user.deposit.recredits == []
            assert can_be_recredited(user) is False

        with freeze_time("2021-05-02"):
            # User turned 16. They can be recredited
            assert can_be_recredited(user) is True

            recredit_underage_users()
            assert user.deposit.amount == 50
            assert user.deposit.recredits[0].recreditType == payments_models.RecreditType.RECREDIT_16
            assert user.recreditAmountToShow == 30
            assert can_be_recredited(user) is False

        with freeze_time("2022-05-02"):
            # User turned 17. They can be recredited
            assert can_be_recredited(user) is True

            recredit_underage_users()
            assert user.deposit.amount == 80
            assert user.deposit.recredits[1].recreditType == payments_models.RecreditType.RECREDIT_17
            assert user.recreditAmountToShow == 30
            assert can_be_recredited(user) is False

    def test_can_be_recredited_no_registration_datetime(self):
        with freeze_time("2020-05-02"):
            user = user_factories.UnderageBeneficiaryFactory(subscription_age=15, dateOfBirth=datetime.date(2005, 5, 1))
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
            )
            fraud_check.resultContent = content
        with freeze_time("2022-05-02"):
            assert can_be_recredited(user) is True

    def test_can_be_recredited_no_identity_fraud_check(self):
        user = user_factories.UserFactory(dateOfBirth=datetime.date(2005, 5, 1))
        with freeze_time("2020-05-02"):
            assert can_be_recredited(user) is False

    @pytest.mark.parametrize(
        "user_age,user_recredits,expected_result",
        [
            (15, [], False),
            (16, [], False),
            (17, [], False),
            (
                16,
                [{"type": payments_models.RecreditType.RECREDIT_16, "date_created": datetime.datetime(2020, 1, 1)}],
                True,
            ),
            (
                17,
                [{"type": payments_models.RecreditType.RECREDIT_16, "date_created": datetime.datetime(2020, 1, 1)}],
                False,
            ),
            (
                17,
                [
                    {"type": payments_models.RecreditType.RECREDIT_16, "date_created": datetime.datetime(2019, 1, 1)},
                    {"type": payments_models.RecreditType.RECREDIT_17, "date_created": datetime.datetime(2020, 1, 1)},
                ],
                True,
            ),
            (
                17,
                [{"type": payments_models.RecreditType.RECREDIT_17, "date_created": datetime.datetime(2020, 1, 1)}],
                True,
            ),
        ],
    )
    def test_has_been_recredited(self, user_age, user_recredits, expected_result):
        if 15 <= user_age <= 17:
            user = user_factories.UnderageBeneficiaryFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=user_age)
            )
        elif user_age == 18:
            user = user_factories.BeneficiaryGrant18Factory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=user_age)
            )

        for recredit in user_recredits:
            payments_factories.RecreditFactory(
                deposit=user.deposit, recreditType=recredit["type"], dateCreated=recredit["date_created"]
            )
        assert has_been_recredited(user) == expected_result

    def test_recredit_underage_users(self):
        # This test aims to check all the possible use cases for recredit_underage_users
        # We create users with different ages (15, 16, 17) with different stages of activation
        # Each user that is credited is supposed to have the corresponding fraud_checks.
        # - We create the fraud_checks manually to override the registration_datetime

        with freeze_time("2020-01-01"):
            # Create users, with their fraud checks

            # Already beneficiary users
            user_15 = user_factories.UnderageBeneficiaryFactory(subscription_age=15)
            user_16_not_recredited = user_factories.UnderageBeneficiaryFactory(subscription_age=16)
            user_16_already_recredited = user_factories.UnderageBeneficiaryFactory(subscription_age=16)
            user_17_not_recredited = user_factories.UnderageBeneficiaryFactory(subscription_age=17)
            user_17_only_recredited_at_16 = user_factories.UnderageBeneficiaryFactory(subscription_age=17)
            user_17_already_recredited = user_factories.UnderageBeneficiaryFactory(subscription_age=17)
            user_17_already_recredited_twice = user_factories.UnderageBeneficiaryFactory(subscription_age=17)

            id_check_application_date = datetime.datetime(2019, 7, 31)  # Asked for credit before birthday
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_15,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_15, birth_date="2004-08-01", registration_datetime=id_check_application_date
                ),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_16_not_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_16_not_recredited,
                    birth_date="2003-08-01",
                    registration_datetime=id_check_application_date,
                ),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_16_already_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_16_already_recredited,
                    birth_date="2003-08-01",
                    registration_datetime=id_check_application_date,
                ),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_not_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_not_recredited,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_only_recredited_at_16,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_only_recredited_at_16,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_already_recredited,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_already_recredited,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.datetime(2019, 12, 31),
                user=user_17_already_recredited_twice,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                resultContent=fraud_factories.EduconnectContentFactory(
                    user=user_17_already_recredited_twice,
                    birth_date="2002-08-01",
                    registration_datetime=id_check_application_date,
                ),
            )

            # Not beneficiary user
            user_17_not_activated = user_factories.UserFactory(dateOfBirth=datetime.datetime(2004, 5, 1))
            user_17_not_activated.add_underage_beneficiary_role()

            # Create the recredits that already happened
            payments_factories.RecreditFactory(
                deposit=user_16_already_recredited.deposit, recreditType=payments_models.RecreditType.RECREDIT_16
            )
            payments_factories.RecreditFactory(
                deposit=user_17_only_recredited_at_16.deposit,
                recreditType=payments_models.RecreditType.RECREDIT_16,
                dateCreated=datetime.datetime(2020, 1, 1),
            )
            payments_factories.RecreditFactory(
                deposit=user_17_already_recredited.deposit, recreditType=payments_models.RecreditType.RECREDIT_17
            )
            payments_factories.RecreditFactory(
                deposit=user_17_already_recredited_twice.deposit,
                recreditType=payments_models.RecreditType.RECREDIT_16,
                dateCreated=datetime.datetime(2019, 5, 1),
            )
            payments_factories.RecreditFactory(
                deposit=user_17_already_recredited_twice.deposit,
                recreditType=payments_models.RecreditType.RECREDIT_17,
                dateCreated=datetime.datetime(2020, 5, 1),
            )

        # Check the initial conditions
        assert payments_models.Recredit.query.count() == 5

        assert user_17_not_activated.deposit is None

        assert user_15.deposit.amount == 20
        assert user_16_not_recredited.deposit.amount == 30
        assert user_16_already_recredited.deposit.amount == 30
        assert user_17_not_recredited.deposit.amount == 30
        assert user_17_only_recredited_at_16.deposit.amount == 30
        assert user_17_already_recredited.deposit.amount == 30
        assert user_17_already_recredited_twice.deposit.amount == 30

        assert user_15.recreditAmountToShow is None
        assert user_16_not_recredited.recreditAmountToShow is None
        assert user_16_already_recredited.recreditAmountToShow is None
        assert user_17_not_recredited.recreditAmountToShow is None
        assert user_17_only_recredited_at_16.recreditAmountToShow is None
        assert user_17_already_recredited.recreditAmountToShow is None
        assert user_17_already_recredited_twice.recreditAmountToShow is None

        # Run the task
        with freeze_time("2020, 5, 2"):
            recredit_underage_users()

        # Check the results:
        # Assert we created new Recredits for user_16_not_recredited, user_17_not_recredited and user_17_only_recredited_at_16
        assert payments_models.Recredit.query.count() == 8
        assert user_15.deposit.recredits == []
        assert user_16_not_recredited.deposit.recredits[0].recreditType == payments_models.RecreditType.RECREDIT_16
        assert user_17_not_recredited.deposit.recredits[0].recreditType == payments_models.RecreditType.RECREDIT_17
        assert len(user_17_only_recredited_at_16.deposit.recredits) == 2
        assert (
            user_17_only_recredited_at_16.deposit.recredits[0].recreditType == payments_models.RecreditType.RECREDIT_17
        )

        assert user_15.deposit.amount == 20
        assert user_16_not_recredited.deposit.amount == 30 + 30
        assert user_16_already_recredited.deposit.amount == 30
        assert user_17_not_recredited.deposit.amount == 30 + 30
        assert user_17_only_recredited_at_16.deposit.amount == 30 + 30
        assert user_17_already_recredited.deposit.amount == 30
        assert user_17_already_recredited_twice.deposit.amount == 30

        assert user_15.recreditAmountToShow is None
        assert user_16_not_recredited.recreditAmountToShow == 30
        assert user_16_already_recredited.recreditAmountToShow is None
        assert user_17_not_recredited.recreditAmountToShow == 30
        assert user_17_only_recredited_at_16.recreditAmountToShow == 30
        assert user_17_already_recredited.recreditAmountToShow is None
        assert user_17_already_recredited_twice.recreditAmountToShow is None

    def test_recredit_around_the_year(self):
        with freeze_time("2015-05-01"):
            user_activated_at_15 = user_factories.UnderageBeneficiaryFactory(subscription_age=15)
            user_activated_at_16 = user_factories.UnderageBeneficiaryFactory(subscription_age=16)
            user_activated_at_17 = user_factories.UnderageBeneficiaryFactory(subscription_age=17)

        assert user_activated_at_15.deposit.amount == 20
        assert user_activated_at_16.deposit.amount == 30
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow is None
        assert user_activated_at_16.recreditAmountToShow is None
        assert user_activated_at_17.recreditAmountToShow is None

        # recredit the following year
        with freeze_time("2016-05-01"):
            recredit_underage_users()

        assert user_activated_at_15.deposit.amount == 50
        assert user_activated_at_16.deposit.amount == 60
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow == 30
        assert user_activated_at_16.recreditAmountToShow == 30
        assert user_activated_at_17.recreditAmountToShow is None

        # recrediting the day after does not affect the amount
        with freeze_time("2016-05-02"):
            recredit_underage_users()

        assert user_activated_at_15.deposit.amount == 50
        assert user_activated_at_16.deposit.amount == 60
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow == 30
        assert user_activated_at_16.recreditAmountToShow == 30
        assert user_activated_at_17.recreditAmountToShow is None

        # recredit the following year
        with freeze_time("2017-05-01"):
            recredit_underage_users()

        assert user_activated_at_15.deposit.amount == 80
        assert user_activated_at_16.deposit.amount == 60
        assert user_activated_at_17.deposit.amount == 30
        assert user_activated_at_15.recreditAmountToShow == 30
        assert user_activated_at_16.recreditAmountToShow == 30  # Was not reset
        assert user_activated_at_17.recreditAmountToShow is None

    def test_recredit_when_account_activated_on_the_birthday(self):
        with freeze_time("2020-05-01"):
            user = user_factories.UnderageBeneficiaryFactory(subscription_age=16, dateOfBirth=datetime.date(2004, 5, 1))
            assert user.deposit.amount == 30
            assert user.recreditAmountToShow is None

            # Should not recredit if the account was created the same day as the birthday
            recredit_underage_users()
            assert user.deposit.amount == 30
            assert user.recreditAmountToShow is None
