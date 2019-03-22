from models import Offer, Thing, Event
from repository import thing_queries, event_queries
from validation.events import check_user_can_create_activation_event
from validation.url import is_url_safe


def fill_offer_with_new_thing_data(thing_dict: str) -> Offer:
    thing = Thing()
    url = thing_dict.get('url')
    if url:
        is_url_safe(url)
        thing_dict['isNational'] = True
    thing.populateFromDict(thing_dict)
    offer = Offer()
    offer.populateFromDict(thing_dict)
    offer.thing = thing
    return offer


def fill_offer_with_new_event_data(event_dict: dict, user) -> Offer:
    event = Event()
    event.populateFromDict(event_dict)
    check_user_can_create_activation_event(user, event)
    offer = Offer()
    offer.populateFromDict(event_dict)
    offer.event = event
    return offer


def fill_offer_with_existing_thing_data(thing_id: str, offer_data) -> Offer:
    thing = thing_queries.find_by_id(thing_id)
    offer = Offer()
    offer.populateFromDict(offer_data)
    offer.thing = thing
    offer.type = thing.type
    offer.name = thing.name
    offer.description = thing.description
    offer.url = thing.url
    offer.mediaUrls = thing.mediaUrls
    offer.isNational = thing.isNational
    offer.extraData = thing.extraData
    return offer


def fill_offer_with_existing_event_data(event_id: str) -> Offer:
    offer = Offer()
    event = event_queries.find_by_id(event_id)
    offer.event = event
    offer.type = event.type
    offer.name = event.name
    offer.description = event.description
    offer.mediaUrls = event.mediaUrls
    offer.conditions = event.conditions
    offer.ageMin = event.ageMin
    offer.ageMax = event.ageMax
    offer.accessibility = event.accessibility
    offer.durationMinutes = event.durationMinutes
    offer.isNational = event.isNational
    offer.extraData = event.extraData
    return offer
