from collections.abc import Iterable
from datetime import date
from datetime import datetime
from math import ceil
from typing import List

from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import BaseQuery
from sqlalchemy import func
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import or_

from pcapi import settings
from pcapi.core.payments.models import Deposit
from pcapi.core.users.external import update_external_user
from pcapi.core.users.external.sendinblue import add_contacts_to_list
from pcapi.core.users.models import User
from pcapi.models import db


YIELD_COUNT_PER_DB_QUERY = 1000

# 4 or 5 leap years in 18 years
DAYS_IN_18_YEARS = 365 * 14 + 366 * 4


def get_young_users_emails_query() -> BaseQuery:
    return (
        db.session.query(User.email)
        .yield_per(YIELD_COUNT_PER_DB_QUERY)
        .filter(User.has_pro_role.is_(False))  # type: ignore [attr-defined]
        .filter(User.has_admin_role.is_(False))  # type: ignore [attr-defined]
    )


def get_emails_who_will_turn_eighteen_in_one_month() -> Iterable[str]:
    # Keep in days and not years and months to ensure that we get birth dates continuously day after day
    # Otherwise, 2022-02-28 - 18y + 30m = 2004-03-29
    #            2022-03-01 - 18y + 30m = 2004-03-31
    #            => users born on 2004-03-30 would be missed
    expected_birth_date = date.today() - relativedelta(days=DAYS_IN_18_YEARS - 30)

    return (
        email for email, in get_young_users_emails_query().filter(func.date(User.dateOfBirth) == expected_birth_date)
    )


def users_turned_eighteen_automation() -> bool:
    """
    This automation is called every day and includes all young users who will turn 18 exactly 30 days later.

    List: jeunes-18-m-1
    """
    return add_contacts_to_list(
        get_emails_who_will_turn_eighteen_in_one_month(),
        settings.SENDINBLUE_AUTOMATION_YOUNG_18_IN_1_MONTH_LIST_ID,
        clear_list_first=True,
    )


def get_users_beneficiary_credit_expiration_within_next_3_months() -> List[User]:
    return (
        db.session.query(User.email)
        .yield_per(YIELD_COUNT_PER_DB_QUERY)
        .join(User.deposits)
        .filter(User.is_beneficiary.is_(True))  # type: ignore [attr-defined]
        .filter(
            Deposit.expirationDate.between(
                datetime.combine(date.today(), datetime.min.time()),
                datetime.combine(date.today() + relativedelta(days=90), datetime.max.time()),
            )
        )
    )


def users_beneficiary_credit_expiration_within_next_3_months_automation() -> bool:
    """
    This automation is called every day and includes all young user whose pass expires in the next 3 months. They may
    have remaining unspent credit or not.

    User enters in the list on the 90th day before expiration date and leaves the list the day after expiration date.

    List: jeunes-expiration-M-3
    """
    user_emails = (email for email, in get_users_beneficiary_credit_expiration_within_next_3_months())
    return add_contacts_to_list(
        user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_EXPIRATION_M3_ID, clear_list_first=True
    )


def get_users_ex_beneficiary() -> List[User]:
    return (
        db.session.query(User.email)
        .join(User.deposits)
        .filter(User.is_beneficiary.is_(True))  # type: ignore [attr-defined]
        .filter(
            or_(
                Deposit.expirationDate <= datetime.combine(date.today(), datetime.min.time()),
                and_(
                    Deposit.expirationDate > datetime.combine(date.today(), datetime.min.time()),
                    func.get_wallet_balance(User.id, False) <= 0,
                ),
            )
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
    user_emails = (email for email, in get_users_ex_beneficiary())
    return add_contacts_to_list(
        user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_EX_BENEFICIARY_ID, clear_list_first=False
    )


def get_email_for_inactive_user_since_thirty_days() -> Iterable[str]:
    date_30_days_ago = date.today() - relativedelta(days=30)

    return (
        email
        for email, in get_young_users_emails_query().filter(func.date(User.lastConnectionDate) <= date_30_days_ago)
    )


def users_inactive_since_30_days_automation() -> bool:
    """
    This automation called every day updates the list of users who are inactive since 30 days or more:
    - adds or keeps any young user who did not connect to the app in the least 30 days (even if the email has been sent;
      marketing filters will ensure that he or she receives the email only once)
    - removes any inactive user who connected recently

    List: jeunes-utilisateurs-inactifs
    """
    return add_contacts_to_list(
        get_email_for_inactive_user_since_thirty_days(),
        settings.SENDINBLUE_AUTOMATION_YOUNG_INACTIVE_30_DAYS_LIST_ID,
        clear_list_first=True,
    )


def get_email_for_users_created_one_year_ago_per_month() -> Iterable[str]:
    first_day_of_month = (date.today() - relativedelta(months=12)).replace(day=1)
    last_day_of_month = first_day_of_month + relativedelta(months=1, days=-1)

    return (
        email
        for email, in get_young_users_emails_query().filter(
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
        clear_list_first=True,
    )


def get_users_whose_credit_expired_today() -> List[User]:
    return (
        db.session.query(User)
        .join(User.deposits)
        .filter(User.is_beneficiary.is_(True))  # type: ignore [attr-defined]
        .filter(
            and_(
                Deposit.expirationDate > datetime.combine(date.today() - relativedelta(days=1), datetime.min.time()),
                Deposit.expirationDate <= datetime.combine(date.today(), datetime.min.time()),
            )
        )
        .yield_per(YIELD_COUNT_PER_DB_QUERY)
    )


def get_ex_underage_beneficiaries_who_can_no_longer_recredit() -> List[User]:
    # No need to be updated on the exact birthday date, but ensure that we don't miss users born one day in leap years.
    days_19y = ceil(365.25 * 19)
    return (
        db.session.query(User)
        .filter(User.has_underage_beneficiary_role.is_(True))  # type: ignore [attr-defined]
        .filter(
            and_(
                User.dateOfBirth
                > datetime.combine(date.today() - relativedelta(days=days_19y + 1), datetime.min.time()),
                User.dateOfBirth <= datetime.combine(date.today() - relativedelta(days=days_19y), datetime.min.time()),
            )
        )
        .yield_per(YIELD_COUNT_PER_DB_QUERY)
    )


def users_whose_credit_expired_today_automation() -> None:
    """
    This automation is called every day to update external contacts attributes after young users reached their credit
    expiration, when they are no longer current beneficiaries and/or become former beneficiaries.
    Ex underage beneficiaries who don't get 18y credit on time become former beneficiaries after their birthday.
    """
    for user in get_users_whose_credit_expired_today():
        update_external_user(user)

    for user in get_ex_underage_beneficiaries_who_can_no_longer_recredit():
        update_external_user(user)
