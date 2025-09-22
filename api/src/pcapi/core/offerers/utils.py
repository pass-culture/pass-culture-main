from pcapi.core.finance.utils import CurrencyEnum
from pcapi.core.offerers import models as offerers_models


def get_venue_currency(venue: offerers_models.Venue) -> CurrencyEnum:
    return CurrencyEnum.XPF if venue.is_caledonian else CurrencyEnum.EUR
