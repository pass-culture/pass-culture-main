""" recommendations offers """
from flask import current_app as app
from sqlalchemy import desc
from sqlalchemy.sql.expression import func

from utils.human_ids import dehumanize
from utils.compose import compose
from utils.content import get_mediation, get_source
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

# FILTER OFFERS WITH THUMBED MEDIATION
mediation_filter = Mediation.thumbCount != None
def get_mediation_query(source_ids):
    def inner(query):
        return query.outerjoin(EventOccurence)\
                    .filter(~EventOccurence.eventId.in_(source_ids))\
                    .outerjoin(Event)\
                    .outerjoin(Thing)\
                    .filter(
                        (Event.mediations.any(mediation_filter)) |\
                        (Thing.mediations.any(mediation_filter))
                    )
    return inner

# FILTER OFFERS THAT ARE THE CLOSEST
def get_distance_query(latitude, longitude):
    distance_order_by = func.sqrt(
        func.pow(Venue.latitude - latitude, 2) +
        func.pow(Venue.longitude - longitude, 2)
    )
    def inner(query):
        return query.join(Offerer)\
                    .join(Venue)\
                    .order_by(distance_order_by)
    return inner


# FILTER OFFER WITH ONE OFFER PER EVENT
# THE ONE THAT IS WITH THE SOONER EVENT OCCURENCE
row_number_column = func.row_number()\
                        .over(partition_by=Event.id,
                              order_by=desc(EventOccurence.beginningDatetime))\
                        .label('row_number')
def get_deduplication_query(query):
    return query.add_column(row_number_column)\
                .from_self()\
                .filter(row_number_column == 1)

def get_offers(user, limit=3):
    # CHECK USER
    if not user.is_authenticated():
        return []

    # ALL
    all_query = Offer.query
    print('(reco) all offers.count', all_query.count())

    # REMOVE OFFERS FOR WHICH THERE IS ALREADY A RECOMMENDATION FOR THIS USER
    user_mediations = UserMediation.query\
                                   .filter(UserMediation.userId == user.id)\
                                   .all()
    user_mediation_ids = [um.id for um in user_mediations]
    user_mediations = [
        um._asdict(include=USER_MEDIATIONS_INCLUDES)
        for um in user_mediations
    ]
    source_ids = [
        dehumanize(get_source(get_mediation(um), um['userMediationOffers'][0])['id'])
        for um in user_mediations if len(um['userMediationOffers'])
    ]
    user_query = all_query.filter(
        ~Offer.userMediationOffers.any() |\
        ~Offer.userMediationOffers.any(
            UserMediationOffer.userMediationId.in_(user_mediation_ids)
        )
    )
    print('(reco) not already used offers.count', user_query.count())

    # COMPOSE
    # ... FROM MONTPELLIER
    mediation_query = compose(
        get_distance_query(43.608495, 3.893408),
        get_deduplication_query,
        get_mediation_query(source_ids)
    )(user_query)
    mediation_query_count = mediation_query.count()
    print('(reco) mediation count', mediation_query_count)

    # LIMIT
    mediation_offers = [t[0] for t in mediation_query.limit(limit)]
    mediation_offer_ids = [offer.id for offer in mediation_offers]

    # PREPARE FINAL OFFERS
    final_offers = mediation_offers

    # MAYBE FEED WITH SOME COMPLEMENTARY PURE OFFERS
    """
    if mediation_query_count < limit:
        pure_query = list(
            user_query.filter(~Offer.id.in_(mediation_offer_ids))\
                      .join(Offerer)\
                      .join(Venue)\
                      .order_by(distance_order_by)\
                      .outerjoin(Thing)\
                      .outerjoin(EventOccurence)\
                      .outerjoin(Event)\
                      .filter((Thing.thumbCount > 0) |\
                              (Event.thumbCount > 0))\
                      .add_column(row_number_column)\
                      .from_self()\
                      .filter(row_number_column == 1)
                      .limit(limit - mediation_query_count))
        print('(reco) pure offers count', len(pure_query))
        final_offers += [t[0] for t in pure_query]
    """

    # RETURN
    print('(reco) final count', len(final_offers))
    return final_offers

app.recommendations.get_offers = get_offers
