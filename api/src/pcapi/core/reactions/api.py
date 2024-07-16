import datetime

from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories.subcategories_v2 import SEANCE_CINE
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.reactions.models import Reaction
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.models import db


def update_or_create_reaction(user_id: int, offer_id: int, reaction_type: ReactionTypeEnum) -> Reaction:
    offer = Offer.query.get(offer_id)
    if offer.productId:
        existing_reaction = Reaction.query.filter_by(userId=user_id, productId=offer.productId).first()
    else:
        existing_reaction = Reaction.query.filter_by(userId=user_id, offerId=offer_id).first()

    if existing_reaction:
        existing_reaction.reactionType = reaction_type
        db.session.flush()
        return existing_reaction

    reaction = Reaction(
        reactionType=reaction_type,
        userId=user_id,
        offerId=offer_id if not offer.productId else None,
        productId=offer.productId,
    )
    db.session.add(reaction)
    db.session.flush()

    return reaction


SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE = [SEANCE_CINE.id]


def get_booking_with_available_reactions(user_id: int) -> list[Booking]:
    cooldown_datetime = datetime.datetime.utcnow() - datetime.timedelta(
        seconds=settings.SUGGEST_REACTION_COOLDOWN_IN_SECONDS
    )

    offer_reaction = aliased(Reaction)
    product_reaction = aliased(Reaction)

    bookings_loaded_query = Booking.query.options(
        joinedload(Booking.stock)
        .joinedload(Stock.offer)
        .load_only(Offer.name)
        .joinedload(Offer.product)
        .joinedload(Product.productMediations)
    ).options(joinedload(Booking.stock).joinedload(Stock.offer).joinedload(Offer.mediations))

    return (
        bookings_loaded_query.filter(
            Booking.userId == user_id, Booking.status == BookingStatus.USED, Booking.dateUsed <= cooldown_datetime
        )
        # Only include available subcategories
        .join(Booking.stock)
        .join(Stock.offer)
        .filter(Offer.subcategoryId.in_(SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE))
        # Exclude bookings with reactions
        .join(offer_reaction, offer_reaction.offerId == Offer.id, isouter=True)
        .join(product_reaction, product_reaction.productId == Offer.productId, isouter=True)
        .filter(offer_reaction.id.is_(None), product_reaction.id.is_(None))
        .order_by(Booking.dateUsed.desc())
    ).all()
