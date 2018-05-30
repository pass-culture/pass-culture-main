""" recommendations offers """
from flask import current_app as app

from datascience.hoqs import with_event_deduplication, with_distance,\
    with_event, with_event_mediation, with_thing, with_thing_mediation
from utils.human_ids import dehumanize
from utils.compose import compose
from utils.content import get_mediation, get_source
from utils.distance import distance
from utils.includes import RECOMMENDATIONS_INCLUDES

Offer = app.model.Offer
Recommendation = app.model.Recommendation
RecommendationOffer = app.model.RecommendationOffer

def get_offers(limit=3, user=None, coords=None):
    # CHECK USER
    if not user or not user.is_authenticated():
        return []

    # POSITION (MONTPELLIER BY DEFAULT...)
    LAT = 43.608495
    LONG = 3.893408
    if coords and coords.get('latitude'):
        LAT = float(coords.get('latitude'))
    if coords and coords.get('longitude'):
        LONG = float(coords.get('longitude'))

    # ALL
    all_query = Offer.query
    print('(reco) all offers.count', all_query.count())

    # REMOVE OFFERS FOR WHICH THERE IS ALREADY A RECOMMENDATION FOR THIS USER
    recommendations = Recommendation.query\
                                   .filter(Recommendation.userId == user.id)\
                                   .all()
    recommendation_ids = [recommendation.id for recommendation in recommendations]
    recommendations = [
        recommendation._asdict(include=RECOMMENDATIONS_INCLUDES)
        for recommendation in recommendations
    ]
    source_ids = [
        dehumanize(
            get_source(
                get_mediation(recommendation),
                recommendation['recommendationOffers'][0]
            )['id']
        )
        for recommendation in recommendations if len(recommendation['recommendationOffers'])
    ]
    user_query = all_query.filter(
        ~Offer.recommendationOffers.any() |\
        ~Offer.recommendationOffers.any(
            RecommendationOffer.recommendationId.in_(recommendation_ids)
        )
    )
    print('(reco) not already used offers.count', user_query.count())

    # COMPOSE EVENTS
    # ... FROM MONTPELLIER
    event_mediation_query = compose(
        LAT and LONG and with_distance(LAT, LONG),
        with_event_deduplication,
        with_event_mediation(source_ids)
    )(user_query)
    event_mediation_query_count = event_mediation_query.count()
    print('(reco) event_mediation count', event_mediation_query_count)

    # LIMIT
    event_mediation_offers = [t[0] for t in event_mediation_query.limit(limit)]

    # COMPOSE THINGS
    thing_mediation_query = compose(
        LAT and LONG and with_distance(LAT, LONG),
        with_thing_mediation(source_ids)
    )(user_query)
    thing_mediation_query_count = thing_mediation_query.count()
    print('(reco) thing_mediation count', thing_mediation_query_count)

    # LIMIT
    thing_mediation_offers = [o for o in thing_mediation_query.limit(limit)]


    # PREPARE FINAL OFFERS
    final_offers = event_mediation_offers + thing_mediation_offers
    final_count = len(final_offers)

    # MAYBE FEED WITH SOME COMPLEMENTARY PURE OFFERS
    if final_count < limit:
        """
        event_mediation_offer_ids = [offer.id for offer in event_mediation_offers]
        thing_mediation_offer_ids = [offer.id for offer in thing_mediation_offers]
        available_pure_query = with_distance(LAT, LONG)(
            user_query.filter(~Offer.id.in_(mediation_offer_ids))
        )
        pure_event_query = compose(
            with_event_deduplication,
            with_event
        )(available_pure_query)
        pure_event_offers = [t[0] for t in pure_event_query.limit(limit - mediation_query_count)]
        print('(reco) pure event offers count', len(pure_event_offers))
        pure_thing_query = with_thing(available_pure_query)
        pure_thing_offers = [o for o in pure_thing_query.limit(limit - mediation_query_count)]
        print('(reco) pure thing offers count', len(pure_thing_offers))
        pure_offers = pure_event_offers + pure_thing_offers
        final_offers += pure_offers
        """
        pass

    # RETURN
    print('(reco) final count', len(final_offers))
    if LAT and LONG:
        final_offers = sorted(
            final_offers,
            key=lambda o: distance(
                o.offerer.venue.latitude,
                o.offerer.venue.longitude,
                LAT,
                LONG
            )
        )
    return final_offers

app.datascience.get_offers = get_offers
