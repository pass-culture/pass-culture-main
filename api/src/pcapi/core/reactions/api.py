from sqlalchemy.orm import joinedload

from pcapi.core.bookings import models as bookings_models
from pcapi.core.offers import models as offers_models
from pcapi.core.reactions import models as reactions_models
from pcapi.core.reactions import schemas as reactions_schemas
from pcapi.core.users.models import User
from pcapi.models import db


def bulk_update_or_create_reaction(user: User, reactions: list[reactions_schemas.PostOneReactionRequest]) -> None:
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


def get_bookings_with_available_reactions(user_id: int) -> list[bookings_models.Booking]:

    bookings_loaded_query = bookings_models.Booking.query.options(
        joinedload(bookings_models.Booking.stock)
        .load_only(
            offers_models.Stock.id,
        )
        .joinedload(offers_models.Stock.offer)
        .load_only(
            offers_models.Offer.id,
            offers_models.Offer.productId,
            offers_models.Offer.subcategoryId,
            offers_models.Offer.name,
        )
        .joinedload(offers_models.Offer.mediations),
        joinedload(bookings_models.Booking.user).joinedload(User.reactions),
    )

    bookings: list[bookings_models.Booking] = (
        bookings_loaded_query.filter(
            bookings_models.Booking.userId == user_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.USED,
        ).order_by(bookings_models.Booking.dateUsed.desc())
    ).all()

    return [booking for booking in bookings if booking.enable_pop_up_reaction]
