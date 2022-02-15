from pcapi.core.offers.models import Mediation


def get_mediations_for_offers(offer_ids: list[int]) -> list[Mediation]:
    return Mediation.query.filter(Mediation.offerId.in_(offer_ids)).all()
