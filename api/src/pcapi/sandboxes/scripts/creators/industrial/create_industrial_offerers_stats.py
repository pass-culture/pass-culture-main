from datetime import datetime
from datetime import timedelta
import logging
from random import randint

from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models


logger = logging.getLogger(__name__)


def create_industrial_offerers_stats(
    offerers_by_name: dict[str, offerers_models.Offerer],
    event_offers_by_name: dict[str, offers_models.Offer],
) -> None:
    for _, offerer in offerers_by_name.items():
        # Create offerer daily views stats
        daily_views_stats = []
        views_count = randint(0, 1000)
        for i in range(180):
            views_count += randint(0, 1000) * randint(0, 10)
            daily_views_stats.append(
                offerers_models.OffererViewsModel(
                    eventDate=datetime.utcnow().date() - timedelta(days=180 - i),
                    numberOfViews=views_count,
                )
            )
        offerers_factories.OffererStatsFactory(
            offerer=offerer,
            table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
            jsonData=offerers_models.OffererStatsData(daily_views=daily_views_stats),
        )

        # Create offerer Top 3 offers stats
        event_offers_generator = list(
            el for el in event_offers_by_name.values() if el.venue.managingOffererId == offerer.id
        )
        top_3_offers_stats = []
        for el in event_offers_generator[:3]:
            top_3_offers_stats.append(offerers_models.TopOffersData(offerId=el.id, numberOfViews=el.id * 100))

        offerers_factories.OffererStatsFactory(
            offerer=offerer,
            table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
            jsonData=offerers_models.OffererStatsData(top_offers=top_3_offers_stats),
        )
