import datetime

import pytest

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational.testing import get_serialized_address
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import db as db_utils


URL = "/collective/offers-template"


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # collective_offer_template

    def test_one_collective_offer_template(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.CollectiveOfferTemplateFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer.id,
                "allowedActions": [
                    "CAN_EDIT_DETAILS",
                    "CAN_ARCHIVE",
                    "CAN_CREATE_BOOKABLE_OFFER",
                    "CAN_HIDE",
                    "CAN_SHARE",
                ],
                "dates": {
                    "start": offer.start.isoformat() + "Z",
                    "end": offer.end.isoformat() + "Z",
                },
                "venue": {
                    "id": venue.id,
                    "departementCode": venue.offererAddress.address.departmentCode,
                    "isVirtual": False,
                    "name": venue.name,
                    "offererName": venue.managingOfferer.name,
                    "publicName": venue.publicName,
                },
                "location": {
                    "location": None,
                    "locationComment": None,
                    "locationType": "TO_BE_DEFINED",
                },
                "name": offer.name,
                "imageUrl": None,
                "displayedStatus": "PUBLISHED",
            }
        ]

    def test_one_collective_offer_template_location_school(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        factories.CollectiveOfferTemplateOnSchoolLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == {"location": None, "locationComment": None, "locationType": "SCHOOL"}

    def test_one_collective_offer_template_location_venue_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.CollectiveOfferTemplateOnAddressVenueLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=venue.common_name, is_venue_location=True
        )

    def test_one_collective_offer_template_location_other_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.CollectiveOfferTemplateOnOtherAddressLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=offer.offererAddress.label, is_venue_location=False
        )

    def test_one_collective_offer_template_location_to_be_defined(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        factories.CollectiveOfferTemplateOnToBeDefinedLocationFactory(venue=venue, locationComment="over here")

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == {
            "location": None,
            "locationComment": "over here",
            "locationType": "TO_BE_DEFINED",
        }

    def test_collective_offer_template_user_has_no_access(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        factories.CollectiveOfferTemplateFactory(venue=venue)
        other_user = users_factories.UserFactory()

        client = client.with_session_auth(other_user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        assert response.json == []

    def test_with_date_filters(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        factories.CollectiveOfferTemplateFactory(
            venue=venue,
            dateCreated=datetime.datetime(2022, 8, 10),
            dateRange=db_utils.make_timerange(
                start=datetime.datetime(2022, 8, 10),
                end=datetime.datetime(2022, 8, 15),
            ),
        )
        offer_with_no_date = factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime(2022, 8, 10), dateRange=None
        )

        # no filters date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers-template")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 2

        # filters date range including date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                "/collective/offers-template?periodBeginningDate=2022-08-09&periodEndingDate=2022-08-17"
            )
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 2

        # filters date range not including date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                "/collective/offers-template?periodBeginningDate=2022-10-08&periodEndingDate=2022-10-12"
            )
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == offer_with_no_date.id

        # filters date range including the lower date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                "/collective/offers-template?periodBeginningDate=2022-08-08&periodEndingDate=2022-08-12"
            )
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 2

        # filters date range excluding the lower date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(
                "/collective/offers-template?periodBeginningDate=2022-08-13&periodEndingDate=2022-08-20"
            )
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == offer_with_no_date.id

        # filters beginning date before lower date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers-template?periodBeginningDate=2022-08-10")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 2

        # filters beginning date after lower date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers-template?periodBeginningDate=2022-08-12")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == offer_with_no_date.id

        # filters ending date after lower date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers-template?periodEndingDate=2022-08-12")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 2

        # filters ending date before lower date range
        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers-template?periodEndingDate=2022-08-09")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == offer_with_no_date.id

    def test_offers_sorting(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        now = datetime.datetime.now()
        offer_1 = factories.CollectiveOfferTemplateFactory(dateCreated=now - datetime.timedelta(days=2), venue=venue)
        offer_2 = factories.CollectiveOfferTemplateFactory(dateCreated=now - datetime.timedelta(days=3), venue=venue)
        archived_offer_1 = factories.create_collective_offer_template_by_status(
            status=models.CollectiveOfferDisplayedStatus.ARCHIVED, dateCreated=now, venue=venue
        )
        archived_offer_2 = factories.create_collective_offer_template_by_status(
            status=models.CollectiveOfferDisplayedStatus.ARCHIVED,
            dateCreated=now - datetime.timedelta(days=1),
            venue=venue,
        )

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        # archived offers must appear at the end of the list even when created more recently
        assert [offer["id"] for offer in response.json] == [
            offer_1.id,
            offer_2.id,
            archived_offer_1.id,
            archived_offer_2.id,
        ]

    @pytest.mark.parametrize("status", models.COLLECTIVE_OFFER_TEMPLATE_STATUSES)
    def test_each_status_filter(self, client, status):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.create_collective_offer_template_by_status(status, venue=venue)

        # add an offer with another status that will not be present in the result
        other_status = next((s for s in models.COLLECTIVE_OFFER_TEMPLATE_STATUSES if s != status))
        factories.create_collective_offer_template_by_status(status=other_status, venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?status={status.value}")

        [response_offer] = response.json
        assert response_offer["id"] == offer.id

    def test_filter_location(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        oa = offerers_factories.OffererAddressFactory()
        offer_school = factories.CollectiveOfferTemplateOnSchoolLocationFactory(venue=venue)
        offer_address = factories.CollectiveOfferTemplateOnOtherAddressLocationFactory(venue=venue, offererAddress=oa)
        factories.CollectiveOfferTemplateOnOtherAddressLocationFactory(venue=venue)
        offer_to_be_defined = factories.CollectiveOfferTemplateOnToBeDefinedLocationFactory(venue=venue)

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=SCHOOL")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_school.id

        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=TO_BE_DEFINED")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_to_be_defined.id

        oa_id = oa.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=ADDRESS&offererAddressId={oa_id}")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_address.id

    def test_filter_format(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        factories.CollectiveOfferTemplateFactory(formats=[EacFormat.ATELIER_DE_PRATIQUE], venue=venue)
        offer_2 = factories.CollectiveOfferTemplateFactory(formats=[EacFormat.CONCERT], venue=venue)

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?format={EacFormat.CONCERT.value}")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_2.id


@pytest.mark.usefixtures("db_session")
class Return400Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # rollback

    def test_return_error_when_status_is_wrong(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?status=NOT_A_VALID_STATUS")
            assert response.status_code == 400

        assert response.json == {
            "status.0": [
                "Input should be 'PUBLISHED', 'UNDER_REVIEW', 'REJECTED', 'PREBOOKED', 'BOOKED', 'HIDDEN', "
                "'EXPIRED', 'ENDED', 'CANCELLED', 'REIMBURSED', 'ARCHIVED' or 'DRAFT'",
            ]
        }

    def test_filter_location_type_error(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=BLOUP")

        assert response.status_code == 400
        assert response.json == {"locationType": ["Input should be 'SCHOOL', 'ADDRESS' or 'TO_BE_DEFINED'"]}

    def test_filter_offerer_address_not_accepted(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=SCHOOL&offererAddressId=1")

        assert response.status_code == 400
        assert response.json == {"": ["Cannot provide offererAddressId when locationType is not ADDRESS"]}
