from datetime import datetime
import logging
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy import not_
from sqlalchemy.orm import Query

from pcapi.core.users import constants
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.domain.beneficiary_pre_subscription.validator import EXCLUDED_DEPARTMENTS
from pcapi.domain.user_emails import send_newly_eligible_user_email
from pcapi.models import UserOfferer


logger = logging.getLogger(__name__)


# Basically, this is _is_postal_code_eligible refactored for queries
def _filter_by_eligible_postal_code(query: Query) -> Query:
    excluded_departments_arg = "(%s)%%" % ("|".join(EXCLUDED_DEPARTMENTS))
    return query.filter(not_(User.postalCode.op("SIMILAR TO")(excluded_departments_arg)))


def _get_eligible_users_created_between(
    start_date: datetime, end_date: datetime, max_number: Optional[int] = None
) -> list[User]:
    today = datetime.combine(datetime.today(), datetime.min.time())
    query = User.query.outerjoin(UserOfferer).filter(
        User.dateCreated.between(start_date, end_date),
        User.has_beneficiary_role == False,  # not already beneficiary
        User.isAdmin == False,  # not an admin
        UserOfferer.userId.is_(None),  # not a pro
        User.dateOfBirth > today - relativedelta(years=(constants.ELIGIBILITY_AGE_18 + 1)),  # less than 19yo
        User.dateOfBirth <= today - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # more than or 18yo
    )
    query = _filter_by_eligible_postal_code(query)
    if max_number:
        query = query.limit(max_number)
    return query.order_by(User.dateCreated).all()


def send_mail_to_potential_beneficiaries(
    start_date: datetime, end_date: datetime, max_number: Optional[int] = None
) -> None:
    # BEWARE: start_date and end_date are expected to be in UTC
    logger.info(
        (
            "Sending IDCheck mails to %s new users created between %s and %s "
            "to notify them they can start the idcheck process - if they eligible"
        ),
        (max_number or ""),
        start_date,
        end_date,
    )
    user = None
    try:
        for i, user in enumerate(_get_eligible_users_created_between(start_date, end_date, max_number)):
            if user.eligibility == EligibilityType.AGE18:
                if not send_newly_eligible_user_email(user):
                    print(f"Could not send mail to user {user.id}")
            if i % 100:
                print(f"Processed {i} users")
    finally:
        if user:
            print("Last user creation datetime: %s" % user.dateCreated)
        else:
            print("No user found within the timeframe")
