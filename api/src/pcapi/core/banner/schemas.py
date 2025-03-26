import dataclasses
import enum

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class BannerQueryParams(BaseModel):
    is_geolocated: bool = False

    class Config:
        alias_generator = to_camel


class BannerName(enum.Enum):
    GEOLOCATION_BANNER = "geolocation_banner"
    ACTIVATION_BANNER = "activation_banner"
    RETRY_IDENTITY_CHECK_BANNER = "retry_identity_check_banner"
    TRANSITION_17_18_BANNER = "transition_17_18_banner"


class BannerTitle(enum.Enum):
    GEOLOCATION_BANNER = "Géolocalise-toi"
    ACTIVATION_BANNER = "Débloque tes {}€"
    RETRY_IDENTITY_CHECK_BANNER = "Nous n’avons pas pu vérifier ton identité"
    TRANSITION_17_18_BANNER = "Débloque tes {}€"


class BannerText(enum.Enum):
    GEOLOCATION_BANNER = "pour trouver des offres autour de toi"
    ACTIVATION_BANNER = "à dépenser sur l'application"
    RETRY_IDENTITY_CHECK_BANNER = "Réessaie dès maintenant"
    TRANSITION_17_18_BANNER_ID_CHECK_DONE = "Confirme tes informations"
    TRANSITION_17_18_BANNER_ID_CHECK_TODO = "Vérifie ton identité"


@dataclasses.dataclass
class Banner:
    name: BannerName
    title: str
    text: str


class BannerResponse(BaseModel):
    banner: Banner | None
