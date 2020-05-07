from repository.discovery_view_queries import update, order_by_score_and_digital_offers
from models.db import db

def update_view_offers_order():
    update(db.session, order_by_score_and_digital_offers)