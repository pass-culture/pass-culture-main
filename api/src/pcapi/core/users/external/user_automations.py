from datetime import date
from datetime import datetime
from typing import List

from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import or_

from pcapi import settings
from pcapi.core.payments.models import Deposit
from pcapi.core.users.external.sendinblue import add_contacts_to_list
from pcapi.core.users.models import User


YIELD_COUNT_PER_DB_QUERY = 1000

# 4 or 5 leap years in 18 years
DAYS_IN_18_YEARS = 365 * 14 + 366 * 4


def get_young_users_emails_query() -> Query:
    return (
        User.query.yield_per(YIELD_COUNT_PER_DB_QUERY)
        .options(load_only(User.email))
        .filter(User.has_pro_role.is_(False))
        .filter(User.has_admin_role.is_(False))
    )


def get_users_who_will_turn_eighteen_in_one_month() -> List[User]:
    # Keep in days and not years and months to ensure that we get birth dates continuously day after day
    # Otherwise, 2022-02-28 - 18y + 30m = 2004-03-29
    #            2022-03-01 - 18y + 30m = 2004-03-31
    #            => users born on 2004-03-30 would be missed
    expected_birth_date = date.today() - relativedelta(days=DAYS_IN_18_YEARS - 30)

    return get_young_users_emails_query().filter(func.date(User.dateOfBirth) == expected_birth_date).all()


def users_turned_eighteen_automation() -> bool:
    """
    This automation is called every day and includes all young users who will turn 18 exactly 30 days later.

    List: jeunes-18-m-1
    """
    user_emails = (user.email for user in get_users_who_will_turn_eighteen_in_one_month())
    return add_contacts_to_list(
        user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_18_IN_1_MONTH_LIST_ID, clear_list_first=True
    )


def get_users_beneficiary_credit_expiration_within_next_3_months() -> List[User]:
    return (
        User.query.yield_per(YIELD_COUNT_PER_DB_QUERY)
        .options(load_only(User.email))
        .join(User.deposits)
        .filter(User.is_beneficiary.is_(True))
        .filter(
            Deposit.expirationDate.between(
                datetime.combine(date.today(), datetime.min.time()),
                datetime.combine(date.today() + relativedelta(days=90), datetime.max.time()),
            )
        )
        .all()
    )


def users_beneficiary_credit_expiration_within_next_3_months_automation() -> bool:
    """
    This automation is called every day and includes all young user whose pass expires in the next 3 months. They may
    have remaining unspent credit or not.

    User enters in the list on the 90th day before expiration date and leaves the list the day after expiration date.

    List: jeunes-expiration-M-3
    """
    user_emails = (user.email for user in get_users_beneficiary_credit_expiration_within_next_3_months())
    return add_contacts_to_list(
        user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_EXPIRATION_M3_ID, clear_list_first=True
    )


def get_users_ex_beneficiary() -> List[User]:
    return (
        User.query.yield_per(YIELD_COUNT_PER_DB_QUERY)
        .options(load_only(User.email))
        .join(User.deposits)
        .filter(User.is_beneficiary.is_(True))
        .filter(
            or_(
                Deposit.expirationDate <= datetime.combine(date.today(), datetime.min.time()),
                and_(
                    Deposit.expirationDate > datetime.combine(date.today(), datetime.min.time()),
                    func.get_wallet_balance(User.id, False) <= 0,
                ),
            )
        )
        .all()
    )


def users_ex_beneficiary_automation() -> bool:
    """
    This automation is called every day to include all young users whose credit is expired: they either spent their full
    credit or reached expiration date with unused credit.

    Note that a young user may be in "jeunes-ex-benefs" list before "jeunes-expiration-M-3".

    List: jeunes-ex-benefs
    """
    user_emails = (user.email for user in get_users_ex_beneficiary())
    return add_contacts_to_list(
        user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_EX_BENEFICIARY_ID, clear_list_first=False
    )


def get_inactive_user_since_thirty_days() -> List[User]:
    date_30_days_ago = date.today() - relativedelta(days=30)

    return get_young_users_emails_query().filter(func.date(User.lastConnectionDate) <= date_30_days_ago).all()


def users_inactive_since_30_days_automation() -> bool:
    """
    This automation called every day updates the list of users who are inactive since 30 days or more:
    - adds or keeps any young user who did not connect to the app in the least 30 days (even if the email has been sent;
      marketing filters will ensure that he or she receives the email only once)
    - removes any inactive user who connected recently

    List: jeunes-utilisateurs-inactifs
    """
    user_emails = (user.email for user in get_inactive_user_since_thirty_days())
    return add_contacts_to_list(
        user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_INACTIVE_30_DAYS_LIST_ID, clear_list_first=True
    )


def get_users_by_month_created_one_year_before() -> List[User]:
    first_day_of_month = (date.today() - relativedelta(months=12)).replace(day=1)
    last_day_of_month = first_day_of_month + relativedelta(months=1, days=-1)

    return (
        get_young_users_emails_query()
        .filter(
            User.dateCreated.between(
                datetime.combine(first_day_of_month, datetime.min.time()),
                datetime.combine(last_day_of_month, datetime.max.time()),
            )
        )
        .all()
    )


def users_one_year_with_pass_automation() -> bool:
    """
    This automation is called once a month and includes young users who created their PassCulture account in the same
    month (from first to last day) one year earlier.

    Example: List produced in November 2021 contains all young users who created their account in November 2020

    List: jeunes-un-an-sur-le-pass
    """
    user_emails = (user.email for user in get_users_by_month_created_one_year_before())
    return add_contacts_to_list(
        user_emails, settings.SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID, clear_list_first=True
    )
