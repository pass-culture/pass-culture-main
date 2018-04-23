from random import randint

def get_mediation (recommendation):
    return recommendation.get('mediation')

def get_offer (offer_id, recommendation):
    return [o for o in recommendation.get('recommendationOffers', []) if o['id'] == offer_id][0]

def get_source(mediation, offer):
    return offer.get('eventOccurence', {"event": None}).get('event') or\
           offer.get('thing') or\
           mediation.get('event') or\
           mediation.get('thing')

def get_thumb_url(mediation, source, offer):
    source_collection_name = (offer.get('eventOccurence') and 'events') or\
        (offer.get('thing') and 'things') or\
        (mediation.get('event') and 'events') or\
        (mediation.get('thing') and 'things') or ''
    if mediation and mediation.get('thumbCount') > 0:
        return '/mediations/'+ mediation['id']
    elif source and source.get('thumbCount') > 0:
        return source_collection_name + '/' + source['id']

def get_venue(offer, source):
    return offer.get('eventOccurence', {'venue': None}).get('venue') or\
    offer.get('venue') or\
    source.get('eventOccurence', {'venue': None}).get('venue') or\
    source.get('venue')

def get_content(recommendation):
    content = {}
    mediation = recommendation.get('mediation')
    recommendation_offers = recommendation['recommendationOffers']
    offer_index = randint(0, len(recommendation_offers) - 1)
    offer_id = recommendation_offers[offer_index]['id']
    mediation = get_mediation(recommendation)
    offer = get_offer(offer_id, recommendation)
    source = get_source(mediation, offer)
    venue = get_venue(offer, source)
    content['thumbUrl'] = get_thumb_url(mediation, source, offer)
    content.update({
        "offer": offer,
        "mediation": mediation,
        "source": source,
        "venue": venue
    })
    return content
