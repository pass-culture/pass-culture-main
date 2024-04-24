import datetime
import sys
from typing import List

from pydantic.v1.class_validators import validator
import sqlalchemy as sa

import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.routes.serialization import BaseModel
from pcapi.utils.date import METROPOLE_TIMEZONE
from pcapi.utils.date import local_datetime_to_default_timezone


class UserProInput(BaseModel):
    id: int
    eligibilityDate: datetime.datetime
    phase: int

    @validator("eligibilityDate", pre=True)
    def validate_eligibilityDate(cls, eligibilityDate: str) -> datetime.datetime:
        try:
            # print(eligibilityDate)
            d = datetime.datetime.strptime(eligibilityDate, "%d/%m/%Y %H:%M")
            d = local_datetime_to_default_timezone(d, METROPOLE_TIMEZONE)
            return d
        except ValueError:
            raise ValueError("Invalid date format")


def make_users_eligible_orm(
    ids: List[int], date_eligible: datetime.datetime = datetime.datetime.utcnow(), phase: int = 0
) -> None:
    ids = sorted(ids)
    user_loaded = (
        users_models.User.query.filter(users_models.User.id.in_(ids))
        .options(sa.orm.load_only(users_models.User.id, users_models.User.email))
        .options(sa.orm.joinedload(users_models.User.pro_new_nav_state))
        .all()
    )
    user_loaded = sorted(user_loaded, key=lambda x: x.id)
    assert len(user_loaded) == len(user_loaded), "Number of users in the csv file and in the database do not match"
    try:
        for index, user in enumerate(user_loaded):
            if user.id == ids[index]:
                if not user.pro_new_nav_state:
                    pro_new_nav_state = users_models.UserProNewNavState(userId=user.id, eligibilityDate=date_eligible)
                    db.session.add(pro_new_nav_state)
                else:
                    user.pro_new_nav_state.eligibilityDate = date_eligible
                    db.session.add(user.pro_new_nav_state)
                print(f"User {user.id} is now eligible email : {user.email}, at phase {phase}")
            else:
                raise ValueError(f"User ids do not match {user.id} != {ids[index]}")
        db.session.commit()
    except ValueError as e:
        print(e)
        db.session.rollback()
        sys.exit(1)
