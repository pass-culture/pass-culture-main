import logging
import typing

from pcapi import settings
from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.external.beamer.backends.beamer import BeamerBackend
from pcapi.core.external.beamer.backends.logger import LoggerBackend


type Backend = BeamerBackend | LoggerBackend

BACKEND_BY_KEY: typing.Final[dict[str, type[Backend]]] = {
    "BeamerBackend": BeamerBackend,
    "LoggerBackend": LoggerBackend,
}

logger = logging.getLogger(__name__)


def _get_backend() -> Backend:
    return BACKEND_BY_KEY[settings.BEAMER_BACKEND]()


def update_beamer_user(pro_attributes: attributes_models.ProAttributes) -> None:
    _get_backend().update_pro_user(pro_attributes)


def delete_beamer_user(user_id: int) -> None:
    _get_backend().delete_pro_user(user_id)
