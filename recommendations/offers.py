""" recommendations offers """
from flask import current_app as app
from math import sqrt
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
def get_event_mediation_query(source_ids):
    def inner(query):
        return query.outerjoin(EventOccurence)\
                    .filter(~EventOccurence.eventId.in_(source_ids))\
                    .outerjoin(Event)\
                    .filter((Event.mediations.any(mediation_filter)))
    return inner

def get_thing_mediation_query(source_ids):
    def inner(query):
        return query.outerjoin(Thing)\
                    .filter(~Thing.id.in_(source_ids))\
                    .filter((Thing.mediations.any(mediation_filter)))
    return inner


def distance(latitude1, longitude1, latitude2, longitude2):
    return sqrt(((float(latitude2) - float(latitude1)) ** 2) +
                ((float(longitude2) - float(longitude1)) ** 2))

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
def get_event_deduplication_query(query):
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

    # COMPOSE EVENTS
    # ... FROM MONTPELLIER

    LAT = 43.608495
    LONG = 3.893408
    event_mediation_query = compose(
        get_distance_query(LAT, LONG),
        get_event_deduplication_query,
        get_event_mediation_query(source_ids)
    )(user_query)
    event_mediation_query_count = event_mediation_query.count()
    print('(reco) event_mediation count', event_mediation_query_count)

    # LIMIT
    event_mediation_offers = [t[0] for t in event_mediation_query.limit(limit)]
    event_mediation_offer_ids = [offer.id for offer in event_mediation_offers]

    # COMPOSE THINGS
    # ... FROM MONTPELLIER
    thing_mediation_query = compose(
        get_distance_query(LAT, LONG),
        get_thing_mediation_query(source_ids)
    )(user_query)
    thing_mediation_query_count = thing_mediation_query.count()
    print('(reco) thing_mediation count', thing_mediation_query_count)

    # LIMIT
    thing_mediation_offers = [t for t in thing_mediation_query.limit(limit)]
    thing_mediation_offer_ids = [offer.id for offer in thing_mediation_offers]


    # PREPARE FINAL OFFERS
    final_offers = event_mediation_offers + thing_mediation_offers

    # MAYBE FEED WITH SOME COMPLEMENTARY PURE OFFERS
    """
    if mediation_query_count < limit:
        pure_query = list(
            compose(
                get_distance_query(LAT, LONG),
                get_event_deduplication_query,
                lambda query: query.outerjoin(Thing)\
                                   .outerjoin(EventOccurence)\
                                   .outerjoin(Event)\
                                   .filter((Thing.thumbCount > 0) |\
                                            (Event.thumbCount > 0))\
            )(user_query.filter(~Offer.id.in_(mediation_offer_ids)))
        ).limit(limit - mediation_query_count))
        print('(reco) pure offers count', len(pure_query))
        final_offers += [t[0] for t in pure_query]
    """

    # RETURN
    print('(reco) final count', len(final_offers))
    return sorted(final_offers, key=lambda o: distance(o.offerer.venue.latitude, o.offerer.venue.longitude, LAT, LONG))

app.recommendations.get_offers = get_offers
