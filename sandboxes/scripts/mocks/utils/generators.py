""" generators """
import numpy
import requests

from domain.types import get_format_types, get_types_by_value
from sandboxes.scripts.mocks.utils.params import EVENT_OR_THING_MOCK_NAMES, \
                                                 EVENT_OCCURRENCE_BEGINNING_DATETIMES, \
                                                 PLACES
from utils.human_ids import humanize

def get_all_offerer_mocks(geo_interval=0.1, geo_number=2):

    dehumanized_id = 10000
    siren = 999999999

    offerer_mocks = []
    for place in PLACES:
        longitudes = numpy.linspace(
            place['longitude'] - geo_interval,
            place['longitude'] + geo_interval,
            geo_number
        )
        for longitude in longitudes :
            latitudes = numpy.linspace(
                place['latitude'] - geo_interval,
                place['latitude'] + geo_interval,
                geo_number
            )
            for latitude in latitudes:
                url = 'https://api-adresse.data.gouv.fr/reverse/?lon='+str(longitude)+'&lat='+str(latitude)
                result = requests.get(url)
                obj = result.json()
                if 'features' in obj and obj['features']:
                    feature = obj['features'][0]
                    coordinates = feature['geometry']['coordinates']
                    properties = feature['properties']
                    offerer_mock = {
                        "address": properties['name'].upper(),
                        "city": properties['city'],
                        "id": humanize(dehumanized_id),
                        "latitude": coordinates[1],
                        "longitude": coordinates[0],
                        "name": "STRUCTURE " + str(siren),
                        "postalCode": properties['postcode'],
                        "siren": str(siren)
                    }

                    dehumanized_id += 1
                    siren = siren - 1

                    offerer_mocks.append(offerer_mock)

    return offerer_mocks

def get_all_venue_mocks(all_offerer_mocks):

    dehumanized_id = 10000

    venue_mocks = []
    for offerer_mock in all_offerer_mocks:
        venue_mock = {
            "address": offerer_mock['address'],
            "bookingEmail": "fake@email.com",
            "city": offerer_mock['city'],
            "comment": "Pas de siret car je suis un mock.",
            "id": humanize(dehumanized_id),
            "latitude": offerer_mock['latitude'],
            "longitude": offerer_mock['longitude'],
            "name": "LIEU " + str(offerer_mock['siren']),
            "offererId": offerer_mock['id'],
            "postalCode": offerer_mock['postalCode']
        }

        dehumanized_id += 1

        venue_mocks.append(venue_mock)

        virtual_venue_mock = {
            "id": humanize(dehumanized_id),
            "isVirtual": True,
            "name": "Offre en ligne",
            "offererId": offerer_mock['id']
        }

        dehumanized_id += 1

        venue_mocks.append(virtual_venue_mock)

    return venue_mocks

def get_all_typed_event_mocks():

    dehumanized_id = 10000

    event_types = [t for t in get_format_types() if t['type'] == 'Event']

    event_mocks = []
    mock_count = -1
    for event_type in event_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        mock_count += 1
        if mock_count > len(EVENT_OR_THING_MOCK_NAMES) - 1:
            mock_count = 0

        event_mock = {
            "durationMinutes": 60,
            "firstThumbDominantColor": b'\x00\x00\x00',
            "id": humanize(dehumanized_id),
            "name": event_type['value'] + " " + EVENT_OR_THING_MOCK_NAMES[mock_count],
            "type": event_type['value'],
            "thumbCount": 1
        }

        dehumanized_id += 1

        event_mocks.append(event_mock)

    return event_mocks

def get_all_typed_thing_mocks():

    dehumanized_id = 10000

    types_by_value = get_types_by_value()

    thing_types = [t for t in types_by_value.values() if t['type'] == 'Thing']

    thing_mocks = []
    mock_count = -1
    for thing_type in thing_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        mock_count += 1
        if mock_count > len(EVENT_OR_THING_MOCK_NAMES) - 1:
            mock_count = 0

        thing_mock = {
            "firstThumbDominantColor": b'\x00\x00\x00',
            "id": humanize(dehumanized_id),
            "name": thing_type['value'] + " " + EVENT_OR_THING_MOCK_NAMES[mock_count],
            "thumbCount": 1,
            "type": thing_type['value'],
        }

        dehumanized_id += 1

        # DETERMINE THE MATCHING VENUE
        thing_type = types_by_value[thing_mock['type']]
        if thing_type['onlineOnly']:
            thing_mock['isNational'] = True
            thing_mock['url'] = 'https://ilestencoretemps.fr/'

        thing_mocks.append(thing_mock)

    return thing_mocks

def get_all_typed_event_offer_mocks(all_typed_event_mocks, all_venue_mocks):

    dehumanized_id = 10000

    types_by_value = get_types_by_value()

    offer_mocks = []

    for venue_mock in all_venue_mocks:

        if 'isVirtual' in venue_mock and venue_mock['isVirtual']:
            continue

        virtual_venue_mock = [
            vm for vm in all_venue_mocks
            if venue_mock['offererId'] == vm['offererId'] and 'isVirtual' in vm and vm['isVirtual'] == True
        ][0]

        for event_mock in all_typed_event_mocks:

            offer_mock = {
                "eventId": event_mock['id'],
                "id": humanize(dehumanized_id),
                "isActive": True,
            }

            # DETERMINE THE MATCHING VENUE
            event_type = types_by_value[event_mock['type']]
            if event_type['offlineOnly']:
                offer_mock['venueId'] = venue_mock['id']
            elif event_type['onlineOnly']:
                offer_mock['venueId'] = virtual_venue_mock['id']
            else:
                offer_mock['venueId'] = venue_mock['id']

            dehumanized_id += 1

            offer_mocks.append(offer_mock)

    return offer_mocks

def get_all_typed_thing_offer_mocks(all_typed_thing_mocks, all_venue_mocks):

    dehumanized_id = 20000

    types_by_value = get_types_by_value()

    offer_mocks = []

    for venue_mock in all_venue_mocks:

        if 'isVirtual' in venue_mock and venue_mock['isVirtual']:
            continue

        virtual_venue_mock = [
            vm for vm in all_venue_mocks
            if venue_mock['offererId'] == vm['offererId'] and 'isVirtual' in vm and vm['isVirtual'] == True
        ][0]

        for thing_mock in all_typed_thing_mocks:
            offer_mock = {
                "id": humanize(dehumanized_id),
                "isActive": True,
                "thingId": thing_mock['id']
            }

            # DETERMINE THE MATCHING VENUE
            thing_type = types_by_value[thing_mock['type']]
            if thing_type['offlineOnly']:
                offer_mock['venueId'] = venue_mock['id']
            elif thing_type['onlineOnly']:
                offer_mock['venueId'] = virtual_venue_mock['id']
            else:
                offer_mock['venueId'] = venue_mock['id']

            dehumanized_id += 1

            offer_mocks.append(offer_mock)

    return offer_mocks

def get_all_typed_event_occurrence_mocks(all_typed_event_offer_mocks):

    dehumanized_id = 10000

    event_occurrence_mocks = []
    for event_offer_mock in all_typed_event_offer_mocks:
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            event_occurrence_mock = {
                "beginningDatetime": beginning_datetime,
                "id": humanize(dehumanized_id),
                "offerId": event_offer_mock['id']
            }

            dehumanized_id += 1

            event_occurrence_mocks.append(event_occurrence_mock)

    return event_occurrence_mocks

def get_all_typed_event_stock_mocks(all_typed_event_occurrence_mocks):

    dehumanized_id = 10000

    stock_mocks = []
    for event_occurrence_mock in all_typed_event_occurrence_mocks:

        stock_mock = {
            "available": 10,
            "eventOccurrenceId": event_occurrence_mock['id'],
            "id": humanize(dehumanized_id),
            "price": 10
        }

        dehumanized_id += 1

        stock_mocks.append(stock_mock)

    return stock_mocks

def get_all_typed_thing_stock_mocks(all_typed_thing_offer_mocks):

    dehumanized_id = 20000

    stock_mocks = []
    for thing_offer_mock in all_typed_thing_offer_mocks:
        stock_mock = {
            "available": 10,
            "id": humanize(dehumanized_id),
            "offerId": thing_offer_mock['id'],
            "price": 10
        }

        dehumanized_id += 1

        stock_mocks.append(stock_mock)

    return stock_mocks

def get_all_typed_event_mediation_mocks(all_typed_event_offer_mocks):

    dehumanized_id = 10000

    mediation_mocks = []
    for event_offer_mock in all_typed_event_offer_mocks:
        mediation_mock = {
            "id": humanize(dehumanized_id),
            "offerId": event_offer_mock['id'],
        }

        dehumanized_id += 1

        mediation_mocks.append(mediation_mock)

    return mediation_mocks

def get_all_typed_thing_mediation_mocks(all_typed_thing_offer_mocks):

    dehumanized_id = 20000

    mediation_mocks = []
    for thing_offer_mock in all_typed_thing_offer_mocks:
        mediation_mock = {
            "id": humanize(dehumanized_id),
            "offerId": thing_offer_mock['id'],
        }

        dehumanized_id += 1

        mediation_mocks.append(mediation_mock)

    return mediation_mocks
