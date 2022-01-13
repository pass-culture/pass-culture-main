import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.core.payments import factories as payments_factories
from pcapi.core.payments import models as payments_models
from pcapi.core.users import factories as user_factories
from pcapi.scripts.payment.user_recredit import has_been_recredited
from pcapi.scripts.payment.user_recredit import has_celebrated_their_birthday_since_activation
from pcapi.scripts.payment.user_recredit import recredit_underage_users


@pytest.mark.usefixtures("db_session")
class UserRecreditTest:
    @freeze_time("2021-07-01")
    @pytest.mark.parametrize(
        "birth_date,deposit_activation_date,expected_result",
        [("2006-01-01", "2021-05-01", False), ("2006-01-01", "2020-05-01", True), ("2006-07-01", "2020-05-01", True)],
    )
    def test_has_celebrated_their_birthday_since_activation(self, birth_date, deposit_activation_date, expected_result):
        user = user_factories.BeneficiaryGrant18Factory(
            dateOfBirth=birth_date,
        )
        payments_models.Deposit.query.delete()
        user_factories.DepositGrantFactory(user=user, dateCreated=deposit_activation_date)
        assert has_celebrated_their_birthday_since_activation(user) == expected_result

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
        with freeze_time("2020-01-01"):
            deposit_creation_date = datetime.datetime(2019, 7, 31)  # Create deposit before birthday
            user_15 = user_factories.UnderageBeneficiaryFactory(
                deposit__dateCreated=deposit_creation_date, subscription_age=15
            )
            user_16_not_recredited = user_factories.UnderageBeneficiaryFactory(
                deposit__dateCreated=deposit_creation_date,
                subscription_age=16,
            )
            user_16_already_recredited = user_factories.UnderageBeneficiaryFactory(
                deposit__dateCreated=deposit_creation_date,
                subscription_age=16,
            )
            user_17_not_recredited = user_factories.UnderageBeneficiaryFactory(
                deposit__dateCreated=deposit_creation_date,
                subscription_age=17,
            )
            user_17_only_recredited_at_16 = user_factories.UnderageBeneficiaryFactory(
                deposit__dateCreated=deposit_creation_date,
                subscription_age=17,
            )
            user_17_already_recredited = user_factories.UnderageBeneficiaryFactory(
                deposit__dateCreated=deposit_creation_date,
                subscription_age=17,
            )
            user_17_already_recredited_twice = user_factories.UnderageBeneficiaryFactory(
                deposit__dateCreated=deposit_creation_date,
                subscription_age=17,
            )

            user_17_not_activated = user_factories.UserFactory(dateOfBirth=datetime.datetime(2004, 5, 1))
            user_17_not_activated.add_underage_beneficiary_role()

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

        with freeze_time("2020, 5, 2"):
            recredit_underage_users()

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
