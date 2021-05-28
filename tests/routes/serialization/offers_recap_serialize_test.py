from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.paginated_offers_recap import OfferRecap
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.routes.serialization.offers_recap_serialize import serialize_offers_recap_paginated


def should_return_serialized_offers_with_relevant_informations():
    # given
    offer_id = 1
    stock_id = 2
    venue_id = 3
    offerer_id = 4
    stock = {
        "identifier": Identifier(stock_id),
        "has_booking_limit_datetime_passed": False,
        "remaining_quantity": 10,
        "beginning_datetime": None,
    }
    departement_code = 12
    offer = OfferRecap(
        identifier=Identifier(offer_id),
        has_booking_limit_datetimes_passed=False,
        is_active=True,
        is_editable=True,
        is_event=False,
        is_thing=True,
        product_isbn=None,
        name="Test Book",
        thumb_url="/thumb/url",
        offer_type="ThingType.AUDIOVISUEL",
        venue_identifier=Identifier(venue_id),
        venue_is_virtual=False,
        venue_managing_offerer_id=offerer_id,
        venue_name="La petite librairie",
        venue_public_name="Petite librairie",
        venue_offerer_name="Gérant de petites librairies",
        venue_departement_code=departement_code,
        stocks=[stock],
        status="ACTIVE",
    )
    paginated_offers_recap = PaginatedOffersRecap(offers_recap=[offer], current_page=1, total_pages=2, total_offers=3)

    # when
    result = serialize_offers_recap_paginated(paginated_offers_recap)

    # then
    expected_serialized_offer = [
        {
            "hasBookingLimitDatetimesPassed": False,
            "id": offer.identifier.scrambled,
            "isActive": True,
            "isEditable": True,
            "isEvent": False,
            "isThing": True,
            "productIsbn": None,
            "name": "Test Book",
            "status": "ACTIVE",
            "stocks": [
                {
                    "id": offer.stocks[0].identifier.scrambled,
                    "hasBookingLimitDatetimePassed": False,
                    "offerId": offer.identifier.scrambled,
                    "remainingQuantity": 10,
                    "beginningDatetime": None,
                }
            ],
            "thumbUrl": "/thumb/url",
            "type": "ThingType.AUDIOVISUEL",
            "venue": {
                "id": offer.venue.identifier.scrambled,
                "isVirtual": False,
                "departementCode": departement_code,
                "managingOffererId": offer.venue.managing_offerer_id.scrambled,
                "name": "La petite librairie",
                "offererName": "Gérant de petites librairies",
                "publicName": "Petite librairie",
            },
            "venueId": offer.venue.identifier.scrambled,
        }
    ]
    assert result["offers"] == expected_serialized_offer


def should_return_pagination_details():
    # given
    offer_id = 1
    stock_id = 2
    venue_id = 3
    offerer_id = 4
    stock = {
        "identifier": Identifier(stock_id),
        "has_booking_limit_datetime_passed": False,
        "remaining_quantity": 10,
        "beginning_datetime": None,
    }
    offer = OfferRecap(
        identifier=Identifier(offer_id),
        has_booking_limit_datetimes_passed=False,
        is_active=True,
        is_editable=True,
        is_event=False,
        is_thing=True,
        product_isbn=None,
        name="Test Book",
        thumb_url="/thumb/url",
        offer_type="ThingType.AUDIOVISUEL",
        venue_identifier=Identifier(venue_id),
        venue_is_virtual=False,
        venue_managing_offerer_id=offerer_id,
        venue_name="La petite librairie",
        venue_public_name="Petite librairie",
        venue_offerer_name="Gérant de petites librairies",
        venue_departement_code=None,
        stocks=[stock],
        status="ACTIVE",
    )
    current_page = 1
    total_pages = 2
    total_offers = 3
    paginated_offers_recap = PaginatedOffersRecap(
        offers_recap=[offer], current_page=current_page, total_pages=total_pages, total_offers=total_offers
    )

    # when
    result = serialize_offers_recap_paginated(paginated_offers_recap)

    # then
    assert result["page"] == current_page
    assert result["page_count"] == total_pages
    assert result["total_count"] == total_offers
