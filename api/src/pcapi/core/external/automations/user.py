from collections.abc import Iterable
from collections.abc import Iterator
from datetime import date
from datetime import datetime
from math import ceil

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from dateutil.relativedelta import relativedelta

import pcapi.core.finance.models as finance_models
from pcapi import settings
from pcapi.core.external.attributes import api as attributes_api
from pcapi.core.external.sendinblue import add_contacts_to_list
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.pc_object import BaseQuery


YIELD_COUNT_PER_DB_QUERY = 1000

# 4 or 5 leap years in 18 years
DAYS_IN_18_YEARS = 365 * 14 + 366 * 4


def get_young_users_emails_query() -> BaseQuery:
    return (
        db.session.query(User.email)
        .yield_per(YIELD_COUNT_PER_DB_QUERY)
        .filter(
            sa.not_(User.has_pro_role),
            sa.not_(User.has_admin_role),
        )
    )


def get_users_ex_beneficiary() -> list[User]:
    return (
        db.session.query(User.email)
        .join(User.deposits)
        .filter(
            User.is_beneficiary,
            sa.or_(
                finance_models.Deposit.expirationDate <= datetime.combine(date.today(), datetime.min.time()),
                sa.and_(
                    finance_models.Deposit.expirationDate > datetime.combine(date.today(), datetime.min.time()),
                    sa.func.get_wallet_balance(User.id, False) <= 0,
                ),
            ),
        )
        .yield_per(YIELD_COUNT_PER_DB_QUERY)
    )


def users_ex_beneficiary_automation() -> bool:
    """
    This automation is called every day to include all young users whose credit is expired: they either spent their full
    credit or reached expiration date with unused credit.

    Note that a young user may be in "jeunes-ex-benefs" list before "jeunes-expiration-M-3".

    List: jeunes-ex-benefs
    """
    user_emails = (email for (email,) in get_users_ex_beneficiary())
    return add_contacts_to_list(user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_EX_BENEFICIARY_ID)


def get_email_for_users_created_one_year_ago_per_month() -> Iterable[str]:
    first_day_of_month = (date.today() - relativedelta(months=12)).replace(day=1)
    last_day_of_month = first_day_of_month + relativedelta(months=1, days=-1)

    return (
        email
        for (email,) in get_young_users_emails_query().filter(
            User.dateCreated.between(
                datetime.combine(first_day_of_month, datetime.min.time()),
                datetime.combine(last_day_of_month, datetime.max.time()),
            )
        )
    )


def users_one_year_with_pass_automation() -> bool:
    """
    This automation is called once a month and includes young users who created their PassCulture account in the same
    month (from first to last day) one year earlier.

    Example: List produced in November 2021 contains all young users who created their account in November 2020

    List: jeunes-un-an-sur-le-pass
    """
    return add_contacts_to_list(
        get_email_for_users_created_one_year_ago_per_month(),
        settings.SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID,
    )


def get_users_whose_credit_expired_today() -> Iterator[User]:
    max_id = db.session.query(sa.func.max(User.id)).scalar()
    yesterday = datetime.combine(date.today() - relativedelta(days=1), datetime.min.time())
    today = datetime.combine(date.today(), datetime.min.time())

    for start in range(1, max_id, YIELD_COUNT_PER_DB_QUERY):
        end = start + (YIELD_COUNT_PER_DB_QUERY - 1)
        users = (
            db.session.query(User)
            .join(User.deposits)
            .filter(
                User.is_beneficiary,
                finance_models.Deposit.expirationDate > yesterday,
                finance_models.Deposit.expirationDate <= today,
                User.id.between(start, end),
            )
            .options(
                sa_orm.selectinload(User.deposits).selectinload(finance_models.Deposit.recredits),
            )
        )
        yield from users


def get_ex_underage_beneficiaries_who_can_no_longer_recredit() -> Iterator[User]:
    # No need to be updated on the exact birthday date, but ensure that we don't miss users born one day in leap years.
    max_id = db.session.query(sa.func.max(User.id)).scalar()
    days_19y = ceil(365.25 * 19)

    for start in range(1, max_id, YIELD_COUNT_PER_DB_QUERY):
        end = start + (YIELD_COUNT_PER_DB_QUERY - 1)
        users = (
            db.session.query(User)
            .filter(
                User.has_underage_beneficiary_role,
                User.dateOfBirth
                > datetime.combine(date.today() - relativedelta(days=days_19y + 1), datetime.min.time()),
                User.dateOfBirth <= datetime.combine(date.today() - relativedelta(days=days_19y), datetime.min.time()),
                User.id.between(start, end),
            )
            .options(
                sa_orm.selectinload(User.deposits).selectinload(finance_models.Deposit.recredits),
            )
        )
        yield from users


def users_whose_credit_expired_today_automation() -> None:
    """
    This automation is called every day to update external contacts attributes after young users reached their credit
    expiration, when they are no longer current beneficiaries and/or become former beneficiaries.
    Ex underage beneficiaries who don't get 18y credit on time become former beneficiaries after their birthday.
    """
    for user in get_users_whose_credit_expired_today():
        attributes_api.update_external_user(user)

    for user in get_ex_underage_beneficiaries_who_can_no_longer_recredit():
        attributes_api.update_external_user(user)
