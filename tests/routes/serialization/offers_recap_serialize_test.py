from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap, OfferRecap, OfferRecapVenue, OfferRecapStock
from routes.serialization.offers_recap_serialize import serialize_offers_recap_paginated
from utils.human_ids import humanize


def test_should_return_offers_dict_with_relevant_informations():
    # given
    offer_id = 1
    stock_id = 2
    venue_id = 3
    offerer_id = 4
    stock = {"identifier": stock_id, "is_event_expired": False, "remaining_quantity": 10}
    offer = OfferRecap(
            identifier=offer_id,
            availability_message="Encore 10 stocks restants",
            has_booking_limit_datetimes_passed=False,
            is_active=True,
            is_editable=True,
            is_fully_booked=False,
            is_event=False,
            is_thing=True,
            name="Test Book",
            thumb_url="/thumb/url",
            offer_type="ThingType.AUDIOVISUEL",
            venue_identifier=venue_id,
            venue_is_virtual=False,
            venue_managing_offerer_id=offerer_id,
            venue_name="La petite librairie",
            venue_public_name="Petite librairie",
            stocks=[stock]
    )
    paginated_offers_recap = PaginatedOffersRecap([offer], 1)

    # when
    serialized_offers = serialize_offers_recap_paginated(paginated_offers_recap)

    # then
    assert serialized_offers[0] == {
        "availabilityMessage": "Encore 10 stocks restants",
        "hasBookingLimitDatetimesPassed": False,
        "id": humanize(offer_id),
        "isActive": True,
        "isEditable": True,
        "isEvent": False,
        "isFullyBooked": False,
        "isThing": True,
        "name": "Test Book",
        "stocks": [{
            "id": humanize(stock_id),
            "offerId": humanize(offer_id),
            "remainingQuantity": 10
        }],
        "thumbUrl": "/thumb/url",
        "type": "ThingType.AUDIOVISUEL",
        "venue": {
            "id": humanize(venue_id),
            "isVirtual": False,
            "managingOffererId": humanize(offerer_id),
            "name": "La petite librairie",
            "publicName": "Petite librairie",
        },
        "venueId": humanize(venue_id),
    }
