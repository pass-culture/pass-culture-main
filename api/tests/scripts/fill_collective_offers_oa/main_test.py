import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.scripts.fill_collective_offers_oa import main


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize(
    "model,factory",
    (
        (models.CollectiveOffer, factories.PublishedCollectiveOfferFactory),
        (models.CollectiveOfferTemplate, factories.CollectiveOfferTemplateFactory),
    ),
)
def test_get_query_collective_offers(model, factory):
    venue = offerers_factories.VenueFactory()
    other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

    offers = [
        factory(venue=venue),
        factory(
            venue=venue,
            offerVenue={
                "addressType": models.OfferAddressType.OFFERER_VENUE.value,
                "otherAddress": "",
                "venueId": venue.id,
            },
        ),
        factory(
            venue=venue,
            offerVenue={
                "addressType": models.OfferAddressType.OFFERER_VENUE.value,
                "otherAddress": "",
                "venueId": other_venue.id,
            },
        ),
    ]

    result = main.get_query(model=model, location_type_none_only=False)
    assert result.count() == 3
    result_iter = iter(result)

    result_offer, result_venue, result_oa = next(result_iter)
    assert result_offer.id == offers[0].id
    assert result_venue is None
    assert result_oa is None

    result_offer, result_venue, result_oa = next(result_iter)
    assert result_offer.id == offers[1].id
    assert result_venue.id == venue.id
    assert result_oa.id == venue.offererAddress.id

    result_offer, result_venue, result_oa = next(result_iter)
    assert result_offer.id == offers[2].id
    assert result_venue.id == other_venue.id
    assert result_oa.id == other_venue.offererAddress.id


@pytest.mark.parametrize(
    "model,factory",
    (
        (models.CollectiveOffer, factories.PublishedCollectiveOfferFactory),
        (models.CollectiveOfferTemplate, factories.CollectiveOfferTemplateFactory),
    ),
)
def test_get_query_collective_offers_location_type_none_only(model, factory):
    offers = [
        factory(locationType=None),
        factory(locationType=models.CollectiveLocationType.SCHOOL),
    ]

    result = main.get_query(model=model, location_type_none_only=True)

    [(offer, _, _)] = result
    assert offer.id == offers[0].id


def test_get_or_create_offerer_address():
    venue = offerers_factories.VenueFactory()

    # call with OA = None -> return None
    offerer_address_by_key = {}
    with assert_num_queries(0):
        result = main.get_or_create_offerer_address(
            venue=venue, venue_offerer_address=None, offerer_address_by_key=offerer_address_by_key
        )

    assert result is None
    assert offerer_address_by_key == {}

    # create and return an OA, and store it in offerer_address_by_key
    offerer_address_by_key = {}
    oa = venue.offererAddress
    with assert_num_queries(1):
        result = main.get_or_create_offerer_address(
            venue=venue, venue_offerer_address=oa, offerer_address_by_key=offerer_address_by_key
        )

    assert result.offererId == venue.managingOffererId
    assert result.addressId == venue.offererAddress.addressId
    assert result.label == venue.common_name
    assert offerer_address_by_key == {(result.offererId, result.addressId, result.label): result}

    # get the OA from offerer_address_by_key, no query
    with assert_num_queries(0):
        result = main.get_or_create_offerer_address(
            venue=venue, venue_offerer_address=oa, offerer_address_by_key=offerer_address_by_key
        )

    assert result.offererId == venue.managingOffererId
    assert result.addressId == venue.offererAddress.addressId
    assert result.label == venue.common_name
    assert offerer_address_by_key == {(result.offererId, result.addressId, result.label): result}


@pytest.mark.parametrize(
    "factory", (factories.PublishedCollectiveOfferFactory, factories.CollectiveOfferTemplateFactory)
)
def test_fill_location_fields_school(factory):
    offer = factory(
        locationType=None,
        locationComment=None,
        offererAddress=None,
        offerVenue={"addressType": models.OfferAddressType.SCHOOL.value, "otherAddress": "", "venueId": None},
    )
    assert offer.offerVenue is not None

    offerer_address_by_key = {}
    with assert_num_queries(0):
        main.fill_location_fields(
            offer=offer,
            venue_from_offer_venue=None,
            oa_from_offer_venue=None,
            offerer_address_by_key=offerer_address_by_key,
        )

    assert offer.locationType == models.CollectiveLocationType.SCHOOL
    assert offer.locationComment is None
    assert offer.offererAddress is None
    assert offerer_address_by_key == {}


@pytest.mark.parametrize(
    "factory", (factories.PublishedCollectiveOfferFactory, factories.CollectiveOfferTemplateFactory)
)
def test_fill_location_fields_other(factory):
    offer = factory(
        locationType=None,
        locationComment=None,
        offererAddress=None,
        offerVenue={
            "addressType": models.OfferAddressType.OTHER.value,
            "otherAddress": "Chez toi",
            "venueId": None,
        },
    )
    assert offer.offerVenue is not None

    offerer_address_by_key = {}
    with assert_num_queries(0):
        main.fill_location_fields(
            offer=offer,
            venue_from_offer_venue=None,
            oa_from_offer_venue=None,
            offerer_address_by_key=offerer_address_by_key,
        )

    assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
    assert offer.locationComment == "Chez toi"
    assert offer.offererAddress is None
    assert offerer_address_by_key == {}


@pytest.mark.parametrize(
    "factory", (factories.PublishedCollectiveOfferFactory, factories.CollectiveOfferTemplateFactory)
)
def test_fill_location_fields_offerer_venue_same_venue(factory):
    venue = offerers_factories.VenueFactory()
    offer = factory(
        venue=venue,
        locationType=None,
        locationComment=None,
        offererAddress=None,
        offerVenue={
            "addressType": models.OfferAddressType.OFFERER_VENUE.value,
            "otherAddress": "",
            "venueId": venue.id,
        },
    )
    assert offer.offerVenue is not None

    offerer_address_by_key = {}
    oa_from_offer_venue = venue.offererAddress
    with assert_num_queries(0):
        main.fill_location_fields(
            offer=offer,
            venue_from_offer_venue=venue,
            oa_from_offer_venue=oa_from_offer_venue,
            offerer_address_by_key=offerer_address_by_key,
        )

    assert offer.locationType == models.CollectiveLocationType.ADDRESS
    assert offer.locationComment is None
    assert offer.offererAddress == venue.offererAddress
    assert offerer_address_by_key == {}


@pytest.mark.parametrize(
    "factory", (factories.PublishedCollectiveOfferFactory, factories.CollectiveOfferTemplateFactory)
)
def test_fill_location_fields_offerer_venue_other_venue(factory):
    venue = offerers_factories.VenueFactory()
    other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
    offer = factory(
        venue=venue,
        locationType=None,
        locationComment=None,
        offererAddress=None,
        offerVenue={
            "addressType": models.OfferAddressType.OFFERER_VENUE.value,
            "otherAddress": "",
            "venueId": other_venue.id,
        },
    )
    assert offer.offerVenue is not None

    oa_from_offer_venue = other_venue.offererAddress
    offerer_address_by_key = {}
    with assert_num_queries(1):  # 1 query to select the OA
        main.fill_location_fields(
            offer=offer,
            venue_from_offer_venue=other_venue,
            oa_from_offer_venue=oa_from_offer_venue,
            offerer_address_by_key=offerer_address_by_key,
        )

    assert offer.locationType == models.CollectiveLocationType.ADDRESS
    assert offer.locationComment is None

    new_oa = offer.offererAddress
    assert new_oa.offererId == other_venue.managingOffererId
    assert new_oa.addressId == oa_from_offer_venue.addressId
    assert new_oa.label == other_venue.common_name
    assert offerer_address_by_key == {(new_oa.offererId, new_oa.addressId, new_oa.label): new_oa}
