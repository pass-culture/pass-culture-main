from flask import current_app as app
from flask_login import current_user
from sqlalchemy.sql.expression import func

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer
UserMediation = app.model.UserMediation
UserMediationOffer = app.model.UserMediationOffer
Thing = app.model.Thing


def get_recommended_offers(user, limit=3):
    query = Offer.query
    # REMOVE OFFERS FOR WHICH THERE IS ALREADY A MEDIATION FOR THIS USER
    print('before userMediation offers.count', query.count())
    if user.is_authenticated:
        query = query.filter(
            ~Offer.userMediationOffers.any() |\
            Offer.userMediationOffers.any(UserMediation.user != user)
        )

    # REMOVE OFFERS WITHOUT THUMBS
    print('after userMediation offers.count', query.count())
    query = query.outerjoin(Thing)\
                 .outerjoin(EventOccurence)\
                 .outerjoin(Event)\
                 .filter((Thing.thumbCount > 0) |
                         (Event.thumbCount > 0))

    # RETURN
    print('after thumbs offers.count', query.count())
    return query.order_by(func.random())\
                .limit(limit)

app.reco.offers = get_recommended_offers
