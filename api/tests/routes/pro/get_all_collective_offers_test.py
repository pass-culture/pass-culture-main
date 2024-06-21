import datetime
import random

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
import pcapi.core.offerers.factories as offerer_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


random.seed(12)


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_one_simple_collective_offer(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, offerId=1, institution=institution, nationalProgramId=national_program.id
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
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
        offerer_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        # When

        response = client.with_session_auth(email=user.email).get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["isActive"] is False
        assert response_json[0]["status"] == "INACTIVE"

    def test_get_passed_booking_limit_datetime_not_beginning_datetime(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=5),
            bookingLimitDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            collectiveOffer__venue=venue,
        )

        # When
        response = client.with_session_auth(user.email).get("/collective/offers?status=INACTIVE")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert len(response_json) == 1
        assert response_json[0]["status"] == "INACTIVE"
        assert response_json[0]["id"] == stock.collectiveOffer.id

    def test_if_collective_offer_is_public_api(self, client):
        # Given
        provider = providers_factories.ProviderFactory()
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.CollectiveOfferFactory(venue=venue, offerId=1, institution=institution, provider=provider)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers")

        # Then
        assert response.status_code == 200

    def test_one_simple_collective_offer_template(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferTemplateFactory(venue=venue, offerId=1)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
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
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
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
        response = client.with_session_auth(user.email).get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 2
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == template.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is True
        assert response_json[0]["imageCredit"] == "template"
        assert (
            response_json[0]["imageUrl"]
            == f"http://localhost/storage/thumbs/collectiveoffertemplate/{template.imageId}.jpg"
        )
        assert response_json[1]["venue"]["id"] == venue.id
        assert response_json[1]["id"] == offer.id
        assert len(response_json[1]["stocks"]) == 1
        assert response_json[1]["isShowcase"] is False
        assert response_json[1]["imageCredit"] == "offer"
        assert response_json[1]["imageUrl"] == f"http://localhost/storage/thumbs/collectiveoffer/{offer.imageId}.jpg"

    def test_one_collective_offer_with_template_id(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        template = educational_factories.CollectiveOfferTemplateFactory()
        educational_factories.CollectiveOfferFactory(venue=venue, template=template)

        # When
        client = client.with_session_auth(email=user.email)
        response = client.get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["templateId"] == str(template.id)

    @pytest.mark.skip(reason="Too long to be played each time")
    def test_max_offers_limit_mix_template(self, client):
        # Given
        offers = []
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)

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
        response = client.with_session_auth(user.email).get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 501
        for i in range(501):
            assert response_json[i]["id"] == offers[-(i + 1)].id
            assert response_json[i]["isShowcase"] != isinstance(offers[-(i + 1)], educational_models.CollectiveOffer)

    def test_mix_collective_offer_and_template_no_user(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=2
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 0

    def test_with_date_filters(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
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
        response = client.with_session_auth(user.email).get(
            "/collective/offers?periodBeginningDate=2022-10-10&periodEndingDate=2022-10-11"
        )

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == offer.id

    def test_with_status_filters(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)

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
        assert len(response_booked_json) == 1
        assert response_booked_json[0]["id"] == offer_booked.id

        assert response_prebooked.status_code == 200

        response_prebooked_json = response_prebooked.json
        assert isinstance(response_prebooked_json, list)
        assert len(response_prebooked_json) == 1
        assert response_prebooked_json[0]["id"] == offer_prebooked.id

    def test_select_only_collective_offer(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, offerId=1)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)
        educational_factories.CollectiveOfferTemplateFactory(venue=venue, offerId=1)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers?collectiveOfferType=offer")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venue"]["id"] == venue.id
        assert response_json[0]["id"] == offer.id
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["isShowcase"] is False

    def test_select_only_collective_offer_template(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )
        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=2
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers?collectiveOfferType=template")

        # Then
        response_json = response.json
        assert response.status_code == 200
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
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)

        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, subcategoryId="")
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        response = client.with_session_auth(user.email).get("/collective/offers")
        response_json = response.json

        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["subcategoryId"] is None


@pytest.mark.usefixtures("db_session")
class Return400Test:
    def test_return_error_when_status_is_wrong(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)

        # When
        response = client.with_session_auth(user.email).get("/collective/offers?status=NOT_A_VALID_STATUS")

        # Then
        assert response.status_code == 400

        msg = response.json["status"][0]
        assert msg.startswith("value is not a valid enumeration member")

        for value in CollectiveOfferDisplayedStatus:
            assert value.name in msg

    def test_with_multiple_status_filters(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        educational_factories.CollectiveOfferFactory(venue=venue, offerId=1)

        # When
        client = client.with_session_auth(user.email)

        # Fetch the session
        # Fetch the user
        with assert_num_queries(2):
            response = client.get("/collective/offers?status=BOOKED&status=PREBOOKED")

            # Then
            assert response.status_code == 400
