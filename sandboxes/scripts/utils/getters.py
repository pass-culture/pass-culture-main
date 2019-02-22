from models.event import Event
from models.thing import Thing
from models.offer import Offer
from models.offerer import Offerer

def get_offerer_with_no_physical_venue_with_no_iban(as_dict=True):
    offerers = Offerer.query.all()
    for offerer in offerers:
        if not all([v.isVirtual for v in offerer.managedVenues]):
            continue
        if offerer.iban:
            continue

        # better if it is 93
        if offerer.postalCode[:2] != '93':
            continue

        if as_dict:
            return {
                "address": offerer.address,
                "city": offerer.city,
                "latitude": '48.9281995',
                "longitude": '2.4579903',
                "keywordsString": offerer.name,
                "name": offerer.name,
                "postalCode": offerer.postalCode,
                "siren": offerer.siren,
            }

        return offerer


def get_offerer_with_physical_venue_with_no_iban(as_dict=True):
    offerers = Offerer.query.all()
    for offerer in offerers:
        if all([v.isVirtual for v in offerer.managedVenues]):
            continue
        if offerer.iban:
            continue

        # better if it is 93
        if offerer.postalCode[:2] != '93':
            continue

        if as_dict:
            return {
                "address": offerer.address,
                "city": offerer.city,
                "keywordsString": offerer.name,
                "name": offerer.name,
                "postalCode": offerer.postalCode,
                "siren": offerer.siren,
            }

        return offerer


def get_offerer_with_physical_venue_with_iban(as_dict=True):
    offerers = Offerer.query.all()
    for offerer in offerers:
        if all([v.isVirtual for v in offerer.managedVenues]):
            continue
        if not offerer.iban:
            continue

        # better if it is 93
        if offerer.postalCode[:2] != '93':
            continue

        if as_dict:
            return {
                "address": offerer.address,
                "city": offerer.city,
                "keywordsString": offerer.name,
                "name": offerer.name,
                "postalCode": offerer.postalCode,
                "siren": offerer.siren,
            }

        return offerer

def get_event_offer_with_no_event_occurrence_with_no_stock_with_no_mediation_with_offerer_iban_with_no_veune_iban(as_dict=True):
    offers = Offer.query.all()
    for offer in offers:
        if not isinstance(offer.eventOrThing, Event):
            continue
        if offer.event.type == 'EventType.ACTIVATION':
            continue
        if offer.eventOccurrences:
            continue
        if offer.stocks:
            continue
        if offer.mediations:
            continue
        if offer.venue.managingOfferer.iban:
            continue
        if offer.venue.iban:
            continue

        # better if it is 93
        if offer.venue.postalCode[:2] != '93':
            continue

        if as_dict:
            return {
                "eventName": offer.eventOrThing.name,
                "venueCity": offer.venue.city,
                "venueName": offer.venue.name
            }
        return offer

def get_event_offer_with_event_occurrence_with_stock_with_mediation_with_offerer_iban_with_no_iban(as_dict=True):
    offers = Offer.query.all()
    for offer in offers:
        if not isinstance(offer.eventOrThing, Event):
            continue
        if offer.event.type == 'EventType.ACTIVATION':
            continue
        if not offer.eventOccurrences:
            continue
        if not offer.stocks:
            continue
        if not offer.mediations:
            continue
        if not offer.venue.managingOfferer.iban:
            continue
        if offer.venue.iban:
            continue

        # better if it is 93
        if offer.venue.postalCode[:2] != '93':
            continue

        if as_dict:
            return {
                "eventName": offer.eventOrThing.name,
                "venueCity": offer.venue.city,
                "venueName": offer.venue.name,
            }
        return offer

def get_event_offer_with_event_occurrence_with_stock_with_mediation_with_no_offerer_iban_with_no_iban(as_dict=True):
    offers = Offer.query.all()
    for offer in offers:
        if not isinstance(offer.eventOrThing, Event):
            continue
        if offer.event.type == 'EventType.ACTIVATION':
            continue
        if not offer.eventOccurrences:
            continue
        if not offer.stocks:
            continue
        if not offer.mediations:
            continue
        if offer.venue.managingOfferer.iban:
            continue
        if offer.venue.iban:
            continue

        # better if it is 93
        if offer.venue.postalCode[:2] != '93':
            continue

        if as_dict:
            return {
                "eventName": offer.eventOrThing.name,
                "venueCity": offer.venue.city,
                "venueName": offer.venue.name
            }
        return offer

def get_virtual_thing_offer_with_no_stock_with_no_mediation_with_no_offerer_iban_with_no_venue_iban(as_dict=True):
    offers = Offer.query.all()
    for offer in offers:
        if not isinstance(offer.eventOrThing, Thing):
            continue
        if not offer.venue.isVirtual:
            continue
        if offer.stocks:
            continue
        if offer.mediations:
            continue
        if offer.venue.managingOfferer.iban:
            continue
        if offer.venue.iban:
            continue

        if as_dict:
            return {
                "venueCity": offer.venue.city,
                "venueName": offer.venue.name,
                "thingName": offer.eventOrThing.name
            }
        return offer

def get_thing_offer_with_stock_with_mediation_with_offerer_iban_with_no_venue_iban(as_dict=True):
    offers = Offer.query.all()
    for offer in offers:
        if not isinstance(offer.eventOrThing, Thing):
            continue
        if not offer.stocks:
            continue
        if not offer.mediations:
            continue
        if not offer.venue.managingOfferer.iban:
            continue
        if offer.venue.iban:
            continue

        # better if it is 93
        if offer.venue.postalCode[:2] != '93':
            continue

        if as_dict:
            return {
                "venueCity": offer.venue.city,
                "venueName": offer.venue.name,
                "thingName": offer.eventOrThing.name
            }
        return offer
