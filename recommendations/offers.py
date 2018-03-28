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

    # DO THE JOINS (DO NOT MAKE CONFUSION WITH JOHN KERRY)
    join_query = user_query.outerjoin(Thing)\
                 .outerjoin(EventOccurence)\
                 .outerjoin(Event)

    # CHOOSE OFFER FOR WHICH WE HAVE MEDIATION
    # TODO WE NEED TO KEEP ONLY ONE BY MEDIATION
    is_mediation = (Mediation.frontText != None) | (Mediation.thumbCount > 0)
    mediation_query = join_query.filter(# (Thing.mediations.any(is_mediation)) |
                                       (Event.mediations.any(is_mediation)))
    mediation_query_count = mediation_query.count()
    print('(reco) mediated offers.count', mediation_query_count)
    mediation_offers = list(mediation_query.order_by(func.random())\
                                           .limit(limit))
    mediation_offer_ids = [m.id for m in mediation_offers]

    # PREPARE FINAL OFFERS
    final_offers = mediation_offers

    # MAYBE FEED WITH SOME COMPLEMENTARY PURE OFFERS
    if mediation_query_count < limit:
        print('(reco) default')
        default_offers = list(join_query.filter(
            (~Offer.id.in_(mediation_offer_ids)) &
            # (Thing.thumbCount > 0) |
            (Event.thumbCount > 0))
        .order_by(func.random())\
        .limit(limit - mediation_query_count))
        final_offers += default_offers

    # RETURN
    print('(reco) final count', len(final_offers))
    return final_offers

app.recommendations.get_offers = get_offers
