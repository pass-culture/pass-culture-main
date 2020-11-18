from typing import List

from pcapi.core.offers.models import Offer
from pcapi.models import Criterion
from pcapi.models import OfferCriterion
from pcapi.repository import repository


GONCOURT_ISBNS = [
    "9782072904073",
    "9782490155255",
    "9782743650940",
    "9782818051382",
    "9782021454901",
    "9782021455885",
    "9782330139346",
    "9782072895098",
    "9782823616644",
    "9782234088207",
    "9782259276788",
    "9782246815266",
    "9791032913710",
    "9782378560775",
]
GONCOURT_TAG = "Home_goncourtlyceens"
OFFER_CRITERION_BATCH_SIZE = 100


def add_criterion_to_goncourt_offers() -> None:
    print("Get offers matching Goncourt ISBNs")
    matching_offers = get_active_offers_matching_isbn(GONCOURT_ISBNS)
    print(f"Found {len(matching_offers)} offers")

    goncourt_criterion = Criterion.query.filter(Criterion.name == GONCOURT_TAG).one()

    print("Add tag for each offers")
    new_offer_criterion = []
    for offer in matching_offers:
        offer_criterion = OfferCriterion()
        offer_criterion.offer = offer
        offer_criterion.criterion = goncourt_criterion
        new_offer_criterion.append(offer_criterion)

        if len(new_offer_criterion) > OFFER_CRITERION_BATCH_SIZE:
            repository.save(*new_offer_criterion)
            new_offer_criterion = []

    repository.save(*new_offer_criterion)
    print("All offers tagged successfuly")


def get_active_offers_matching_isbn(product_isbns: List) -> List[Offer]:
    return Offer.query.filter(Offer.extraData["isbn"].astext.in_(product_isbns)).filter(Offer.isActive == True).all()
