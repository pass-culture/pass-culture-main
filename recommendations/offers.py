""" recommendations offers """
from flask import current_app as app
from sqlalchemy.sql.expression import func

from utils.human_ids import dehumanize
from utils.content import get_mediation, get_offer, get_source
from utils.includes import USER_MEDIATIONS_INCLUDES

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer
Offerer = app.model.Offerer
UserMediation = app.model.UserMediation
UserMediationOffer = app.model.UserMediationOffer
Thing = app.model.Thing
Venue = app.model.Venue


def get_offers(user, limit=3):
    # CHECK USER
    if not user.is_authenticated():
        return []

    # ALL
    all_query = Offer.query
    print('(reco) all offers.count', all_query.count())

    # REMOVE OFFERS FOR WHICH THERE IS ALREADY A RECOMMENDATION FOR THIS USER
    # WE JUST KEEP ONE OFFER PER EVENT
    # THE ONE THAT IS WITH THE SOONER EVENT OCCURENCE
    user_mediations = UserMediation.query\
                                   .filter(UserMediation.userId == user.id)\
                                   .all()
    user_mediation_ids = [um.id for um in user_mediations]
    user_mediations = [um._asdict(include=USER_MEDIATIONS_INCLUDES) for um in user_mediations]
    source_ids = [dehumanize(get_source(get_mediation(um), um['userMediationOffers'][0])['id']) for um in user_mediations if len(um['userMediationOffers'])]
    user_query = all_query.filter(~Offer.userMediationOffers.any() |\
                                  ~Offer.userMediationOffers.any(
                                      UserMediationOffer.userMediationId.in_(user_mediation_ids)
                                  ))
    print('(reco) not already used offers.count', user_query.count())

    # CHOOSE OFFER FOR WHICH WE HAVE MEDIATION
    is_mediation = Mediation.thumbCount != None
    mediation_query = user_query.outerjoin(EventOccurence)\
                                .distinct(EventOccurence.eventId)\
                                .order_by(EventOccurence.eventId,
                                          EventOccurence.beginningDatetime)\
                                .filter(
                                    ~EventOccurence.eventId.in_(source_ids))\
                                .outerjoin(Event)\
                                .outerjoin(Thing)\
                                .filter(
                                    (Event.mediations.any(is_mediation)) |\
                                    (Thing.mediations.any(is_mediation))
                                )
    mediation_query_count = mediation_query.count()
    print('(reco) mediation count', mediation_query_count)
                                
    mediation_offers = list(mediation_query.join(Offerer)
                                           .join(Venue)
                                           .order_by(func.sqrt(func.pow(Venue.latitude - 43.608495, 2) +
                                                               func.pow(Venue.longitude - 3.893408, 2)))
                                           .limit(limit))
    mediation_offer_ids = [offer.id for offer in mediation_offers]

    # PREPARE FINAL OFFERS
    final_offers = mediation_offers

    # MAYBE FEED WITH SOME COMPLEMENTARY PURE OFFERS
    if mediation_query_count < limit:
        pure_offers = list(
            user_query.filter(~Offer.id.in_(mediation_offer_ids))\
                      .outerjoin(Thing)\
                      .outerjoin(EventOccurence)\
                      .distinct(EventOccurence.eventId)\
                      .order_by(EventOccurence.eventId, EventOccurence.beginningDatetime)\
                      .outerjoin(Event)\
                      .filter((Thing.thumbCount > 0) |\
                              (Event.thumbCount > 0))\
                      .order_by(func.random())\
                      .limit(limit - mediation_query_count))
        print('(reco) pure offers count', len(pure_offers))
        final_offers += pure_offers
    # RETURN
    print('(reco) final count', len(final_offers))
    return final_offers

app.recommendations.get_offers = get_offers
