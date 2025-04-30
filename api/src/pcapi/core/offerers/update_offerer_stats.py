from datetime import datetime
import logging

import sqlalchemy as sa

from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import OffererDailyViewsLast180Days
from pcapi.connectors.big_query.queries.offerer_stats import OffererTopOffersAndTotalViewsLast30Days
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)

PAGE_SIZE = 1000


def save_offerer_stats(daily_views: list[offerers_models.OffererStats]) -> None:
    try:
        db.session.bulk_save_objects(daily_views)
        db.session.commit()
    except sa.exc.IntegrityError:
        db.session.rollback()
        # batch failed, try inserting one by one
        for daily_view in daily_views:
            try:
                db.session.add(daily_view)
                db.session.commit()
            except sa.exc.IntegrityError:
                db.session.rollback()
                logger.error("save_offerer_stats failed for offerer #%i", daily_view.offererId, stack_info=True)


def update_offerer_daily_views_stats() -> None:
    daily_views_query = OffererDailyViewsLast180Days().execute(page_size=PAGE_SIZE)
    daily_views = []
    counter = 0
    for daily_views_row in daily_views_query:
        daily_views_model = offerers_models.OffererStats(
            offererId=daily_views_row.offererId,
            table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
            jsonData=dict(offerers_models.OffererStatsData(daily_views=list(daily_views_row.dailyViews[::-1]))),
            syncDate=datetime.utcnow(),
        )
        daily_views.append(daily_views_model)
        counter += 1
        if counter % PAGE_SIZE == 0:
            save_offerer_stats(daily_views)
            daily_views = []

    if daily_views:  # we need this because the last chunk might not be a full page
        save_offerer_stats(daily_views)


def update_offerer_top_views_stats() -> None:
    top_offers_query = OffererTopOffersAndTotalViewsLast30Days().execute(page_size=PAGE_SIZE)
    top_offers = []
    counter = 0
    for top_offers_row in top_offers_query:
        top_offers_model = offerers_models.OffererStats(
            offererId=top_offers_row.offererId,
            table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
            jsonData=dict(
                offerers_models.OffererStatsData(
                    top_offers=top_offers_row.topOffers, total_views_last_30_days=top_offers_row.totalViews
                )
            ),
            syncDate=datetime.utcnow(),
        )
        top_offers.append(top_offers_model)
        counter += 1
        if counter % PAGE_SIZE == 0:
            db.session.bulk_save_objects(top_offers)
            db.session.commit()
            top_offers = []
    if top_offers:  # we need this because the last chunk might not be a full page
        db.session.bulk_save_objects(top_offers)
        db.session.commit()


def delete_offerer_old_stats() -> None:
    offerers_ids = db.session.query(offerers_models.Offerer).with_entities(offerers_models.Offerer.id).all()
    index = 0
    step = 1000
    while offerers_ids_chunk := offerers_ids[index : index + step]:
        offerers_ids_chunk = [offerer_id for (offerer_id,) in offerers_ids_chunk]
        db.session.query(offerers_models.OffererStats).filter(
            offerers_models.OffererStats.offererId.in_(offerers_ids_chunk),
            offerers_models.OffererStats.syncDate < datetime.utcnow().date(),
        ).delete()
        db.session.commit()
        index += step
