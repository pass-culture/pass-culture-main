import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import models as bookings_models
from pcapi.core.offers import models as offers_models
from pcapi.core.reactions import exceptions as reactions_exceptions
from pcapi.core.reactions import models as reactions_models
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.routes.native.v1.serialization.reaction import PostOneReactionRequest


def bulk_update_or_create_reaction(user: User, reactions: list[PostOneReactionRequest]) -> None:
    offer_ids = {reaction.offer_id for reaction in reactions}

    bookings = (
        db.session.query(bookings_models.Booking)
        .join(bookings_models.Booking.stock)
        .filter(
            bookings_models.Booking.userId == user.id,
            sa.not_(bookings_models.Booking.isCancelled),
            offers_models.Stock.offerId.in_(offer_ids),
        )
        .options(
            sa_orm.contains_eager(bookings_models.Booking.stock)
            .joinedload(offers_models.Stock.offer, innerjoin=True)
            .load_only(offers_models.Offer.id, offers_models.Offer.subcategoryId, offers_models.Offer.productId)
        )
    )

    bookings_by_offer_id = {booking.stock.offerId: booking for booking in bookings}

    for reaction in reactions:
        if not (booking := bookings_by_offer_id.get(reaction.offer_id)):
            raise reactions_exceptions.OfferNotBooked()
        if not booking.can_react:
            raise reactions_exceptions.CanNotReact()
        update_or_create_reaction(user, booking.stock.offer, reaction.reaction_type)
    db.session.flush()


def update_or_create_reaction(
    user: User,
    offer: offers_models.Offer,
    reaction_type: reactions_models.ReactionTypeEnum,
) -> reactions_models.Reaction:
    if offer.productId:
        existing_reaction = next(
            (reaction for reaction in user.reactions if reaction.productId == offer.productId), None
        )
    else:
        existing_reaction = next((reaction for reaction in user.reactions if reaction.offerId == offer.id), None)

    if existing_reaction:
        existing_reaction.reactionType = reaction_type
        db.session.flush()
        return existing_reaction

    reaction = reactions_models.Reaction(
        reactionType=reaction_type,
        userId=user.id,
        offerId=offer.id if not offer.productId else None,
        productId=offer.productId,
    )
    db.session.add(reaction)

    return reaction


def get_bookings_with_available_reactions(user_id: int) -> list[bookings_models.Booking]:
    bookings_loaded_query = db.session.query(bookings_models.Booking).options(
        sa_orm.joinedload(bookings_models.Booking.stock)
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
        sa_orm.joinedload(bookings_models.Booking.user).joinedload(User.reactions),
    )

    bookings: list[bookings_models.Booking] = (
        bookings_loaded_query.filter(
            bookings_models.Booking.userId == user_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.USED,
        ).order_by(bookings_models.Booking.dateUsed.desc())
    ).all()

    return [booking for booking in bookings if booking.enable_pop_up_reaction]
