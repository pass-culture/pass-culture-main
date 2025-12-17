import pcapi.core.educational.models as educational_models
from pcapi.core.finance.utils import CurrencyEnum
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas


def get_venue_currency(venue: offerers_models.Venue) -> CurrencyEnum:
    return CurrencyEnum.XPF if venue.is_caledonian else CurrencyEnum.EUR


def get_venue_activity_from_type_code(
    is_open_to_public: bool | None, type_code: offerers_schemas.VenueTypeCode | str | None
) -> offerers_models.Activity | None:
    """
    Temporary utility function to compute a Venue's Activity from the chosen VenueTypeCode
    If the activity is not easily infered from the VenueTypeCode, None is returned instead
    """
    if not is_open_to_public:
        return offerers_models.Activity.NOT_ASSIGNED
    if type_code is None:
        return None
    if not isinstance(type_code, offerers_schemas.VenueTypeCode):
        try:
            type_code = offerers_schemas.VenueTypeCode[type_code]
        except KeyError:
            return None
    match type_code:
        case offerers_schemas.VenueTypeCode.ARTISTIC_COURSE:
            return offerers_models.Activity.ART_SCHOOL
        case offerers_schemas.VenueTypeCode.BOOKSTORE:
            return offerers_models.Activity.BOOKSTORE
        case offerers_schemas.VenueTypeCode.CONCERT_HALL:
            return offerers_models.Activity.PERFORMANCE_HALL
        case offerers_schemas.VenueTypeCode.CREATIVE_ARTS_STORE:
            return offerers_models.Activity.CREATIVE_ARTS_STORE
        case offerers_schemas.VenueTypeCode.DISTRIBUTION_STORE:
            return offerers_models.Activity.DISTRIBUTION_STORE
        case offerers_schemas.VenueTypeCode.FESTIVAL:
            return offerers_models.Activity.FESTIVAL
        case offerers_schemas.VenueTypeCode.GAMES:
            return offerers_models.Activity.GAMES_CENTRE
        case offerers_schemas.VenueTypeCode.LIBRARY:
            return offerers_models.Activity.LIBRARY
        case offerers_schemas.VenueTypeCode.MOVIE:
            return offerers_models.Activity.CINEMA
        case offerers_schemas.VenueTypeCode.MUSEUM:
            return offerers_models.Activity.MUSEUM
        case offerers_schemas.VenueTypeCode.MUSICAL_INSTRUMENT_STORE:
            return offerers_models.Activity.MUSIC_INSTRUMENT_STORE
        case offerers_schemas.VenueTypeCode.PERFORMING_ARTS:
            return offerers_models.Activity.PERFORMANCE_HALL
        case offerers_schemas.VenueTypeCode.RECORD_STORE:
            return offerers_models.Activity.RECORD_STORE
        case offerers_schemas.VenueTypeCode.SCIENTIFIC_CULTURE:
            return offerers_models.Activity.SCIENCE_CENTRE
        case offerers_schemas.VenueTypeCode.TRAVELING_CINEMA:
            return offerers_models.Activity.CINEMA
        case _:
            return None


ACTIVITY_NAME_TO_VENUE_TYPE_CODE_MAPPING = {
    offerers_models.Activity.BOOKSTORE.name: offerers_schemas.VenueTypeCode.BOOKSTORE,
    offerers_models.Activity.LIBRARY.name: offerers_schemas.VenueTypeCode.LIBRARY,
    offerers_models.Activity.MUSEUM.name: offerers_schemas.VenueTypeCode.MUSEUM,
    offerers_models.Activity.CINEMA.name: offerers_schemas.VenueTypeCode.MOVIE,
    offerers_models.Activity.RECORD_STORE.name: offerers_schemas.VenueTypeCode.RECORD_STORE,
    offerers_models.Activity.MUSIC_INSTRUMENT_STORE.name: offerers_schemas.VenueTypeCode.MUSICAL_INSTRUMENT_STORE,
    offerers_models.Activity.CREATIVE_ARTS_STORE.name: offerers_schemas.VenueTypeCode.CREATIVE_ARTS_STORE,
    offerers_models.Activity.DISTRIBUTION_STORE.name: offerers_schemas.VenueTypeCode.DISTRIBUTION_STORE,
    offerers_models.Activity.PERFORMANCE_HALL.name: offerers_schemas.VenueTypeCode.PERFORMING_ARTS,
    offerers_models.Activity.FESTIVAL.name: offerers_schemas.VenueTypeCode.FESTIVAL,
    offerers_models.Activity.ARTS_CENTRE.name: offerers_schemas.VenueTypeCode.VISUAL_ARTS,
    offerers_models.Activity.ART_GALLERY.name: offerers_schemas.VenueTypeCode.VISUAL_ARTS,
    offerers_models.Activity.ART_SCHOOL.name: offerers_schemas.VenueTypeCode.ARTISTIC_COURSE,
    offerers_models.Activity.CULTURAL_CENTRE.name: offerers_schemas.VenueTypeCode.CULTURAL_CENTRE,
    offerers_models.Activity.COMMUNITY_CENTRE.name: offerers_schemas.VenueTypeCode.CULTURAL_CENTRE,
    offerers_models.Activity.SCIENCE_CENTRE.name: offerers_schemas.VenueTypeCode.SCIENTIFIC_CULTURE,
    offerers_models.Activity.HERITAGE_SITE.name: offerers_schemas.VenueTypeCode.PATRIMONY_TOURISM,
    offerers_models.Activity.TOURIST_INFORMATION_CENTRE.name: offerers_schemas.VenueTypeCode.PATRIMONY_TOURISM,
    offerers_models.Activity.OTHER.name: offerers_schemas.VenueTypeCode.OTHER,
}


def get_venue_type_code_from_activity(
    activity: offerers_models.Activity | offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic,
) -> offerers_schemas.VenueTypeCode:
    """
    Temporary utility function to compute a Venue's VenueTypeCode from the chosen Activity
    If no mapping exists, None is returned instead
    """
    assert activity.name != offerers_models.Activity.NOT_ASSIGNED.name
    return ACTIVITY_NAME_TO_VENUE_TYPE_CODE_MAPPING[activity.name]


EDUCATIONAL_DOMAINS_TO_VENUE_TYPE_CODE_MAPPING = {
    "Architecture": offerers_schemas.VenueTypeCode.PATRIMONY_TOURISM,
    "Arts du cirque et arts de la rue": offerers_schemas.VenueTypeCode.PERFORMING_ARTS,
    "Arts numériques": offerers_schemas.VenueTypeCode.ARTISTIC_COURSE,
    "Arts visuels, arts plastiques, arts appliqués": offerers_schemas.VenueTypeCode.VISUAL_ARTS,
    "Cinéma, audiovisuel": offerers_schemas.VenueTypeCode.MOVIE,
    "Culture scientifique, technique et industrielle": offerers_schemas.VenueTypeCode.SCIENTIFIC_CULTURE,
    "Danse": offerers_schemas.VenueTypeCode.PERFORMING_ARTS,
    "Design": offerers_schemas.VenueTypeCode.VISUAL_ARTS,
    "Développement durable": offerers_schemas.VenueTypeCode.SCIENTIFIC_CULTURE,
    "Univers du livre, de la lecture et des écritures": offerers_schemas.VenueTypeCode.OTHER,
    "Musique": offerers_schemas.VenueTypeCode.PERFORMING_ARTS,
    "Patrimoine": offerers_schemas.VenueTypeCode.PATRIMONY_TOURISM,
    "Photographie": offerers_schemas.VenueTypeCode.VISUAL_ARTS,
    "Théâtre, expression dramatique, marionnettes": offerers_schemas.VenueTypeCode.PERFORMING_ARTS,
    "Bande dessinée": offerers_schemas.VenueTypeCode.OTHER,
    "Média et information": offerers_schemas.VenueTypeCode.OTHER,
    "Mémoire": offerers_schemas.VenueTypeCode.PATRIMONY_TOURISM,
}


def get_venue_type_code_from_educational_domains(
    educational_domains: list[educational_models.EducationalDomain],
) -> offerers_schemas.VenueTypeCode:
    if not educational_domains:
        raise ValueError("EducationalDomain expected")
    venue_type_codes = set(
        EDUCATIONAL_DOMAINS_TO_VENUE_TYPE_CODE_MAPPING[domain.name] for domain in educational_domains
    )
    if len(venue_type_codes) > 1:
        # Use one random value other than "OTHER"
        return list(venue_type_codes - {offerers_schemas.VenueTypeCode.OTHER})[0]
    return list(venue_type_codes)[0]
