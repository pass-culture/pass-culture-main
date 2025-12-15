import enum
from typing import Annotated

import pydantic as pydantic_v2
from pydantic import BeforeValidator


# needed because original VenueTypeCode uses pydantic v1... which
# is not compatible with v2 model used here.
# ----- original data and deprecation notice ----- #
# [DEPRECATION NOTICE - ETA T1 2026]
# This typology is to be replaced by Activity (Venue's main business activity) and EducationalDomains (Venue's cultural domains)
# Once activity and domains are implemented and data migrated, this will be deleted
# Keep this enum ordered and with the OTHER value first
class VenueTypeCode(enum.Enum):
    OTHER = "Autre"
    VISUAL_ARTS = "Arts visuels, arts plastiques et galeries"
    LIBRARY = "Bibliothèque ou médiathèque"
    CULTURAL_CENTRE = "Centre culturel"
    MOVIE = "Cinéma - Salle de projections"
    TRAVELING_CINEMA = "Cinéma itinérant"
    ARTISTIC_COURSE = "Cours et pratique artistiques"
    SCIENTIFIC_CULTURE = "Culture scientifique"
    FESTIVAL = "Festival"
    GAMES = "Jeux / Jeux vidéos"
    BOOKSTORE = "Librairie"
    CREATIVE_ARTS_STORE = "Magasin arts créatifs"
    DISTRIBUTION_STORE = "Magasin de distribution de produits culturels"
    RECORD_STORE = "Musique - Disquaire"
    MUSICAL_INSTRUMENT_STORE = "Musique - Magasin d’instruments"
    CONCERT_HALL = "Musique - Salle de concerts"
    MUSEUM = "Musée"
    DIGITAL = "Offre numérique"
    PATRIMONY_TOURISM = "Patrimoine et tourisme"
    PERFORMING_ARTS = "Spectacle vivant"


def parse_venue_type_code(code: str | VenueTypeCode) -> VenueTypeCode:
    if isinstance(code, str):
        return VenueTypeCode[code]
    return code


class Venue(pydantic_v2.BaseModel):
    id: int
    code: Annotated[VenueTypeCode, BeforeValidator(parse_venue_type_code)]
    has_ticketing: bool = False
