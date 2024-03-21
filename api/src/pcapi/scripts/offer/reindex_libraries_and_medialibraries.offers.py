from pcapi.core.categories.subcategories_v2 import ABO_BIBLIOTHEQUE
from pcapi.core.categories.subcategories_v2 import ABO_MEDIATHEQUE
from pcapi.core.offers.models import Offer
from pcapi.core.search import reindex_offer_ids


offer_ids = (
    Offer.query.filter(Offer.subcategoryId.in_(ABO_BIBLIOTHEQUE.id, ABO_MEDIATHEQUE.id)).with_entities(Offer.id).all()
)
reindex_offer_ids(offer_ids)
