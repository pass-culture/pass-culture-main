import typing

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only

from pcapi.core import search
from pcapi.core.criteria import models as criteria_models
from pcapi.core.offers import models
from pcapi.models import db


CriterionNames = typing.Collection[str]
Ids = typing.Collection[int]

Offers = typing.Collection[models.Offer]
Criteria = typing.Collection[criteria_models.Criterion]
OffersCriteria = typing.Collection[criteria_models.OfferCriterion]


def load_offers(offer_ids: Ids) -> Offers:
    return (
        db.session.query(models.Offer)
        .filter(models.Offer.id.in_(offer_ids))
        .options(joinedload(models.Offer.criteria))
        .options(load_only(models.Offer.id))
        .all()
    )


def load_criteria(criterion_names: CriterionNames) -> Criteria:
    return db.session.query(criteria_models.Criterion).filter(criteria_models.Criterion.name.in_(criterion_names)).all()


def find_offer_missing_criteria(offer: models.Offer, criteria: Criteria) -> OffersCriteria:
    offer_criterion_names = {criterion.name for criterion in offer.criteria}
    criterion_names = {criterion.name for criterion in criteria}

    missing_criterion_names = criterion_names - offer_criterion_names
    missing_offer_criteria = [criterion for criterion in criteria if criterion.name in missing_criterion_names]

    return [
        criteria_models.OfferCriterion(offerId=offer.id, criterionId=criterion.id)
        for criterion in missing_offer_criteria
    ]


def create_missing_mappings(offer_ids: Ids, criterion_names: CriterionNames, dry_run: bool = False) -> None:
    """
    Create missing offers <-> criteria mappings. The offer criteria must
    exist, they will not be created by this function.
    """
    offers = load_offers(offer_ids)
    criteria = load_criteria(criterion_names)

    for offer in offers:
        missing_offer_criteria_mapping = find_offer_missing_criteria(offer, criteria)
        print(f"offer: {offer.name}, found {len(missing_offer_criteria_mapping)} missing criterion(s)")

        for mapping in missing_offer_criteria_mapping:
            db.session.add(mapping)

    if not dry_run:
        db.session.commit()
        search.async_index_offer_ids(
            offer_ids,
            reason=search.IndexationReason.CRITERIA_LINK,
        )
    else:
        db.session.rollback()
