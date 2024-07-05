from pcapi.core.offers.models import Offer
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
