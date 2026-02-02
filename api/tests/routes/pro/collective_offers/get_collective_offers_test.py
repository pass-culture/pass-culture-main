import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational.testing import get_serialized_address
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


URL = "/collective/bookable-offers"


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # collective_offer

    def test_one_collective_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.BookedCollectiveOfferFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        institution = offer.institution
        stock = offer.collectiveStock
        assert response.json == [
            {
                "id": offer.id,
                "allowedActions": ["CAN_EDIT_DISCOUNT", "CAN_DUPLICATE", "CAN_CANCEL"],
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
                "stock": {
                    "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat() + "Z",
                    "price": float(stock.price),
                    "numberOfTickets": stock.numberOfTickets,
                },
                "educationalInstitution": {
                    "name": institution.name,
                    "city": institution.city,
                    "id": institution.id,
                    "institutionId": institution.institutionId,
                    "institutionType": institution.institutionType,
                    "phoneNumber": institution.phoneNumber,
                    "postalCode": institution.postalCode,
                },
                "imageUrl": None,
                "displayedStatus": "BOOKED",
                "dates": {"start": stock.startDatetime.isoformat() + "Z", "end": stock.endDatetime.isoformat() + "Z"},
            }
        ]

    def test_one_collective_offer_location_school(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        factories.CollectiveOfferOnSchoolLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == {"location": None, "locationComment": None, "locationType": "SCHOOL"}

    def test_one_collective_offer_location_venue_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.CollectiveOfferOnAddressVenueLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=venue.common_name, is_venue_location=True
        )

    def test_one_collective_offer_location_other_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.CollectiveOfferOnOtherAddressLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=offer.offererAddress.label, is_venue_location=False
        )

    def test_collective_offer_is_public_api(self, client):
        provider = providers_factories.ProviderFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.PublishedCollectiveOfferFactory(venue=venue, provider=provider)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["id"] == offer.id

    def test_user_has_no_access(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        factories.PublishedCollectiveOfferFactory(venue=venue)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        assert response.json == []

    def test_with_date_filters(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        now = date_utils.get_naive_utc_now()
        offer = factories.CollectiveStockFactory(collectiveOffer__venue=venue, startDatetime=now).collectiveOffer
        past_offer = factories.CollectiveStockFactory(
            collectiveOffer__venue=venue, startDatetime=now - datetime.timedelta(days=10)
        ).collectiveOffer
        future_offer = factories.CollectiveStockFactory(
            collectiveOffer__venue=venue, startDatetime=now + datetime.timedelta(days=10)
        ).collectiveOffer

        lower = (now - datetime.timedelta(days=1)).date().isoformat()
        upper = (now + datetime.timedelta(days=1)).date().isoformat()
        client = client.with_session_auth(user_offerer.user.email)

        # filter on periodBeginningDate and periodEndingDate
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?periodBeginningDate={lower}&periodEndingDate={upper}")
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["id"] == offer.id

        # filter on periodBeginningDate only
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?periodBeginningDate={lower}")
            assert response.status_code == 200

        assert {offer["id"] for offer in response.json} == {offer.id, future_offer.id}

        # filter on periodEndingDate only
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?periodEndingDate={upper}")
            assert response.status_code == 200

        assert {offer["id"] for offer in response.json} == {offer.id, past_offer.id}

    def test_with_multiple_status_filters(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        factories.PublishedCollectiveOfferFactory(venue=venue)
        booked_offer = factories.BookedCollectiveOfferFactory(venue=venue)
        prebooked_offer = factories.PrebookedCollectiveOfferFactory(venue=venue)
        factories.ArchivedCollectiveOfferFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?status=BOOKED&status=PREBOOKED")
            assert response.status_code == 200

        response_json = response.json
        assert {offer["id"] for offer in response_json} == {booked_offer.id, prebooked_offer.id}

    def test_collective_offers_sorting(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        now = date_utils.get_naive_utc_now()
        offer_1 = factories.PublishedCollectiveOfferFactory(dateCreated=now - datetime.timedelta(days=2), venue=venue)
        offer_2 = factories.PublishedCollectiveOfferFactory(dateCreated=now - datetime.timedelta(days=3), venue=venue)
        archived_offer_1 = factories.ArchivedCollectiveOfferFactory(dateCreated=now, venue=venue)
        archived_offer_2 = factories.ArchivedCollectiveOfferFactory(
            dateCreated=now - datetime.timedelta(days=1), venue=venue
        )

        # not urgent (booking limit > 7 days)
        not_urgent_offer = factories.PrebookedCollectiveOfferFactory(
            venue=venue, dateCreated=now - datetime.timedelta(days=12)
        )
        not_urgent_offer.collectiveStock.bookingLimitDatetime = now + datetime.timedelta(days=10)

        # medium urgency (booking limit between 2-7 days)
        medium_offer = factories.PublishedCollectiveOfferFactory(
            venue=venue, dateCreated=now - datetime.timedelta(days=8)
        )
        medium_offer.collectiveStock.bookingLimitDatetime = now + datetime.timedelta(days=4)

        # urgent
        urgent_offer = factories.PrebookedCollectiveOfferFactory(
            venue=venue, dateCreated=now - datetime.timedelta(days=7)
        )
        urgent_offer.collectiveStock.bookingLimitDatetime = now + datetime.timedelta(days=1)

        # same urgency, created more recently
        urgent_recent_offer = factories.PrebookedCollectiveOfferFactory(
            venue=venue, dateCreated=now - datetime.timedelta(days=6)
        )
        urgent_recent_offer.collectiveStock.bookingLimitDatetime = now + datetime.timedelta(days=1)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 200

        ids = [offer["id"] for offer in response.json]
        assert len(ids) == 8

        # Sorting logic:
        # 1. Non-archived offers come before archived ones
        # 2. Offers with PREBOOKED or PUBLISHED status and booking limit < 7 days are prioritized by urgency
        # 3. When same urgency, sorted by dateCreated (most recent first)
        # 4. Archived offers are always last
        assert ids == [
            urgent_recent_offer.id,
            urgent_offer.id,
            medium_offer.id,
            offer_1.id,
            offer_2.id,
            not_urgent_offer.id,
            archived_offer_1.id,
            archived_offer_2.id,
        ]

    @pytest.mark.parametrize(
        "status",
        set(models.CollectiveOfferDisplayedStatus) - {models.CollectiveOfferDisplayedStatus.HIDDEN},
    )
    def test_each_status_filter(self, client, status):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.create_collective_offer_by_status(status, venue=venue)

        # Add an offer with another status that will not be present in the result
        other_status = next((s for s in models.CollectiveOfferDisplayedStatus if s != status))
        factories.create_collective_offer_by_status(status=other_status, venue=venue)

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?status={status.value}")

        [response_offer] = response.json
        assert response_offer["id"] == offer.id

    def test_filter_location(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        oa = offerers_factories.OffererAddressFactory()
        offer_school = factories.CollectiveOfferOnSchoolLocationFactory(venue=venue)
        offer_address = factories.CollectiveOfferOnOtherAddressLocationFactory(venue=venue, offererAddress=oa)
        factories.CollectiveOfferOnOtherAddressLocationFactory(venue=venue)
        offer_to_be_defined = factories.CollectiveOfferOnToBeDefinedLocationFactory(venue=venue)

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=SCHOOL")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_school.id

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=TO_BE_DEFINED")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_to_be_defined.id

        oa_id = oa.id
        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?locationType=ADDRESS&offererAddressId={oa_id}")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_address.id


@pytest.mark.usefixtures("db_session")
class Return400Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # rollback

    def test_return_error_when_status_is_wrong(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?status=NOT_A_VALID_STATUS")
            assert response.status_code == 400

        assert response.json == {
            "status.0": [
                "Input should be 'PUBLISHED', 'UNDER_REVIEW', 'REJECTED', 'PREBOOKED', 'BOOKED', 'HIDDEN', "
                "'EXPIRED', 'ENDED', 'CANCELLED', 'REIMBURSED', 'ARCHIVED' or 'DRAFT'"
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
