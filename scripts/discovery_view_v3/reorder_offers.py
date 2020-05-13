from models.db import db
from repository.discovery_view_v3_queries import update, _order_by_score_and_digital_offers


def update_offers_order_in_discovery_view_v3():
    update(db.session, _order_by_score_and_digital_offers)

