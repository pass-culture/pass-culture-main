import datetime
import decimal

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.scripts.reduce_credit_or_suspend_user.main import reduce_or_expire_user_credit
from pcapi.utils import transaction_manager


@pytest.mark.usefixtures("db_session")
def test_credit_reduction():
    author = users_factories.UserFactory.create()

    before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
    next_year = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1)
    in_three_years = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=3)
    users = []
    for _i in range(2):
        with time_machine.travel(before_decree):
            user = users_factories.BeneficiaryFactory.create(
                age=17,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
            finance_factories.RecreditFactory.create(
                deposit=user.deposit, recreditType=finance_models.RecreditType.RECREDIT_17
            )

        with time_machine.travel(next_year):
            user.deposit.expirationDate = next_year
            new_deposit = users_factories.DepositGrantFactory.create(user=user, expirationDate=in_three_years)
            recredit = finance_factories.RecreditFactory.create(
                deposit=new_deposit,
                recreditType=finance_models.RecreditType.RECREDIT_17,
                amount=finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3,
            )
            new_deposit.amount += recredit.amount
            starting_deposit_amount = new_deposit.amount

        users.append(user)

    with transaction_manager.atomic():
        reduce_or_expire_user_credit(should_update_external_user=False, author_id=author.id)

    for user in users:
        assert user.deposit.amount == starting_deposit_amount - finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3


@pytest.mark.usefixtures("db_session")
def test_credit_expiration():
    author = users_factories.UserFactory.create()

    before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
    next_year = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1)
    in_three_years = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=3)
    users = []
    for _i in range(2):
        with time_machine.travel(before_decree):
            user = users_factories.BeneficiaryFactory.create(
                age=17,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
            finance_factories.RecreditFactory.create(
                deposit=user.deposit, recreditType=finance_models.RecreditType.RECREDIT_17
            )

        with time_machine.travel(next_year):
            user.deposit.expirationDate = next_year
            new_deposit = users_factories.DepositGrantFactory.create(user=user, expirationDate=in_three_years)
            recredit = finance_factories.RecreditFactory.create(
                deposit=new_deposit,
                recreditType=finance_models.RecreditType.RECREDIT_17,
                amount=finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3,
            )
            new_deposit.amount += recredit.amount
            starting_deposit_amount = new_deposit.amount

            bookings_factories.BookingFactory.create(user=user, amount=decimal.Decimal("167.89"))

        users.append(user)

    with transaction_manager.atomic():
        reduce_or_expire_user_credit(should_update_external_user=False, author_id=author.id)

    for user in users:
        assert user.deposit.expirationDate <= datetime.datetime.now(tz=None)
        assert user.deposit.amount == starting_deposit_amount


@pytest.mark.usefixtures("db_session")
def test_credit_no_reduction():
    author = users_factories.UserFactory.create()

    before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
    next_year = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1)
    in_three_years = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=3)
    users = []
    for _i in range(2):
        with time_machine.travel(before_decree):
            user = users_factories.BeneficiaryFactory.create(
                age=17,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )

        with time_machine.travel(next_year):
            user.deposit.expirationDate = next_year
            new_deposit = users_factories.DepositGrantFactory.create(user=user, expirationDate=in_three_years)
            recredit = finance_factories.RecreditFactory.create(
                deposit=new_deposit,
                recreditType=finance_models.RecreditType.RECREDIT_17,
                amount=finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3,
            )
            new_deposit.amount += recredit.amount
            starting_deposit_amount = new_deposit.amount

            bookings_factories.BookingFactory.create(user=user, amount=decimal.Decimal("167.89"))

        users.append(user)

    with transaction_manager.atomic():
        reduce_or_expire_user_credit(should_update_external_user=False, author_id=author.id)

    for user in users:
        assert user.deposit.expirationDate >= datetime.datetime.now(tz=None)
        assert user.deposit.amount == starting_deposit_amount


@pytest.mark.usefixtures("db_session")
def test_credit_no_expiration():
    author = users_factories.UserFactory.create()

    before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
    next_year = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1)
    in_three_years = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=3)
    users = []
    for _i in range(2):
        with time_machine.travel(before_decree):
            user = users_factories.BeneficiaryFactory.create(
                age=17,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )

        with time_machine.travel(next_year):
            user.deposit.expirationDate = next_year
            new_deposit = users_factories.DepositGrantFactory.create(user=user, expirationDate=in_three_years)
            recredit = finance_factories.RecreditFactory.create(
                deposit=new_deposit,
                recreditType=finance_models.RecreditType.RECREDIT_17,
                amount=finance_conf.GRANTED_DEPOSIT_AMOUNT_17_v3,
            )
            new_deposit.amount += recredit.amount
            starting_deposit_amount = new_deposit.amount

            bookings_factories.BookingFactory.create(user=user, amount=decimal.Decimal("167.89"))

        users.append(user)

    with transaction_manager.atomic():
        reduce_or_expire_user_credit(should_update_external_user=False, author_id=author.id)

    for user in users:
        assert user.deposit.expirationDate >= datetime.datetime.now(tz=None)
        assert user.deposit.amount == starting_deposit_amount
