from models.seen_offers import SeenOffer


def find_by_offer_id_and_user_id(offer_id: int, user_id: int) -> SeenOffer:
    return SeenOffer.query.filter_by(offerId=offer_id, userId=user_id).first()
