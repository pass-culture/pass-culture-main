import logging

from pcapi.core.external.attributes import models as attributes_models


logger = logging.getLogger(__name__)


class BaseBackend:
    def update_pro_user(self, pro_attributes: attributes_models.ProAttributes) -> None:
        """Upserts the user into the Beamer database"""
        raise NotImplementedError()

    def delete_pro_user(self, user_id: int) -> None:
        """Deletes the user from the Beamer database"""
        raise NotImplementedError()
