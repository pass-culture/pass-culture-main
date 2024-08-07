import datetime
import random

import dateutil
import pytest
import time_machine

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


random.seed(12)


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # 1. session
    # 2. user
    # 3. collective_offer
    # 4. collective_offer_template
    # 5. national_program
    expected_num_queries = 5

    def test_one_simple_collective_offer(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, offerId=1, institution=institution, nationalProgramId=national_program.id
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/collective/offers")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == offer.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is False
        assert response_json[0]["educationalInstitution"]["name"] == institution.name
        assert response_json[0]["imageCredit"] is None
        assert response_json[0]["imageUrl"] is None
        assert response_json[0]["nationalProgram"] == {"id": national_program.id, "name": national_program.name}

    @time_machine.travel("2024-06-1")
    def test_one_simple_collective_offer_dates(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, offerId=1, institution=institution, nationalProgramId=national_program.id
        )
        next_week = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        in_two_weeks = datetime.datetime.utcnow() + datetime.timedelta(days=14)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, stockId=1, startDatetime=next_week, endDatetime=in_two_weeks
        )

        client = client.with_session_auth(user.email)

        # When
        queries = 0
        queries += 1  # load session
        queries += 1  # load user
        queries += 1  # load collective offers
        queries += 1  # load collective offers template
        queries += 1  # load national program

        with assert_num_queries(queries):
            response = client.get("/collective/offers")

            # Then
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
        # Given
        user = users_factories.UserFactory()

        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=125),
            bookingLimitDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=125),
        )
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock,
            teacher=educational_factories.EducationalRedactorFactory(),
            isActive=True,
        )
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["isActive"] is False
        assert response_json[0]["status"] == "INACTIVE"

    def test_get_passed_booking_limit_datetime_not_beginning_datetime(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=5),
            bookingLimitDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            collectiveOffer__venue=venue,
            collectiveOffer__isActive=False,
        )

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers?status=INACTIVE")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert len(response_json) == 1
        assert response_json[0]["status"] == "INACTIVE"
        assert response_json[0]["id"] == stock.collectiveOffer.id

    def test_if_collective_offer_is_public_api(self, client):
        # Given
        provider = providers_factories.ProviderFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.CollectiveOfferFactory(venue=venue, offerId=1, institution=institution, provider=provider)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers")
            assert response.status_code == 200

    def test_one_simple_collective_offer_template(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferTemplateFactory(venue=venue, offerId=1)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == offer.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is True
        assert response_json[0]["imageCredit"] is None
        assert response_json[0]["imageUrl"] is None

    def test_mix_collective_offer_and_template(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            dateCreated=datetime.datetime.utcnow(),
            offerId=1,
            imageId="00000125999998",
            imageCredit="offer",
        )

        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            dateCreated=datetime.datetime.utcnow(),
            offerId=2,
            imageId="00000125999999",
            imageCredit="template",
        )

        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 2
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == offer.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is False
        assert response_json[0]["imageCredit"] == "offer"
        assert response_json[0]["imageUrl"] == f"http://localhost/storage/thumbs/collectiveoffer/{offer.imageId}.jpg"

        assert response_json[1]["venue"]["id"] == venue.id
        assert response_json[1]["id"] == template.id
        assert len(response_json[1]["stocks"]) == 1
        assert response_json[1]["isShowcase"] is True
        assert response_json[1]["imageCredit"] == "template"
        assert (
            response_json[1]["imageUrl"]
            == f"http://localhost/storage/thumbs/collectiveoffertemplate/{template.imageId}.jpg"
        )

    def test_one_collective_offer_with_template_id(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        template = educational_factories.CollectiveOfferTemplateFactory()
        educational_factories.CollectiveOfferFactory(venue=venue, template=template)

        # When
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["templateId"] == str(template.id)

    @pytest.mark.skip(reason="Too long to be played each time")
    def test_max_offers_limit_mix_template(self, client):
        # Given
        offers = []
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        for i in range(510):
            if random.randrange(10) % 2:
                offer = educational_factories.CollectiveOfferFactory(
                    venue=venue, dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=i), offerId=1
                )
                educational_factories.CollectiveStockFactory(collectiveOffer=offer)
            else:
                offer = educational_factories.CollectiveOfferTemplateFactory(
                    venue=venue, dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=i), offerId=2
                )

            offers.append(offer)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.with_session_auth(user.email).get("/collective/offers")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 501
        for i in range(501):
            assert response_json[i]["id"] == offers[-(i + 1)].id
            assert response_json[i]["isShowcase"] != isinstance(offers[-(i + 1)], educational_models.CollectiveOffer)

    def test_mix_collective_offer_and_template_no_user(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=2
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 0

    def test_with_date_filters(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )

        other_offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=2
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__venue=venue,
            collectiveOffer__dateCreated=datetime.datetime.utcnow(),
            collectiveOffer__offerId=other_offer.id,
            beginningDatetime=datetime.datetime(2022, 8, 10),
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=other_offer.id
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            stockId=1,
            beginningDatetime=datetime.datetime(2022, 10, 10),
        )

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers?periodBeginningDate=2022-10-10&periodEndingDate=2022-10-11")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == offer.id

    def test_with_status_filters(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer_booked = educational_factories.CollectiveOfferFactory(venue=venue, dateCreated=datetime.datetime.utcnow())
        stock_booked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_booked, dateCreated=datetime.datetime.utcnow()
        )
        _booking_confirmed = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_booked,
            dateCreated=datetime.datetime.utcnow(),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )

        offer_prebooked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow()
        )
        stock_prebooked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_prebooked, dateCreated=datetime.datetime.utcnow()
        )
        _booking_cancelled = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        _booking_pending = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=datetime.datetime.utcnow(),
            status=educational_models.CollectiveBookingStatus.PENDING,
        )

        client = client.with_session_auth(user.email)

        # When

        with assert_num_queries(4):
            # Fetch the session
            # Fetch the user
            # Select collective_offers
            # Select collective_offers_templates
            response_booked = client.get("/collective/offers?status=BOOKED")

        response_prebooked = client.get("/collective/offers?status=PREBOOKED")

        # Then
        assert response_booked.status_code == 200

        response_booked_json = response_booked.json
        assert isinstance(response_booked_json, list)
        assert [offer["id"] for offer in response_booked_json] == [offer_booked.id]

        # Then
        assert response_prebooked.status_code == 200

        response_prebooked_json = response_prebooked.json
        assert isinstance(response_prebooked_json, list)
        assert [offer["id"] for offer in response_prebooked_json] == [offer_prebooked.id]

    def test_with_multiple_status_filters(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offer_not_booked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow()
        )
        _stock_not_booked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_not_booked, dateCreated=datetime.datetime.utcnow()
        )

        offer_booked = educational_factories.CollectiveOfferFactory(venue=venue, dateCreated=datetime.datetime.utcnow())
        stock_booked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_booked, dateCreated=datetime.datetime.utcnow()
        )
        _booking_confirmed = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_booked,
            dateCreated=datetime.datetime.utcnow(),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )

        offer_prebooked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow()
        )
        stock_prebooked = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_prebooked, dateCreated=datetime.datetime.utcnow()
        )
        _booking_cancelled = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        _booking_pending = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_prebooked,
            dateCreated=datetime.datetime.utcnow(),
            status=educational_models.CollectiveBookingStatus.PENDING,
        )

        client = client.with_session_auth(user.email)

        # When

        with assert_num_queries(4):
            # Fetch the session
            # Fetch the user
            # Select collective_offers
            # Select collective_offers_templates
            response = client.get("/collective/offers?status=BOOKED&status=PREBOOKED")

            # Then
            assert response.status_code == 200

            response_json = response.json
            assert isinstance(response_json, list)
            assert {offer["id"] for offer in response_json} == {offer_booked.id, offer_prebooked.id}

    def test_select_only_collective_offer(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, offerId=1)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)
        educational_factories.CollectiveOfferTemplateFactory(venue=venue, offerId=1)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(3):  # user + session + collective_offers
            response = client.get("/collective/offers?collectiveOfferType=offer")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == offer.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is False

    def test_select_only_collective_offer_template(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )
        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=2
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(3):  # session + user + collective_offer_template
            response = client.get("/collective/offers?collectiveOfferType=template")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == template.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is True

    def test_offers_with_empty_string_subcategory_instead_of_none(self, client):
        """Test that a list of offers can contain one that has a legal
        but unexpected subcategory (empty string instead if none).
        """
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, subcategoryId="")
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        client = client.with_session_auth(user.email)
        with assert_num_queries(self.expected_num_queries - 1):  # - national_program
            response = client.get("/collective/offers")
            assert response.status_code == 200

        response_json = response.json
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["subcategoryId"] is None

    def test_offers_sorting(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        # Fresher
        offer_created_10_days_ago = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=10)
        )

        # Oldest
        offer_created_30_days_ago = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=30)
        )

        # Older
        offer_created_20_days_ago = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=20)
        )

        # Archived offer
        archived_offer = educational_factories.CollectiveOfferFactory(
            dateArchived=datetime.datetime.utcnow(),
            venue=venue,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=15),
        )

        # average template
        template_created_14_days_ago = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=14)
        )

        # Offer that needs confirmation
        offer_requiring_attention = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=35)
        )
        futur = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=futur, collectiveOffer=offer_requiring_attention
        )
        _booking = educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        # Published offer that needs urgent confirmation
        published_offer_requiring_urgent_attention = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=35)
        )
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=tomorrow, collectiveOffer=published_offer_requiring_urgent_attention
        )

        # Offer that needs urgent confirmation
        offer_requiring_urgent_attention = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=35)
        )
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=tomorrow, collectiveOffer=offer_requiring_urgent_attention
        )
        _booking = educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        # Offer already booked
        offer_booked = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=34)
        )
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=tomorrow, collectiveOffer=offer_booked
        )
        _booking = educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)

        # Offer that needs confirmation that can be waited
        offer_requiring_not_urgent_confirmation = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=35)
        )
        # 10 days > 7 days
        futur_far = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=futur_far, collectiveOffer=offer_requiring_not_urgent_confirmation
        )
        _booking = educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)

        ids = [o["id"] for o in response_json]

        # in first the most fresh
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


@pytest.mark.usefixtures("db_session")
class Return400Test:
    def test_return_error_when_status_is_wrong(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        # When
        client = client.with_session_auth(user.email)
        with assert_num_queries(2):  # user + session
            response = client.get("/collective/offers?status=NOT_A_VALID_STATUS")
            assert response.status_code == 400

        msg = response.json["status"][0]
        assert msg.startswith("value is not a valid enumeration member")

        for value in CollectiveOfferDisplayedStatus:
            assert value.name in msg
