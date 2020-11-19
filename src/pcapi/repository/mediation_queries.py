from typing import List

from pcapi.core.offers.models import MediationSQLEntity


def find_by_id(mediation_id: str) -> MediationSQLEntity:
    return MediationSQLEntity.query.filter_by(id=mediation_id).first()


def get_mediations_for_offers(offer_ids: List[int]) -> List[MediationSQLEntity]:
    return MediationSQLEntity.query.filter(MediationSQLEntity.offerId.in_(offer_ids)).all()
