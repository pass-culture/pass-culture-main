from pcapi.flask_app import app


app.app_context().push()

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.models import db


# def delete_obsolete_stock():
#     offerer_id = 13653
#     offerer = Offerer.query.get(13653)
#     venues_id = [x.id for x in db.session.query(Venue.id).filter(Venue.managingOffererId == 13653).all()]
#     assert offerer.name == "STUDIOMAP"
#     stock_to_deletes = (
#         db.session.query(Stock, Offer.id, Offer.venueId, Offer.name)
#         .join(Offer, Stock.offer)
#         .filter(Offer.venueId.in_(venues_id))
#         .order_by(Offer.id, Stock.beginningDatetime)
#     ).all()

#     venues = [v for v in Venue.query.filter(Venue.managingOffererId == offerer_id).all()]
#     for venue in venues:
#         offer_ids_tuple = Offer.query.filter(Offer.venueId == venue.id)
#         nb_offers = len(offer_ids_tuple)
#         print(f"{nb_offers} to update ...")


print("Change offers sub-categories")
offerer_id = 13653
offerer = Offerer.query.get(offerer_id)
assert offerer.name == "STUDIOMAP"
venues = Venue.query.filter(Venue.managingOffererId == offerer_id).all()

for venue in venues:
    print(f"Updating {venue.name}({venue.id})...")
    offer_ids_tuple = Offer.query.filter(Offer.venueId == venue.id)

    nb_offers = len(offer_ids_tuple)
    print(f"{nb_offers} to update ...")
    offer_ids_tuple.update({"subcategoryId": "ABO_PRATIQUE_ART"}, synchronize_session=False)
    for current_index in range(0, nb_offers):
        current_offer_id = offer_ids_tuple[current_index]
        last_stock = (
            Stock.query.filter(Stock.offerId == current_offer_id, not Stock.isSoftDeleted)
            .order_by(Stock.beginningDatetime.desc())
            .first()
        )
        stock_to_delete = Stock.query.filter(Stock.offerId == current_offer_id, Stock.id != last_stock.id)
        stock_to_delete.update({"isSoftDeleted": True}, synchronize_session=False)
        last_stock.update({"beginningDatetime": None}, {"bookingLimitDatetime": None}, synchronize_session=False)
    db.session.commit()


print("Change offers subcategories done !")
