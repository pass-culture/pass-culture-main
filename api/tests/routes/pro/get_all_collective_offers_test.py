import datetime
import random

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerer_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


random.seed(12)


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_one_simple_collective_offer(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(venue=venue, offerId=1, institution=institution)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venueId"] == humanize(venue.id)
        assert response_json[0]["id"] == humanize(offer.id)
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["stocks"][0]["id"] == humanize(stock.id)
        assert response_json[0]["isShowcase"] == False
        assert response_json[0]["educationalInstitution"]["name"] == institution.name
        assert response_json[0]["imageCredit"] == None
        assert response_json[0]["imageUrl"] == None
        assert response_json[0]["isPublicApi"] == False

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
        assert response_json[0]["isActive"] == False
        assert response_json[0]["status"] == "INACTIVE"

    def test_get_passed_booking_limit_datetime_not_beginning_datetime(self, app):
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
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers?status=INACTIVE")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert len(response_json) == 1
        assert response_json[0]["status"] == "INACTIVE"
        assert response_json[0]["id"] == humanize(stock.collectiveOffer.id)

    def test_if_collective_offer_is_public_api(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.CollectiveOfferFactory(venue=venue, offerId=1, institution=institution, isPublicApi=True)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json[0]["isPublicApi"] == True

    def test_one_simple_collective_offer_template(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferTemplateFactory(venue=venue, offerId=1)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venueId"] == humanize(venue.id)
        assert response_json[0]["id"] == humanize(offer.id)
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["stocks"][0]["id"] == ""
        assert response_json[0]["isShowcase"] == True
        assert response_json[0]["imageCredit"] == None
        assert response_json[0]["imageUrl"] == None

    def test_mix_collective_offer_and_template(self, app):
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
            dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=10),
            offerId=2,
            imageId="00000125999999",
            imageCredit="template",
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 2
        assert response_json[0]["venueId"] == humanize(venue.id)
        assert response_json[0]["id"] == humanize(template.id)
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["stocks"][0]["id"] == ""
        assert response_json[0]["isShowcase"] == True
        assert response_json[0]["imageCredit"] == "template"
        assert (
            response_json[0]["imageUrl"]
            == f"http://localhost/storage/thumbs/collectiveoffertemplate/{template.imageId}.jpg"
        )
        assert response_json[1]["venueId"] == humanize(venue.id)
        assert response_json[1]["id"] == humanize(offer.id)
        assert len(response_json[1]["stocks"]) == 1
        assert response_json[1]["stocks"][0]["id"] == humanize(stock.id)
        assert response_json[1]["isShowcase"] == False
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
    def test_max_offers_limit_mix_template(self, app):
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
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 501
        for i in range(501):
            assert response_json[i]["id"] == humanize(offers[-(i + 1)].id)
            assert response_json[i]["isShowcase"] != isinstance(offers[-(i + 1)], educational_models.CollectiveOffer)

    def test_mix_collective_offer_and_template_no_user(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=10), offerId=2
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 0

    def test_with_filters(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer__venue=venue,
            collectiveOffer__dateCreated=datetime.datetime.utcnow(),
            collectiveOffer__offerId=2,
            beginningDatetime=datetime.datetime(2022, 8, 10),
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=10), offerId=2
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            stockId=1,
            beginningDatetime=datetime.datetime(2022, 10, 10),
        )

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers?periodBeginningDate=2022-10-10&periodEndingDate=2022-10-11")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["id"] == humanize(offer.id)

    def test_select_only_collective_offer(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, offerId=1)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)
        educational_factories.CollectiveOfferTemplateFactory(venue=venue, offerId=1)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers?collectiveOfferType=offer")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venueId"] == humanize(venue.id)
        assert response_json[0]["id"] == humanize(offer.id)
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["stocks"][0]["id"] == humanize(stock.id)
        assert response_json[0]["isShowcase"] == False

    def test_select_only_collective_offer_template(self, app):
        # Given
        user = users_factories.UserFactory()
        offerer = offerer_factories.OffererFactory()
        offerer_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerer_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow(), offerId=1
        )
        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, dateCreated=datetime.datetime.utcnow() + datetime.timedelta(days=10), offerId=2
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, stockId=1)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user.email)
        response = client.get("/collective/offers?collectiveOfferType=template")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert isinstance(response_json, list)
        assert len(response_json) == 1
        assert response_json[0]["venueId"] == humanize(venue.id)
        assert response_json[0]["id"] == humanize(template.id)
        assert len(response_json[0]["stocks"]) == 1
        assert response_json[0]["stocks"][0]["id"] == ""
        assert response_json[0]["isShowcase"] == True
