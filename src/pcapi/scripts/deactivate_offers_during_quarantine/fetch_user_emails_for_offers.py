from datetime import datetime

from pcapi.models import VenueSQLEntity, Offerer, UserOfferer, UserSQLEntity
from pcapi.scripts.deactivate_offers_during_quarantine.deactivate_offers import \
    build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine


def fetch_user_emails_for_offers_with_max_stock_date_between_today_and_end_of_quarantine(
        first_day_after_quarantine: datetime,
        today: datetime):
    offers_query = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(
        first_day_after_quarantine, today)
    users_info = offers_query.join(VenueSQLEntity) \
        .join(Offerer) \
        .join(UserOfferer) \
        .join(UserSQLEntity) \
        .distinct(UserSQLEntity.email) \
        .with_entities(UserSQLEntity.email) \
        .all()

    return [user_info.email for user_info in users_info]
