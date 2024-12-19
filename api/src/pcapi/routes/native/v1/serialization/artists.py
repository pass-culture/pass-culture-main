import logging

from pcapi.routes.serialization import ConfiguredBaseModel


logger = logging.getLogger(__name__)


class ArtistResponse(ConfiguredBaseModel):
    id: str
    name: str
