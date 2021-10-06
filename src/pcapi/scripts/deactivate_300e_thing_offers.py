import os

from pcapi.core import search
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models.db import db


def deactivate_300e_thing_offers() -> None:
    stock_offer_ids = (
        Stock.query.filter(Stock.beginningDatetime == None, Stock.price > 300).with_entities(Stock.offerId).all()
    )
    offer_qs = Offer.query.filter(Offer.id.in_(stock_offer_ids)).filter(Offer.isEducational == False)
    offer_ids = [offer_id for offer_id, in offer_qs.with_entities(Offer.id)]
    print("Nombre d'offres desactivées: ", len(offer_ids))
    with open("offer_ids_to_reject.csv", "w") as out:
        out.write(",\n".join(str(offer_id) for offer_id in offer_ids))
    offer_qs.update({"isActive": False}, synchronize_session=False)
    db.session.commit()
    batch_size = int(os.environ.get("ALGOLIA_DELETING_OFFERS_CHUNK_SIZE"))
    print(batch_size)
    batches = [offer_ids[i : i + batch_size] for i in range(0, len(offer_ids), batch_size)]
    print(len(batches))
    for i, batch in enumerate(batches, start=1):
        print(f"Processing batch #{i}")
        search.unindex_offer_ids(batch)
