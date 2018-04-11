""" recommendations offers """
from flask import current_app as app
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

    # REMOVE OFFERS FOR WHICH THERE IS ALREADY A RECOMMENDATION FOR THIS USER
    if user.is_authenticated:
        user_mediations = UserMediation.query.filter(UserMediation.user == user).all()
        user_mediation_ids = [um.id for um in user_mediations]
        user_query = all_query.filter(
            ~Offer.userMediationOffers.any() |\
            ~Offer.userMediationOffers.any(
                UserMediationOffer.userMediationId.in_(user_mediation_ids)
            )
        )
    print('(reco) not already used offers.count', user_query.count())

    # CHOOSE OFFER FOR WHICH WE HAVE MEDIATION
    # WE JUST KEEP ONE OFFER PER EVENT
    # THE ONE THAT IS WITH THE SOONER EVENT OCCURENCE
    is_mediation = Mediation.thumbCount != None
    mediation_query = user_query.outerjoin(Thing)\
                                .outerjoin(EventOccurence)\
                                .distinct(EventOccurence.eventId)\
                                .order_by(EventOccurence.eventId,
                                          EventOccurence.beginningDatetime)\
                                .outerjoin(Event)\
                                .filter((Thing.mediations.any(is_mediation)) |
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
        pure_offers = list(
            user_query.outerjoin(Thing)\
                      .outerjoin(EventOccurence)\
                      .distinct(EventOccurence.eventId)\
                      .order_by(EventOccurence.eventId, EventOccurence.beginningDatetime)\
                      .outerjoin(Event)\
                      .filter((~Offer.id.in_(mediation_offer_ids)) &
                              (Thing.thumbCount > 0) |
                              (Event.thumbCount > 0))\
                      .order_by(func.random())\
                      .limit(limit - mediation_query_count))
        print('(reco) pure offers count', len(pure_offers))
        final_offers += pure_offers
    # RETURN
    print('(reco) final count', len(final_offers))
    print('(reco) ids ', [final_offer._asdict()['id'] for final_offer in final_offers])
    return final_offers

app.recommendations.get_offers = get_offers
