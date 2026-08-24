from unittest import mock

import pytest
import sqlalchemy.orm as sa_orm

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.models import api_errors
from pcapi.routes.public.individual_offers.v1 import serialization
from pcapi.routes.public.individual_offers.v1 import utils
from pcapi.routes.public.individual_offers.v1.serializers import events as events_serializers


pytestmark = pytest.mark.usefixtures("db_session")


class ExtractVenueAndOffererAddressFromLocationTest:
    GET_VENUE = "pcapi.routes.public.individual_offers.v1.utils.get_venue_with_offerer_address"
    GET_ADDRESS = "pcapi.routes.public.utils.get_address_or_raise_404"
    GET_VENUE_LOCATION = "pcapi.core.offers.api.get_or_create_offerer_address_from_address_body"
    GET_OFFER_LOCATION = "pcapi.core.offerers.api.get_or_create_offer_location"

    # --- No location sent

    @mock.patch(GET_VENUE)
    def test_should_return_no_venue_and_no_offerer_address_when_no_location_is_sent(
        self, get_venue_with_offerer_address
    ):
        assert utils.extract_venue_and_offerer_address_from_location(None) == (None, None)
        get_venue_with_offerer_address.assert_not_called()

    # --- Venue resolution

    @mock.patch(GET_VENUE)
    def test_should_look_the_venue_up_by_the_id_sent_in_the_location(self, get_venue_with_offerer_address):
        venue = offerers_factories.VenueFactory()
        get_venue_with_offerer_address.return_value = venue

        returned_venue, _ = utils.extract_venue_and_offerer_address_from_location(
            serialization.PhysicalLocation(venue_id=venue.id)
        )

        get_venue_with_offerer_address.assert_called_once_with(venue.id)
        assert returned_venue == venue

    @mock.patch(GET_VENUE)
    def test_should_not_look_the_venue_up_when_it_is_given_by_the_caller(self, get_venue_with_offerer_address):
        venue = offerers_factories.VenueFactory()

        returned_venue, _ = utils.extract_venue_and_offerer_address_from_location(
            serialization.PhysicalLocation(venue_id=venue.id), venue=venue
        )

        get_venue_with_offerer_address.assert_not_called()
        assert returned_venue == venue

    # --- Physical and digital locations

    @pytest.mark.parametrize(
        "build_location",
        [
            lambda venue: serialization.PhysicalLocation(venue_id=venue.id),
            lambda venue: serialization.DigitalLocation(venue_id=venue.id, url="https://example.com"),
        ],
        ids=["physical", "digital"],
    )
    @mock.patch(GET_ADDRESS)
    @mock.patch(GET_VENUE_LOCATION)
    def test_should_reuse_the_venue_location_without_looking_up_an_address(
        self, get_or_create_offerer_address_from_address_body, get_address_or_raise_404, build_location
    ):
        venue = offerers_factories.VenueFactory()

        _, offerer_address = utils.extract_venue_and_offerer_address_from_location(build_location(venue), venue=venue)

        get_address_or_raise_404.assert_not_called()
        get_or_create_offerer_address_from_address_body.assert_called_once_with(
            offerers_schemas.LocationOnlyOnVenueModel(), venue
        )
        assert offerer_address == get_or_create_offerer_address_from_address_body.return_value

    # --- Address location

    @mock.patch(GET_ADDRESS)
    def test_should_look_the_address_up_by_the_id_sent_in_the_location(self, get_address_or_raise_404):
        venue = offerers_factories.VenueFactory()
        address = geography_factories.AddressFactory()
        get_address_or_raise_404.return_value = address

        utils.extract_venue_and_offerer_address_from_location(
            serialization.AddressLocation(venue_id=venue.id, address_id=address.id, address_label="Salle Jean Vilar"),
            venue=venue,
        )

        get_address_or_raise_404.assert_called_once_with(address.id)

    @mock.patch(GET_OFFER_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_create_an_offer_location_when_the_address_differs_from_the_venue_one(
        self, get_address_or_raise_404, get_or_create_offer_location
    ):
        venue = offerers_factories.VenueFactory()
        address = geography_factories.AddressFactory()
        get_address_or_raise_404.return_value = address

        _, offerer_address = utils.extract_venue_and_offerer_address_from_location(
            serialization.AddressLocation(venue_id=venue.id, address_id=address.id, address_label="Salle Jean Vilar"),
            venue=venue,
        )

        get_or_create_offer_location.assert_called_once_with(
            offerer_id=venue.managingOffererId,
            venue_id=venue.id,
            address_id=address.id,
            label="Salle Jean Vilar",
        )
        assert offerer_address == get_or_create_offer_location.return_value

    @mock.patch(GET_OFFER_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_create_an_offer_location_when_only_the_label_differs_from_the_venue_public_name(
        self, get_address_or_raise_404, get_or_create_offer_location
    ):
        venue = offerers_factories.VenueFactory()
        get_address_or_raise_404.return_value = venue.offererAddress.address

        utils.extract_venue_and_offerer_address_from_location(
            serialization.AddressLocation(
                venue_id=venue.id,
                address_id=venue.offererAddress.addressId,
                address_label="Salle Jean Vilar",
            ),
            venue=venue,
        )

        get_or_create_offer_location.assert_called_once_with(
            offerer_id=venue.managingOffererId,
            venue_id=venue.id,
            address_id=venue.offererAddress.addressId,
            label="Salle Jean Vilar",
        )

    @mock.patch(GET_VENUE_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_reuse_the_venue_location_when_the_address_and_the_label_match_the_venue_ones(
        self, get_address_or_raise_404, get_or_create_offerer_address_from_address_body
    ):
        venue = offerers_factories.VenueFactory()
        get_address_or_raise_404.return_value = venue.offererAddress.address

        _, offerer_address = utils.extract_venue_and_offerer_address_from_location(
            serialization.AddressLocation(
                venue_id=venue.id,
                address_id=venue.offererAddress.addressId,
                address_label=venue.publicName,
            ),
            venue=venue,
        )

        get_or_create_offerer_address_from_address_body.assert_called_once_with(
            offerers_schemas.LocationOnlyOnVenueModel(), venue
        )
        assert offerer_address == get_or_create_offerer_address_from_address_body.return_value

    @mock.patch(GET_OFFER_LOCATION)
    @mock.patch(GET_VENUE_LOCATION)
    @mock.patch(GET_ADDRESS)
    def test_should_create_an_offer_location_when_no_label_is_sent_and_the_venue_has_a_public_name(
        self, get_address_or_raise_404, get_or_create_offerer_address_from_address_body, get_or_create_offer_location
    ):
        venue = offerers_factories.VenueFactory()
        get_address_or_raise_404.return_value = venue.offererAddress.address

        utils.extract_venue_and_offerer_address_from_location(
            serialization.AddressLocation(
                venue_id=venue.id, address_id=venue.offererAddress.addressId, address_label=None
            ),
            venue=venue,
        )

        get_or_create_offerer_address_from_address_body.assert_not_called()
        get_or_create_offer_location.assert_called_once_with(
            offerer_id=venue.managingOffererId,
            venue_id=venue.id,
            address_id=venue.offererAddress.addressId,
            label=None,
        )


class GetVenueWithOffererAddressTest:
    def test_should_return_the_venue_matching_the_id(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory()

        assert utils.get_venue_with_offerer_address(venue.id) == venue

    def test_should_raise_when_no_venue_matches_the_id(self):
        venue = offerers_factories.VenueFactory()

        with pytest.raises(sa_orm.exc.NoResultFound):
            utils.get_venue_with_offerer_address(venue.id + 1000)

    def test_should_load_the_offerer_address_along_with_the_venue(self):
        venue = offerers_factories.VenueFactory()

        venue_id = venue.id

        with testing.assert_num_queries(1):
            fetched_venue = utils.get_venue_with_offerer_address(venue_id)
            assert fetched_venue.offererAddress.addressId


class CheckOfferSubcategoryTest:
    def test_should_accept_a_body_that_carries_no_category_related_fields(self):
        body = events_serializers.EventOfferEdition(name="Jules et Jim")

        utils.check_offer_subcategory(body, subcategories.SEANCE_CINE.id)

    def test_should_accept_the_subcategory_the_offer_already_has(self):
        body = events_serializers.EventOfferEdition(category_related_fields={"category": "SEANCE_CINE"})

        utils.check_offer_subcategory(body, subcategories.SEANCE_CINE.id)

    def test_should_refuse_another_subcategory_for_an_event(self):
        body = events_serializers.EventOfferEdition(category_related_fields={"category": "SEANCE_CINE"})

        with pytest.raises(api_errors.ApiErrors) as error:
            utils.check_offer_subcategory(body, subcategories.CONCERT.id)

        assert error.value.errors == {"categoryRelatedFields.category": ["The category cannot be changed"]}
        assert error.value.status_code == 400
