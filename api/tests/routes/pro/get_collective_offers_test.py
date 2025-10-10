import datetime

import dateutil
import pytest
import time_machine

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.testing import get_serialized_address
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # 1. session
    # 2. user
    # 3. collective_offer
    # 4. collective_offer_template
    expected_num_queries = 4

    def test_one_simple_collective_offer(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, institution=institution, nationalProgramId=national_program.id
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer.id,
                "allowedActions": [
                    "CAN_EDIT_DETAILS",
                    "CAN_EDIT_DATES",
                    "CAN_EDIT_DISCOUNT",
                    "CAN_DUPLICATE",
                    "CAN_ARCHIVE",
                ],
                "booking": None,
                "dates": {
                    "start": offer.collectiveStock.startDatetime.isoformat() + "Z",
                    "end": offer.collectiveStock.endDatetime.isoformat() + "Z",
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
                    "address": None,
                    "locationComment": None,
                    "locationType": "TO_BE_DEFINED",
                },
                "hasBookingLimitDatetimesPassed": False,
                "name": offer.name,
                "stocks": [
                    {
                        "hasBookingLimitDatetimePassed": offer.collectiveStock.hasBookingLimitDatetimePassed,
                        "remainingQuantity": 0,
                        "bookingLimitDatetime": offer.collectiveStock.bookingLimitDatetime.isoformat() + "Z",
                        "startDatetime": offer.collectiveStock.startDatetime.isoformat() + "Z",
                        "endDatetime": offer.collectiveStock.endDatetime.isoformat() + "Z",
                        "price": float(offer.collectiveStock.price),
                        "numberOfTickets": offer.collectiveStock.numberOfTickets,
                    }
                ],
                "isShowcase": False,
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
                "displayedStatus": "PUBLISHED",
                "isActive": True,
                "isEducational": True,
            }
        ]

    def test_one_collective_offer_location_school(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        educational_factories.CollectiveOfferOnSchoolLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == {"address": None, "locationComment": None, "locationType": "SCHOOL"}

    def test_one_collective_offer_location_venue_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = educational_factories.CollectiveOfferOnAddressVenueLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=venue.common_name, is_linked_to_venue=True
        )

    def test_one_collective_offer_location_other_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = educational_factories.CollectiveOfferOnOtherAddressLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=offer.offererAddress.label, is_linked_to_venue=False
        )

    @time_machine.travel("2024-06-1")
    def test_one_simple_collective_offer_dates(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, institution=institution, nationalProgramId=national_program.id
        )
        next_week = date_utils.get_naive_utc_now() + datetime.timedelta(days=7)
        in_two_weeks = date_utils.get_naive_utc_now() + datetime.timedelta(days=14)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=next_week, endDatetime=in_two_weeks
        )

        client = client.with_session_auth(user.email)

        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")

            assert response.status_code == 200
            response_json = response.json
            assert isinstance(response_json, list)
            assert len(response_json) == 1
            assert len(response_json[0]["stocks"]) == 1
            stock = response_json[0]["stocks"][0]

            startDatetime = dateutil.parser.parse(stock["startDatetime"]).date()
            assert startDatetime == datetime.date(2024, 6, 8)
            endDatetime = dateutil.parser.parse(stock["endDatetime"]).date()
            assert endDatetime == datetime.date(2024, 6, 15)

            dates_json = response_json[0]["dates"]
            assert isinstance(dates_json, dict)
            start = dateutil.parser.parse(dates_json["start"]).date()
            assert start == datetime.date(2024, 6, 8)
            end = dateutil.parser.parse(dates_json["end"]).date()
            assert end == datetime.date(2024, 6, 15)

    def test_one_inactive_offer(self, client):
        user = users_factories.UserFactory()

        stock = educational_factories.CollectiveStockFactory(
            startDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=125),
            bookingLimitDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=125),
        )
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock,
            teacher=educational_factories.EducationalRedactorFactory(),
            isActive=False,
        )
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["isActive"] is False

    def test_get_passed_booking_limit_datetime_not_beginning_datetime(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=5),
            bookingLimitDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=5),
            collectiveOffer__venue=venue,
        )

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?status=EXPIRED")
            assert response.status_code == 200

        response_json = response.json
        assert len(response_json) == 1
        assert response_json[0]["displayedStatus"] == "EXPIRED"
        assert response_json[0]["id"] == stock.collectiveOffer.id

    def test_if_collective_offer_is_public_api(self, client):
        provider = providers_factories.ProviderFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.CollectiveOfferFactory(venue=venue, institution=institution, provider=provider)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

    def test_one_simple_collective_offer_template(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferTemplateFactory(venue=venue)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        assert response.json == [
            {
                "allowedActions": [
                    "CAN_EDIT_DETAILS",
                    "CAN_ARCHIVE",
                    "CAN_CREATE_BOOKABLE_OFFER",
                    "CAN_HIDE",
                ],
                "booking": None,
                "dates": {
                    "start": offer.dateRange.lower.isoformat() + "Z",
                    "end": offer.dateRange.upper.isoformat() + "Z",
                },
                "displayedStatus": "PUBLISHED",
                "educationalInstitution": None,
                "hasBookingLimitDatetimesPassed": False,
                "id": offer.id,
                "imageUrl": None,
                "isActive": True,
                "isEducational": True,
                "isShowcase": True,
                "location": {
                    "address": None,
                    "locationComment": None,
                    "locationType": "TO_BE_DEFINED",
                },
                "name": offer.name,
                "stocks": [
                    {
                        "bookingLimitDatetime": None,
                        "endDatetime": None,
                        "hasBookingLimitDatetimePassed": False,
                        "numberOfTickets": None,
                        "price": None,
                        "remainingQuantity": 1,
                        "startDatetime": None,
                    },
                ],
                "venue": {
                    "departementCode": venue.offererAddress.address.departmentCode,
                    "id": venue.id,
                    "isVirtual": venue.isVirtual,
                    "name": venue.name,
                    "offererName": venue.managingOfferer.name,
                    "publicName": venue.publicName,
                },
            }
        ]

    def test_one_collective_offer_template_location_school(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        educational_factories.CollectiveOfferTemplateOnSchoolLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == {"address": None, "locationComment": None, "locationType": "SCHOOL"}

    def test_one_collective_offer_template_location_venue_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = educational_factories.CollectiveOfferTemplateOnAddressVenueLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=venue.common_name, is_linked_to_venue=True
        )

    def test_one_collective_offer_template_location_other_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = educational_factories.CollectiveOfferTemplateOnOtherAddressLocationFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        [offer_json] = response.json
        assert offer_json["location"] == get_serialized_address(
            offerer_address=offer.offererAddress, label=offer.offererAddress.label, is_linked_to_venue=False
        )

    def test_mix_collective_offer_and_template(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            dateCreated=date_utils.get_naive_utc_now(),
            imageId="00000125999998",
        )

        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            dateCreated=date_utils.get_naive_utc_now(),
            imageId="00000125999999",
        )

        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 2
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == offer.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is False
        assert response_json[0]["imageUrl"] == f"http://localhost/storage/thumbs/collectiveoffer/{offer.imageId}.jpg"

        assert response_json[1]["venue"]["id"] == venue.id
        assert response_json[1]["id"] == template.id
        assert len(response_json[1]["stocks"]) == 1
        assert response_json[1]["isShowcase"] is True
        assert (
            response_json[1]["imageUrl"]
            == f"http://localhost/storage/thumbs/collectiveoffertemplate/{template.imageId}.jpg"
        )

    def test_mix_collective_offer_and_template_no_user(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            dateCreated=date_utils.get_naive_utc_now(),
        )
        educational_factories.CollectiveOfferTemplateFactory(venue=venue, dateCreated=date_utils.get_naive_utc_now())
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 0

    def test_with_date_filters(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, dateCreated=date_utils.get_naive_utc_now())

        educational_factories.CollectiveOfferFactory(venue=venue, dateCreated=date_utils.get_naive_utc_now())
        educational_factories.CollectiveStockFactory(
            collectiveOffer__venue=venue,
            collectiveOffer__dateCreated=date_utils.get_naive_utc_now(),
            startDatetime=datetime.datetime(2022, 8, 10),
        )
        educational_factories.CollectiveOfferTemplateFactory(venue=venue, dateCreated=date_utils.get_naive_utc_now())
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=datetime.datetime(2022, 10, 10)
        )

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?periodBeginningDate=2022-10-10&periodEndingDate=2022-10-11")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == offer.id

    def test_with_status_filters(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer_booked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now()
        )
        stock_booked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_booked, dateCreated=date_utils.get_naive_utc_now()
        )
        _booking_confirmed = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_booked,
            dateCreated=date_utils.get_naive_utc_now(),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )

        offer_prebooked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now()
        )
        stock_prebooked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_prebooked, dateCreated=date_utils.get_naive_utc_now()
        )
        _booking_cancelled = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        _booking_pending = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=date_utils.get_naive_utc_now(),
            status=educational_models.CollectiveBookingStatus.PENDING,
        )

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response_booked = client.get("/collective/offers?status=BOOKED")

        response_prebooked = client.get("/collective/offers?status=PREBOOKED")

        assert response_booked.status_code == 200

        response_booked_json = response_booked.json
        assert isinstance(response_booked_json, list)
        assert [offer["id"] for offer in response_booked_json] == [offer_booked.id]

        assert response_prebooked.status_code == 200

        response_prebooked_json = response_prebooked.json
        assert isinstance(response_prebooked_json, list)
        assert [offer["id"] for offer in response_prebooked_json] == [offer_prebooked.id]

    def test_with_multiple_status_filters(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer_not_booked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now()
        )
        _stock_not_booked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_not_booked, dateCreated=date_utils.get_naive_utc_now()
        )

        offer_booked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now()
        )
        stock_booked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_booked, dateCreated=date_utils.get_naive_utc_now()
        )
        _booking_confirmed = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_booked,
            dateCreated=date_utils.get_naive_utc_now(),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )

        offer_prebooked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now()
        )
        stock_prebooked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_prebooked, dateCreated=date_utils.get_naive_utc_now()
        )
        _booking_cancelled = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        _booking_pending = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=date_utils.get_naive_utc_now(),
            status=educational_models.CollectiveBookingStatus.PENDING,
        )

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?status=BOOKED&status=PREBOOKED")

            assert response.status_code == 200

            response_json = response.json
            assert isinstance(response_json, list)

        assert {offer["id"] for offer in response_json} == {offer_booked.id, offer_prebooked.id}

    def test_select_only_collective_offer(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)
        educational_factories.CollectiveOfferTemplateFactory(venue=venue)

        client = client.with_session_auth(user.email)
        with assert_num_queries(3):  # user + session + collective_offers
            response = client.get("/collective/offers?collectiveOfferType=offer")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == offer.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is False

    def test_select_only_collective_offer_template(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, dateCreated=date_utils.get_naive_utc_now())
        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now()
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        client = client.with_session_auth(user.email)
        with assert_num_queries(3):
            response = client.get("/collective/offers?collectiveOfferType=template")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == template.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is True

    def test_offers_sorting(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer_created_10_days_ago = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=10)
        )

        offer_created_30_days_ago = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=30)
        )

        offer_created_20_days_ago = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=20)
        )

        archived_offer = educational_factories.CollectiveOfferFactory(
            dateArchived=date_utils.get_naive_utc_now(),
            venue=venue,
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=15),
        )

        template_created_14_days_ago = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=14)
        )

        offer_requiring_attention = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=35)
        )
        futur = date_utils.get_naive_utc_now() + datetime.timedelta(days=5)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=futur, collectiveOffer=offer_requiring_attention
        )
        _booking = educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        published_offer_requiring_urgent_attention = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=35)
        )
        tomorrow = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=tomorrow, collectiveOffer=published_offer_requiring_urgent_attention
        )

        offer_requiring_urgent_attention = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=35)
        )
        tomorrow = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=tomorrow, collectiveOffer=offer_requiring_urgent_attention
        )
        _booking = educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        offer_booked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=34)
        )
        tomorrow = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=tomorrow, collectiveOffer=offer_booked
        )
        _booking = educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)

        offer_requiring_not_urgent_confirmation = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=35)
        )
        futur_far = date_utils.get_naive_utc_now() + datetime.timedelta(days=10)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=futur_far, collectiveOffer=offer_requiring_not_urgent_confirmation
        )
        _booking = educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        response = client.with_session_auth(user.email).get("/collective/offers")

        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)

        ids = [o["id"] for o in response_json]

        assert ids == [
            offer_requiring_urgent_attention.id,
            published_offer_requiring_urgent_attention.id,
            offer_requiring_attention.id,
            offer_created_10_days_ago.id,
            template_created_14_days_ago.id,
            offer_created_20_days_ago.id,
            offer_created_30_days_ago.id,
            offer_booked.id,
            offer_requiring_not_urgent_confirmation.id,
            archived_offer.id,
        ]

    def test_collective_offers_only_sorting(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        # IMPORTANT: When offers have the same urgency score, they are sorted by dateCreated (most recent first)

        archived_offer = educational_factories.CollectiveOfferFactory(
            dateArchived=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            venue=venue,
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=15),
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=archived_offer)

        old_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=30)
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer=old_offer, bookingLimitDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=20)
        )

        recent_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=5)
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer=recent_offer,
            bookingLimitDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=15),
        )

        booked_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=10)
        )
        stock_booked = educational_factories.CollectiveStockFactory(
            collectiveOffer=booked_offer,
            bookingLimitDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=5),
        )
        educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock_booked)

        # Not urgent (booking limit > 7 days)
        pending_not_urgent_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=12)
        )
        stock_pending_not_urgent = educational_factories.CollectiveStockFactory(
            collectiveOffer=pending_not_urgent_offer,
            bookingLimitDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=10),
        )
        educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock_pending_not_urgent)

        # Medium urgency (booking limit between 2-7 days)
        pending_medium_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=8)
        )
        stock_pending_medium = educational_factories.CollectiveStockFactory(
            collectiveOffer=pending_medium_offer,
            bookingLimitDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=4),
        )
        educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock_pending_medium)

        # Expiring soon, created more recently than pending_urgent_offer
        expiring_soon_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=6)
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer=expiring_soon_offer,
            bookingLimitDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(hours=20),
        )

        # Urgent, created less recently than expiring_soon_offer
        pending_urgent_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=7)
        )
        stock_pending_urgent = educational_factories.CollectiveStockFactory(
            collectiveOffer=pending_urgent_offer,
            bookingLimitDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=1),
        )
        educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock_pending_urgent)

        response = client.with_session_auth(user.email).get("/collective/offers?collectiveOfferType=offer")

        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 8

        ids = [o["id"] for o in response_json]

        # Sorting logic:
        # 1. Non-archived offers come before archived ones
        # 2. Offers with PREBOOKED or PUBLISHED status and booking limit < 7 days are prioritized by urgency
        # 3. When same urgency, sorted by dateCreated (most recent first)
        # 4. Archived offers are always last
        assert ids == [
            expiring_soon_offer.id,
            pending_urgent_offer.id,
            pending_medium_offer.id,
            recent_offer.id,
            booked_offer.id,
            pending_not_urgent_offer.id,
            old_offer.id,
            archived_offer.id,
        ]

    @pytest.mark.parametrize(
        "status",
        set(educational_models.CollectiveOfferDisplayedStatus)
        - {educational_models.CollectiveOfferDisplayedStatus.HIDDEN},
    )
    def test_each_status_filter(self, client, status):
        offer = educational_factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # Add an offer with another status that will not be present in the result
        other_status = next((s for s in educational_models.CollectiveOfferDisplayedStatus if s != status))
        educational_factories.create_collective_offer_by_status(status=other_status, venue=offer.venue)

        client = client.with_session_auth(email="user@example.com")
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/collective/offers?status={status.value}")

        [response_offer] = response.json
        assert response_offer["id"] == offer.id

    def test_status_filter_hidden(self, client):
        offer = educational_factories.create_collective_offer_by_status(
            status=educational_models.CollectiveOfferDisplayedStatus.HIDDEN
        )
        offer_template = educational_factories.create_collective_offer_template_by_status(
            status=educational_models.CollectiveOfferDisplayedStatus.HIDDEN, venue=offer.venue
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?status=HIDDEN")

        [response_offer] = response.json
        assert response_offer["id"] == offer_template.id

    @pytest.mark.parametrize("status", educational_models.COLLECTIVE_OFFER_TEMPLATE_STATUSES)
    def test_each_status_filter_template(self, client, status):
        offer = educational_factories.create_collective_offer_template_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # Add an offer with another status that will not be present in the result
        other_status = next((s for s in educational_models.COLLECTIVE_OFFER_TEMPLATE_STATUSES if s != status))
        educational_factories.create_collective_offer_template_by_status(other_status, venue=offer.venue)

        client = client.with_session_auth(email="user@example.com")
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/collective/offers?status={status.value}")

        [response_offer] = response.json
        assert response_offer["id"] == offer.id

    def test_filter_location(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        oa = offerers_factories.OffererAddressFactory()
        offer_school = educational_factories.CollectiveOfferOnSchoolLocationFactory(venue=venue)
        offer_address = educational_factories.CollectiveOfferOnOtherAddressLocationFactory(
            venue=venue, offererAddress=oa
        )
        educational_factories.CollectiveOfferOnOtherAddressLocationFactory(venue=venue)
        offer_to_be_defined = educational_factories.CollectiveOfferOnToBeDefinedLocationFactory(venue=venue)

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?locationType=SCHOOL")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_school.id

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?locationType=TO_BE_DEFINED")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_to_be_defined.id

        oa_id = oa.id
        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/collective/offers?locationType=ADDRESS&offererAddressId={oa_id}")

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer_address.id


@pytest.mark.usefixtures("db_session")
class Return400Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # rollback

    def test_return_error_when_status_is_wrong(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?status=NOT_A_VALID_STATUS")
            assert response.status_code == 400

        assert response.json == {
            "status.0": [
                "value is not a valid enumeration member; permitted: 'PUBLISHED', "
                "'UNDER_REVIEW', 'REJECTED', 'PREBOOKED', 'BOOKED', 'HIDDEN', "
                "'EXPIRED', 'ENDED', 'CANCELLED', 'REIMBURSED', 'ARCHIVED', "
                "'DRAFT'",
            ]
        }

    def test_filter_location_type_error(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?locationType=BLOUP")

        assert response.status_code == 400
        assert response.json == {
            "locationType": [
                "value is not a valid enumeration member; permitted: 'SCHOOL', 'ADDRESS', 'TO_BE_DEFINED'",
            ]
        }

    def test_filter_offerer_address_not_accepted(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers?locationType=SCHOOL&offererAddressId=1")

        assert response.status_code == 400
        assert response.json == {"__root__": ["Cannot provide offerer_address_id when location_type is not ADDRESS"]}
