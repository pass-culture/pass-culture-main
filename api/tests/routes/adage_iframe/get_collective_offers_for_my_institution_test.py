from datetime import datetime
from datetime import timedelta

import pytest
from flask import url_for

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


UAI = "1234UAI"
EMAIL = "toto@mail.com"


@pytest.fixture(name="eac_client")
def eac_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai=UAI)


@pytest.fixture(name="redactor")
def redactor_fixture():
    return educational_factories.EducationalRedactorFactory(email=EMAIL)


class CollectiveOfferTest:
    # 1. fetch redactor
    # 2. fetch collective offer and related data
    # 3. fetch the offerVenue's details (Venue)
    num_queries = 3

    def test_get_collective_offer_for_my_institution(self, eac_client, redactor):
        START_DATE = datetime.today() + timedelta(days=3)
        venue = offerers_factories.VenueFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId=UAI)
        stocks = educational_factories.CollectiveStockFactory.create_batch(
            3,
            startDatetime=START_DATE,
            collectiveOffer__institution=institution,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )
        # this archived offer should not appear in the result
        stocks[2].collectiveOffer.dateArchived = datetime.utcnow() - timedelta(days=1)
        stocks[2].collectiveOffer.isActive = False

        # cancelled booking should not appear in the result
        stock_with_cancelled_booking = educational_factories.CollectiveStockFactory(
            startDatetime=START_DATE,
            collectiveOffer__institution=institution,
            collectiveOffer__offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
        )
        educational_factories.CancelledCollectiveBookingFactory(collectiveStock=stock_with_cancelled_booking)

        dst = url_for("adage_iframe.get_collective_offers_for_my_institution")

        with assert_num_queries(self.num_queries):
            response = eac_client.get(dst)

        assert response.status_code == 200
        response_data = sorted(response.json["collectiveOffers"], key=lambda offer: offer["id"])
        assert len(response_data) == 2, response_data

        assert response_data[0]["id"] == stocks[0].collectiveOffer.id
        assert response_data[0]["educationalInstitution"]["id"] == institution.id
        assert response_data[0]["stock"]["id"] == stocks[0].id
        venue = stocks[0].collectiveOffer.venue
        assert response_data[0]["venue"] == {
            "adageId": None,
            "address": "1 boulevard Poissonnière",
            "city": "Paris",
            "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
            "distance": None,
            "id": venue.id,
            "imgUrl": None,
            "managingOfferer": {"name": venue.managingOfferer.name},
            "name": venue.name,
            "postalCode": "75002",
            "departmentCode": "75",
            "publicName": venue.publicName,
        }

        assert response_data[1]["id"] == stocks[1].collectiveOffer.id
        assert response_data[1]["educationalInstitution"]["id"] == institution.id
        assert response_data[1]["stock"]["id"] == stocks[1].id
        venue = stocks[1].collectiveOffer.venue
        assert response_data[1]["venue"] == {
            "adageId": None,
            "address": "1 boulevard Poissonnière",
            "city": "Paris",
            "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
            "distance": None,
            "id": venue.id,
            "imgUrl": None,
            "managingOfferer": {"name": venue.managingOfferer.name},
            "name": venue.name,
            "postalCode": "75002",
            "departmentCode": "75",
            "publicName": venue.publicName,
        }

    def test_location_address_venue(self, eac_client):
        institution = educational_factories.EducationalInstitutionFactory(institutionId=UAI)
        venue = offerers_factories.VenueFactory()
        educational_factories.PublishedCollectiveOfferFactory(
            venue=venue,
            locationType=models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddressId,
            interventionArea=None,
            institution=institution,
        )

        ban_id = venue.offererAddress.address.banId
        offer_address_id = venue.offererAddressId
        db.session.expunge_all()

        dst = url_for("adage_iframe.get_collective_offers_for_my_institution")
        num_queries = 1  # fetch collective offer and related data
        num_queries += 1  # fetch redactor
        with assert_num_queries(num_queries):
            response = eac_client.get(dst)

        assert response.status_code == 200
        [result] = response.json["collectiveOffers"]
        response_location = result["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["address"] is not None
        assert response_location["address"]["id_oa"] == offer_address_id
        assert response_location["address"]["isLinkedToVenue"] is True
        assert response_location["address"]["banId"] == ban_id
