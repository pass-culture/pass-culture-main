import logging

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db


logger = logging.getLogger(__name__)


def create_user_offerers() -> None:
    # Add a user and user_offerer for each offerer without one, except if the offerer has a provider
    logger.info("create_user_offerers")
    user = None
    count = 0

    query = (
        db.session.query(offerers_models.Offerer)
        .outerjoin(offerers_models.Offerer.UserOfferers)
        .outerjoin(offerers_models.Offerer.offererProviders)
        .filter(offerers_models.UserOfferer.id.is_(None), offerers_models.OffererProvider.id.is_(None))
    )
    for offerer in query:
        if user is None:
            user = users_factories.ProFactory.create(
                email="user.offerer@example.com", firstName="Compte pro", lastName="Rattaché"
            )

        offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)
        count += 1

    logger.info("created %d user offerers", count)
