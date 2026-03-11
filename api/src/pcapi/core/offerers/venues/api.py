import dataclasses
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.offerers import models
from pcapi.models import db


Venues = typing.MutableSequence[models.Venue]


@dataclasses.dataclass
class SplittedVenues:
    others: Venues
    with_pending_validation: Venues


def fetch_user_venues_splitted_based_on_user_offerer_status(user_id: int) -> SplittedVenues:
    with_pending_validation: Venues = []
    others: Venues = []

    user_offerers = (
        db.session.query(models.UserOfferer)
        .join(models.UserOfferer.offerer)
        .filter(
            models.UserOfferer.userId == user_id,
            sa.or_(
                models.UserOfferer.isWaitingForValidation,
                models.UserOfferer.isValidated,
            ),
            sa.or_(
                models.Offerer.isWaitingForValidation,
                models.Offerer.isValidated,
                models.Offerer.isClosed,
            ),
        )
        .options(
            sa_orm.selectinload(models.UserOfferer.offerer)
            .selectinload(models.Offerer.managedVenues)
            .joinedload(models.Venue.offererAddress)
            .joinedload(models.OffererAddress.address)
        )
    )

    for user_offerer in user_offerers:
        all_venues = user_offerer.offerer.managedVenues
        existing_venues = filter(lambda v: not v.isSoftDeleted, all_venues)

        if user_offerer.isWaitingForValidation:
            with_pending_validation.extend(existing_venues)
        else:
            others.extend(existing_venues)

    return SplittedVenues(others=others, with_pending_validation=with_pending_validation)
