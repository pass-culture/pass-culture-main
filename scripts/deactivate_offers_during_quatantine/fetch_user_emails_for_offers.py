from datetime import datetime

from models import Venue, Offerer, UserOfferer, User
from scripts.deactivate_offers_during_quatantine.deactivate_offers import \
    build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine


def fetch_user_emails_for_offers_with_max_stock_date_between_today_and_end_of_quarantine(
        first_day_after_quarantine: datetime,
        today: datetime):
    offers_query = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(
        first_day_after_quarantine, today)
    users_info = offers_query.join(Venue) \
        .join(Offerer) \
        .join(UserOfferer) \
        .join(User) \
        .distinct(User.email) \
        .with_entities(User.email) \
        .all()

    return [user_info.email for user_info in users_info]
