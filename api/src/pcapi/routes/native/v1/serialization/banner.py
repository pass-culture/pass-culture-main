import dataclasses
import enum

from pcapi.routes.serialization import BaseModel


class BannerName(enum.Enum):
    GEOLOCATION_BANNER = "geolocation_banner"
    ACTIVATION_BANNER = "activation_banner"


@dataclasses.dataclass
class Banner:
    name: BannerName
    title: str
    text: str


class BannerResponse(BaseModel):
    banner: Banner | None
