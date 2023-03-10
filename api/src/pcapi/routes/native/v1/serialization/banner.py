import dataclasses
import enum

from pcapi.routes.serialization import BaseModel


class BannerName(enum.Enum):
    GEOLOCATION_BANNER = "geolocation_banner"
    ACTIVATION_BANNER = "activation_banner"
    RETRY_IDENTITY_CHECK_BANNER = "retry_identity_check_banner"


class BannerTitle(enum.Enum):
    GEOLOCATION_BANNER = "Géolocalise-toi"
    ACTIVATION_BANNER = "Débloque tes {}\u00a0€"
    RETRY_IDENTITY_CHECK_BANNER = "Nous n’avons pas pu vérifier ton identité"


class BannerText(enum.Enum):
    GEOLOCATION_BANNER = "pour trouver des offres autour de toi"
    ACTIVATION_BANNER = "à dépenser sur l'application"
    RETRY_IDENTITY_CHECK_BANNER = "Réessaie dès maintenant"


@dataclasses.dataclass
class Banner:
    name: BannerName
    title: str
    text: str


class BannerResponse(BaseModel):
    banner: Banner | None
