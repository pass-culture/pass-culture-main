from datetime import datetime
from datetime import timedelta

from pcapi.models.db import db
from pcapi.models.seen_offers import SeenOffer


def find_by_offer_id_and_user_id(offer_id: int, user_id: int) -> SeenOffer:
    return SeenOffer.query.filter_by(offerId=offer_id, userId=user_id).first()


def remove_old_seen_offers():
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    delete_query = SeenOffer.__table__.delete().where(SeenOffer.dateSeen < one_month_ago)
    db.session.execute(delete_query)
    db.session.commit()
