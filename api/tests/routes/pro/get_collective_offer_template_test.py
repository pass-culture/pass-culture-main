import pytest

from pcapi.core import testing
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # session + user
    # offerer
    # user_offerer
    # collective_offer_template
    # google_places_info
    num_queries = 5

    # location / address
    num_queries_with_location = num_queries + 1

    def test_get_collective_offer_template(self, client):
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(nationalProgramId=national_program.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        assert "iban" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
        assert response_json["venue"]["departementCode"] == offer.venue.offererAddress.address.departmentCode
        assert response_json["venue"]["managingOfferer"] == {
            "id": offer.venue.managingOffererId,
            "name": offer.venue.managingOfferer.name,
            "siren": offer.venue.managingOfferer.siren,
        }
        assert "stock" not in response_json
        assert "dateCreated" in response_json
        assert "educationalPriceDetail" in response_json
        assert response_json["imageCredit"] is None
        assert response_json["imageUrl"] is None
        assert response_json["name"] == offer.name
        assert response_json["id"] == offer.id
        assert response.json["nationalProgram"] == {"id": national_program.id, "name": national_program.name}
        assert response.json["dates"] == {
            "start": format_into_utc_date(offer.start),
            "end": format_into_utc_date(offer.end),
        }
        assert response.json["formats"] == [format.value for format in offer.formats]
        assert response.json["displayedStatus"] == "PUBLISHED"
        assert response.json["allowedActions"] == [
            "CAN_EDIT_DETAILS",
            "CAN_ARCHIVE",
            "CAN_CREATE_BOOKABLE_OFFER",
            "CAN_HIDE",
            "CAN_SHARE",
        ]

        assert response_json["location"] == {
            "location": None,
            "locationComment": None,
            "locationType": "TO_BE_DEFINED",
        }

    def test_location_address_venue(self, client):
        venue = offerers_factories.VenueFactory()
        # Venue has its location, the offer has another one but they should appear as venue location
        oa = offerers_factories.OffererAddressFactory(
            offerer=venue.managingOfferer, address=venue.offererAddress.address, label=venue.publicName
        )
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddress=oa,
            interventionArea=None,
        )
        assert offer.offererAddress != venue.offererAddress
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries_with_location):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is True
        assert response_location["location"]["banId"] == venue.offererAddress.address.banId
        assert response_json["interventionArea"] == []

    # TODO(OA): This test matches the data pre location refactoring
    # venue and offer have the same OA/location
    def test_location_address_venue_legacy(self, client):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddress.id,
            interventionArea=None,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        ban_id = venue.offererAddress.address.banId
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 200

            response_json = response.json
            response_location = response_json["location"]
            assert response_location["locationType"] == "ADDRESS"
            assert response_location["locationComment"] is None
            assert response_location["location"] is not None
            assert response_location["location"]["isVenueLocation"] is True
            assert response_location["location"]["banId"] == ban_id
            assert response_json["interventionArea"] == []

    def test_location_school(self, client):
        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.SCHOOL,
            locationComment=None,
            offererAddressId=None,
            interventionArea=["33", "75", "93"],
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "SCHOOL"
        assert response_location["locationComment"] is None
        assert response_location["location"] is None
        assert response_json["interventionArea"] == ["33", "75", "93"]

    def test_location_address(self, client):
        venue = offerers_factories.VenueFactory()
        oa = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)
        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddress=oa,
            interventionArea=None,
            venue=venue,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries_with_location):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is False
        assert response_location["location"]["banId"] == oa.address.banId
        assert response_json["interventionArea"] == []

    def test_location_same_address_different_label(self, client):
        venue = offerers_factories.VenueFactory()
        oa = offerers_factories.OffererAddressFactory(
            offerer=venue.managingOfferer, address=venue.offererAddress.address
        )
        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddress=oa,
            interventionArea=None,
            venue=venue,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries_with_location):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is False
        assert response_location["location"]["banId"] == oa.address.banId
        assert response_json["interventionArea"] == []

    def test_location_to_be_defined(self, client):
        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.TO_BE_DEFINED,
            locationComment="In space",
            offererAddressId=None,
            interventionArea=["33", "75", "93"],
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "TO_BE_DEFINED"
        assert response_location["locationComment"] == "In space"
        assert response_location["location"] is None
        assert response_json["interventionArea"] == ["33", "75", "93"]

    def test_performance(self, client):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            with testing.assert_no_duplicated_queries():
                client.get(f"/collective/offers-template/{offer_id}")


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email=pro_user.email)
        offer_id = offer.id
        expected_num_queries = 5
        # get user_session + user
        # get offerer
        # check user_offerer exists
        # rollback
        # rollback
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers-template/{offer_id}")
            assert response.status_code == 403
