import datetime

from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories.subcategories_v2 import SEANCE_CINE
from pcapi.core.offers import models as offers_models
from pcapi.core.reactions import models as reactions_models
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.routes.native.v1.serialization.reaction import PostOneReactionRequest


def bulk_update_or_create_reaction(user: User, reactions: list[PostOneReactionRequest]) -> None:
    for reaction in reactions:
        update_or_create_reaction(user, reaction.offer_id, reaction.reaction_type)
    db.session.flush()


def update_or_create_reaction(
    user: User,
    offer_id: int,
    reaction_type: reactions_models.ReactionTypeEnum,
) -> reactions_models.Reaction:
    offer = offers_models.Offer.query.get_or_404(offer_id)
    if offer.productId:
        existing_reaction = next(
            (reaction for reaction in user.reactions if reaction.productId == offer.productId), None
        )
    else:
        existing_reaction = next((reaction for reaction in user.reactions if reaction.offerId == offer_id), None)

    if existing_reaction:
        existing_reaction.reactionType = reaction_type
        db.session.flush()
        return existing_reaction

    reaction = reactions_models.Reaction(
        reactionType=reaction_type,
        userId=user.id,
        offerId=offer_id if not offer.productId else None,
        productId=offer.productId,
    )
    db.session.add(reaction)

    return reaction


SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE = [SEANCE_CINE.id]


def get_booking_with_available_reactions(user_id: int) -> list[bookings_models.Booking]:
    cooldown_datetime = datetime.datetime.now() - datetime.timedelta(
        seconds=settings.SUGGEST_REACTION_COOLDOWN_IN_SECONDS
    )

    offer_reaction = aliased(reactions_models.Reaction)
    product_reaction = aliased(reactions_models.Reaction)

    bookings_loaded_query = bookings_models.Booking.query.options(
        joinedload(bookings_models.Booking.stock)
        .joinedload(offers_models.Stock.offer)
        .load_only(offers_models.Offer.name)
        .joinedload(offers_models.Offer.product)
        .joinedload(offers_models.Product.productMediations)
    ).options(
        joinedload(bookings_models.Booking.stock)
        .joinedload(offers_models.Stock.offer)
        .joinedload(offers_models.Offer.mediations)
    )

    return (
        bookings_loaded_query.filter(
            bookings_models.Booking.userId == user_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.USED,
            bookings_models.Booking.dateUsed <= cooldown_datetime,
        )
        # Only include available subcategories
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .filter(offers_models.Offer.subcategoryId.in_(SUBCATEGORY_IDS_WITH_REACTION_AVAILABLE))
        # Exclude bookings with reactions
        .join(offer_reaction, offer_reaction.offerId == offers_models.Offer.id, isouter=True)
        .join(product_reaction, product_reaction.productId == offers_models.Offer.productId, isouter=True)
        .filter(offer_reaction.id.is_(None), product_reaction.id.is_(None))
        .order_by(bookings_models.Booking.dateUsed.desc())
    ).all()
