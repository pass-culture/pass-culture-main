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


def get_offers(user, limit=3):
    all_query = Offer.query
    print('(reco) all offers.count', all_query.count())

    # REMOVE OFFERS FOR WHICH THERE IS ALREADY A MEDIATION FOR THIS USER
    if user.is_authenticated:
        user_query = all_query.filter(
            ~Offer.userMediationOffers.any() |\
            Offer.userMediationOffers.any(UserMediation.user != user)
        )
    print('(reco) not already used offers.count', user_query.count())

    # CHOOSE OFFER FOR WHICH WE HAVE MEDIATION
    mediation_query = user_query.outerjoin(Thing)\
                 .outerjoin(EventOccurence)\
                 .outerjoin(Event)\
                 .filter(# (Thing.mediations.any(Mediation.thumbCount > 0)) |
                         (Event.mediations.any(Mediation.thumbCount > 0)))
    mediation_query_count = mediation_query.count()
    print('(reco) mediated offers.count', mediation_query.count())

    # MAYBE FEED WITH SOME COMPLEMENTARY PURE OFFERS
    final_query = mediation_query
    if mediation_query_count < limit:
        final_query = mediation_query.filter(# (Thing.thumbCount > 0) |
                                            (Event.thumbCount > 0))

    # RETURN
    print('(reco) final count', final_query.count())
    return final_query.order_by(func.random())\
                .limit(limit)

app.recommendations.get_offers = get_offers
