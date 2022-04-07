import logging

import pcapi.core.offerers.factories as offerers_factories
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def create_industrial_user_offerers(users_by_name, offerers_by_name):  # type: ignore [no-untyped-def]
    logger.info("create_industrial_user_offerers")

    user_offerers_by_name = {}

    # special validation
    user = users_by_name["pro93 real-validation"]
    offerer = offerers_by_name["414819409 lat:48.8 lon:1.48"]
    user_offerers_by_name[
        "pro93 real-validation / 414819409 lat:48.8 lon:1.48"
    ] = offerers_factories.UserOffererFactory(offerer=offerer, user=user)

    # loop on users
    for (user_name, user) in users_by_name.items():

        for (offerer_name, offerer) in offerers_by_name.items():

            if (
                PostalCode(offerer.postalCode).get_departement_code() != user.departementCode
                or "real-validation" in user_name
            ):
                continue

            user_offerers_by_name["{} / {}".format(user_name, offerer_name)] = offerers_factories.UserOffererFactory(
                offerer=offerer, user=user
            )

    repository.save(*user_offerers_by_name.values())

    logger.info("created %d user_offerers", len(user_offerers_by_name))

    return user_offerers_by_name
