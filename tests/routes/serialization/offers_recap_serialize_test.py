import json

from domain.pro_offers.paginated_offers import PaginatedOffers
from routes.serialization.offers_recap_serialize import serialize_offers_recap_paginated
from tests.model_creators.generic_creators import create_venue, create_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_stock_from_offer
from utils.human_ids import humanize


def test_should_return_offers_dict_with_relevant_informations():
    # given
    offerId = 1
    stockId = 2
    venueId = 3
    venue = create_venue(offerer=create_offerer(), idx=venueId)
    offer = create_offer_with_thing_product(venue, idx=offerId)
    stock = create_stock_from_offer(offer, idx=stockId)
    stock.offerId = offer.id
    paginated_offers = PaginatedOffers([offer], 1)

    # when
    serialized_offers = serialize_offers_recap_paginated(paginated_offers)

    # then
    assert json.loads(json.dumps(serialized_offers[0])) == {
        "availabilityMessage": "Encore 10 stocks restants",
        "hasBookingLimitDatetimesPassed": False,
        "id": humanize(offerId),
        "isActive": True,
        "isEditable": True,
        "isEvent": False,
        "isFullyBooked": False,
        "isThing": True,
        "name": "Test Book",
        "stocks": [{
            "id": humanize(stockId),
            "isEventExpired": False,
            "offerId": humanize(offerId),
            "remainingQuantity": 10
        }],
        "thumbUrl": None,
        "type": "ThingType.AUDIOVISUEL",
        "venue": {
            "id": humanize(venueId),
            "isVirtual": False,
            "name": "La petite librairie",
            "publicName": None,
        },
        "venueId": None,
    }
