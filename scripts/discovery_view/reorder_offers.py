from models.db import db
from repository.discovery_view_queries import update, order_by_score_and_digital_offers


def update_offers_order_in_discovery_view():
    update(db.session, order_by_score_and_digital_offers)

