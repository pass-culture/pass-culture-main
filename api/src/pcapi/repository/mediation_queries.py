from pcapi.core.offers.models import Mediation


def find_by_id(mediation_id: str) -> Mediation:
    return Mediation.query.filter_by(id=mediation_id).first()


def get_mediations_for_offers(offer_ids: list[int]) -> list[Mediation]:
    return Mediation.query.filter(Mediation.offerId.in_(offer_ids)).all()
