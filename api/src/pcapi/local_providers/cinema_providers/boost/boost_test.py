import datetime

from pcapi.connectors import boost
from pcapi.core.external_bookings.boost import constants
from pcapi.core.external_bookings.boost.client import BoostClientAPI
import pcapi.core.providers.repository as providers_repository
from pcapi.core.providers.repository import get_provider_by_local_class


start_date = datetime.date.today()
pattern_values = {
    "dateStart": start_date.strftime("%Y-%m-%d"),
    "dateEnd": (start_date + datetime.timedelta(days=constants.BOOST_SHOWS_INTERVAL_DAYS)).strftime("%Y-%m-%d"),
}


boost_stocks_provider_id = get_provider_by_local_class("BoostStocks").id
venue_providers = providers_repository.get_active_venue_providers_by_provider(boost_stocks_provider_id)


for venue_provider in venue_providers[:1]:
    cinema_id = venue_provider.venueIdAtOfferProvider
    client_boost = BoostClientAPI(cinema_id)
    json_data = boost.get_resource(cinema_id, boost.ResourceBoost.SHOWTIMES, params=None, pattern_values=pattern_values)
    print(json_data)
