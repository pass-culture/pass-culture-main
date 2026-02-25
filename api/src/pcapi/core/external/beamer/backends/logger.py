import logging

from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.external.beamer.backends.base import BaseBackend
from pcapi.core.external.beamer.serialization import format_pro_attributes


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    def update_pro_user(self, pro_attributes: attributes_models.ProAttributes) -> None:
        request_data = format_pro_attributes(pro_attributes)

        if not pro_attributes.user_id:
            logger.info("Pro attributes %s not linked to a user, skipping", request_data)
            return

        logger.info("Updated pro user data on Beamer: %s", request_data)

    def delete_pro_user(self, user_id: int) -> None:
        logger.info("Deleted pro user data on Beamer: %s", user_id)
