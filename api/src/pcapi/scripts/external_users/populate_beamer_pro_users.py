import logging
import math
import typing

import sqlalchemy.orm as sqla_orm

from pcapi.connectors import beamer
import pcapi.core.external.attributes.api as attributes_api
import pcapi.core.external.attributes.models as attributes_models
import pcapi.core.users.models as users_models


CHUNK_SIZE = 500

logger = logging.getLogger(__name__)


def populate_beamer_pro_users(from_user_id: typing.Optional[int] = None) -> None:
    pros_with_attributes = _get_pro_user_attributes(from_user_id)

    for pro_with_attributes in pros_with_attributes:
        beamer.update_beamer_user(pro_with_attributes)


def _get_pro_user_attributes(
    from_user_id: typing.Optional[int],
) -> typing.Generator[attributes_models.ProAttributes, None, None]:
    pro_users_query = (
        users_models.User.query.options(sqla_orm.load_only(users_models.User.id, users_models.User.email))
        .filter(users_models.User.has_pro_role.is_(True))  # type: ignore [attr-defined]
        .order_by(users_models.User.id)
    )
    if from_user_id:
        pro_users_query = pro_users_query.filter(users_models.User.id >= from_user_id)

    pro_count = pro_users_query.count()
    max_chunk_index = math.ceil(pro_count / CHUNK_SIZE)
    logger.info("Pro users count : %s", pro_count)
    logger.info("Total chunks : %s", max_chunk_index)

    for chunk_index in range(max_chunk_index):
        pro_users = pro_users_query.offset(chunk_index * CHUNK_SIZE).limit(CHUNK_SIZE)
        last_pro_id = None
        for pro_user in pro_users:
            last_pro_id = pro_user.id
            yield attributes_api.get_pro_attributes(pro_user.email)
        logger.info("Chunk %s/%s", chunk_index + 1, max_chunk_index)
        logger.info("Current progress %s%%", (chunk_index + 1) / max_chunk_index * 100)
        logger.info("Last user id %s", last_pro_id)
