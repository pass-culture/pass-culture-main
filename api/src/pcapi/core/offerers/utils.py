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
