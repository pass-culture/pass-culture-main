import logging

import sqlalchemy as sa

from pcapi.connectors.dms import api as ds_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def sync_instructor_ids(procedure_number: int) -> None:
    logger.info("[DS] Sync instructor ids from DS procedure %s", procedure_number)

    ds_client = ds_api.DMSGraphQLClient()
    instructors = ds_client.get_instructors(procedure_number=procedure_number)
    emails = instructors.keys()

    users = (
        users_models.User.query.outerjoin(users_models.User.backoffice_profile)
        .filter(
            users_models.User.email.in_(list(emails)),
            perm_models.BackOfficeUserProfile.id.is_not(None),
        )
        .options(
            sa.orm.load_only(users_models.User.email),
            sa.orm.contains_eager(users_models.User.backoffice_profile).load_only(
                perm_models.BackOfficeUserProfile.dsInstructorId
            ),
        )
        .all()
    )

    for user in users:
        ds_instructor_id = instructors[user.email]
        if user.backoffice_profile.dsInstructorId != ds_instructor_id:
            user.backoffice_profile.dsInstructorId = ds_instructor_id
            db.session.add(user.backoffice_profile)

    db.session.flush()
