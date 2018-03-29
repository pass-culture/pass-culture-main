from random import randint

def get_mediation (user_mediation):
    return user_mediation.get('mediation')

def get_offer (offer_id, user_mediation):
    return [o for o in user_mediation.get('userMediationOffers', []) if o['id'] == offer_id][0]

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
    return '/static/images/default_thumb.png'

def get_venue(offer, source):
    return offer.get('eventOccurence', {'venue': None}).get('venue') or\
    offer.get('venue') or\
    source.get('eventOccurence', {'venue': None}).get('venue') or\
    source.get('venue')

def get_content(user_mediation):
    content = {}
    mediation = user_mediation.get('mediation')
    user_mediation_offers = user_mediation['userMediationOffers']
    offer_index = randint(0, len(user_mediation_offers) - 1)
    offer_id = user_mediation_offers[offer_index]['id']
    mediation = get_mediation(user_mediation)
    offer = get_offer(offer_id, user_mediation)
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
