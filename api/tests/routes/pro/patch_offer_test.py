import datetime
import logging
from decimal import Decimal
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.cultural_outreach.factories as cultural_outreach_factories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors import api_adresse
from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.categories import subcategories
from pcapi.core.external.batch import testing as push_testing
from pcapi.core.geography import models as geography_models
from pcapi.core.highlights import factories as highlights_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.reminders import factories as reminders_factories
from pcapi.core.reminders import models as reminders_models
from pcapi.core.search.models import IndexationReason
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    endpoint = "/offers/{offer_id}"

    def test_patch_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            name="L'amie prodigieuse",
            description="Un livre sur l'italie des années 60",
        )
        publication_datetime = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=2)
        booking_allowed_datetime = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)

        data = {
            "name": "Notre part de nuit",
            "mentalDisabilityCompliant": True,
            "publicationDatetime": format_into_utc_date(publication_datetime),
            "bookingAllowedDatetime": format_into_utc_date(booking_allowed_datetime),
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/{offer.id}", json=data)

        assert response.status_code == 200, response.json
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id
        assert response.json["location"]["street"]

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.name == "Notre part de nuit"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert updated_offer.publicationDatetime == publication_datetime
        assert updated_offer.bookingAllowedDatetime == booking_allowed_datetime
        assert not updated_offer.product

    def test_patch_virtual_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            name="New name",
            url="test@test.com",
            offererAddress=None,
            description="description",
        )
        publication_datetime = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=2)
        booking_allowed_datetime = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)

        data = {
            "name": "New name",
            "externalTicketOfficeUrl": "http://example.net",
            "mentalDisabilityCompliant": True,
            "publicationDatetime": format_into_utc_date(publication_datetime),
            "bookingAllowedDatetime": format_into_utc_date(booking_allowed_datetime),
        }
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200, response.json
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id
        assert response.json["venue"]["street"] == venue.offererAddress.address.street

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.externalTicketOfficeUrl == "http://example.net"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.subcategoryId == subcategories.ABO_PLATEFORME_VIDEO.id
        assert updated_offer.publicationDatetime == publication_datetime
        assert updated_offer.bookingAllowedDatetime == booking_allowed_datetime
        assert not updated_offer.product

    @time_machine.travel(datetime.datetime(2025, 6, 24, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "initial_publication_datetime,request_publication_datetime,final_publication_datetime,response_publication_datetime",
        [
            # update publicationDatetime
            (
                datetime.datetime(2025, 6, 26),
                "2025-06-28T14:30:00+02:00",
                datetime.datetime(2025, 6, 28, 12, 30, tzinfo=datetime.UTC),
                "2025-06-28T12:30:00Z",
            ),
            (
                None,
                "2025-06-28T14:30:00Z",
                datetime.datetime(2025, 6, 28, 14, 30, tzinfo=datetime.UTC),
                "2025-06-28T14:30:00Z",
            ),
            # publish offer now
            (
                datetime.datetime(2025, 6, 26),
                "now",
                datetime.datetime(2025, 6, 24, tzinfo=datetime.UTC),
                "2025-06-24T00:00:00Z",
            ),
            # unpublish offer
            (datetime.datetime(2025, 6, 26), None, None, None),
        ],
    )
    def test_patch_offer_publication_datetime(
        self,
        client,
        initial_publication_datetime,
        request_publication_datetime,
        final_publication_datetime,
        response_publication_datetime,
    ):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            name="New name",
            url="test@test.com",
            description="description",
            publicationDatetime=initial_publication_datetime,
            offererAddress=None,
        )

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id),
            json={"publicationDatetime": request_publication_datetime},
        )

        assert response.status_code == 200
        assert response.json["publicationDatetime"] == response_publication_datetime

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.publicationDatetime == final_publication_datetime

    @time_machine.travel(datetime.datetime(2025, 6, 24, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "initial_booking_allowed_datetime,request_booking_allowed_datetime,final_booking_allowed_datetime,response_booking_allowed_datetime",
        [
            # update bookingAllowedDatetime
            (
                datetime.datetime(2025, 6, 26),
                "2025-06-28T14:30:00+02:00",
                datetime.datetime(2025, 6, 28, 12, 30, tzinfo=datetime.UTC),
                "2025-06-28T12:30:00Z",
            ),
            (
                None,
                "2025-06-28T14:30:00Z",
                datetime.datetime(2025, 6, 28, 14, 30, tzinfo=datetime.UTC),
                "2025-06-28T14:30:00Z",
            ),
            # unset bookingAllowedDatetime
            (datetime.datetime(2025, 6, 26), None, None, None),
        ],
    )
    def test_patch_offer_booking_allowed_datetime(
        self,
        client,
        initial_booking_allowed_datetime,
        request_booking_allowed_datetime,
        final_booking_allowed_datetime,
        response_booking_allowed_datetime,
    ):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            name="New name",
            url="test@test.com",
            description="description",
            publicationDatetime=datetime.datetime(2025, 6, 23),
            bookingAllowedDatetime=initial_booking_allowed_datetime,
            offererAddress=None,
        )

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id),
            json={"bookingAllowedDatetime": request_booking_allowed_datetime},
        )

        assert response.status_code == 200
        assert response.json["bookingAllowedDatetime"] == response_booking_allowed_datetime

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.bookingAllowedDatetime == final_booking_allowed_datetime
        assert updated_offer.publicationDatetime == datetime.datetime(2025, 6, 23, tzinfo=datetime.UTC)

    def test_we_handle_unique_address_among_manual_edition_while_patch_offer(self, client):
        user_offerer_1 = offerers_factories.UserOffererFactory(user__email="user1@example.com")
        user_offerer_2 = offerers_factories.UserOffererFactory(user__email="user2@example.com")
        user_offerer_3 = offerers_factories.UserOffererFactory(user__email="user3@example.com")

        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer_1.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONFERENCE.id,
            venue=venue,
            name="New name",
            description="description",
            offererAddress=venue.offererAddress,
        )

        data = {
            "location": {
                "city": "Saint-Pierre-des-Corps",
                "latitude": 47.38,
                "longitude": 0.72,
                "postalCode": "37700",
                "street": "20 Rue des Grands Mortiers",
                "banId": "37233_0531_00020",
                "inseeCode": "37233",
                "label": "",
                "isManualEdition": False,
                "isVenueLocation": False,
            }
        }
        client_session = client.with_session_auth("user1@example.com")

        # User of offerer 1 create the address through BAN API
        with patch(
            "pcapi.connectors.api_adresse.get_address",
            return_value=api_adresse.AddressInfo(
                id="37233_0531_00020",
                label="20 Rue des Grands Mortiers, 37700 Saint-Pierre-des-Corps",
                postcode="37700",
                citycode="37233",
                latitude=47.38,
                longitude=0.72,
                score=0.9,
                city="Saint-Pierre-des-Corps",
                street="20 Rue des Grands Mortiers",
            ),
        ):
            response = client_session.patch(self.endpoint.format(offer_id=offer.id), json=data)
            assert response.status_code == 200

        offer = db.session.query(offers_models.Offer).one()
        assert offer.offererAddress.address.city == data["location"]["city"]
        address = db.session.query(geography_models.Address).order_by(geography_models.Address.id.desc()).first()
        assert address.isManualEdition == False
        assert address.city == "Saint-Pierre-des-Corps"

        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer_2.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONFERENCE.id,
            venue=venue,
            name="New name",
            description="description",
            offererAddress=venue.offererAddress,
        )

        data = {
            "location": {
                "city": "saint-pierre-des-corps",
                "latitude": 47.38,
                "longitude": 0.72,
                "postalCode": "37700",
                "street": "20 Rue des Grands Mortiers",
                "banId": None,
                "label": "",
                "isManualEdition": True,
                "isVenueLocation": False,
            }
        }
        client_session = client.with_session_auth("user2@example.com")

        with patch(
            "pcapi.connectors.api_adresse.get_municipality_centroid",
            return_value=api_adresse.AddressInfo(
                id="37233",
                label="Saint-Pierre-des-Corps",
                postcode="37700",
                citycode="37233",
                latitude=47.38,
                longitude=0.72,
                score=0.9,
                city="Saint-Pierre-des-Corps",
                street="unused",
            ),
        ):
            # User of offerer 2 create the exact same address but manually. Maybe the BAN API is down, maybe is though the
            # address wasn't knwon. Anyway this can happen and it should be handled.
            response = client_session.patch(self.endpoint.format(offer_id=offer.id), json=data)
            assert response.status_code == 200

        offer = db.session.query(offers_models.Offer).order_by(Offer.id.desc()).first()
        assert offer.offererAddress.address.city == data["location"]["city"].title()
        address = db.session.query(geography_models.Address).order_by(geography_models.Address.id.desc()).first()
        assert address.isManualEdition == True
        assert address.city == data["location"]["city"].title()

        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer_3.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONFERENCE.id,
            venue=venue,
            name="New name",
            description="description",
            offererAddress=venue.offererAddress,
        )

        data = {
            "location": {
                "city": "SAINT-PIERRE-DES-CORPS",
                "latitude": 47.38,
                "longitude": 0.72,
                "postalCode": "37700",
                "street": "20 Rue des Grands Mortiers",
                "banId": None,
                "label": "",
                "isManualEdition": True,
                "isVenueLocation": False,
            }
        }
        client_session = client.with_session_auth("user3@example.com")

        with patch(
            "pcapi.connectors.api_adresse.get_municipality_centroid",
            return_value=api_adresse.AddressInfo(
                id="37233",
                label="Saint-Pierre-des-Corps",
                postcode="37700",
                citycode="37233",
                latitude=47.38,
                longitude=0.72,
                score=0.9,
                city="Saint-Pierre-des-Corps",
                street="unused",
            ),
        ):
            # User of offerer 3 could create manually the same address as user of offerer 2 for same reasons.
            # We should handle that case
            response = client_session.patch(self.endpoint.format(offer_id=offer.id), json=data)
            assert response.status_code == 200

        offer = db.session.query(offers_models.Offer).order_by(offers_models.Offer.id.desc()).first()
        assert (
            db.session.query(geography_models.Address).filter(geography_models.Address.inseeCode == "37233").count()
            == 2
        )
        assert offer.offererAddress.address.isManualEdition == True
        assert offer.offererAddress.address.city == data["location"]["city"].title()

    def test_patch_offer_with_manually_edited_oa(self, client):
        LONGITUDE = "1.55"
        LATITUDE = "47.16995"
        # Due to the convertion between base 10 and binary, floats are an approximation.
        # Those numbers should be equal but aren't exactly.
        # This assert ensures the number were amoung those causing issues, please, don't remove them.
        assert Decimal(float(LONGITUDE)) != Decimal(LONGITUDE)
        assert Decimal(float(LATITUDE)) != Decimal(LATITUDE)

        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONFERENCE.id,
            venue=venue,
            name="New name",
            description="description",
            offererAddress=venue.offererAddress,
        )

        data = {
            "location": {
                "city": "Rio",
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "postalCode": "12345",
                "street": "666 rue du bug",
                "label": "",
                "isManualEdition": True,
                "isVenueLocation": False,
            }
        }
        client_session = client.with_session_auth("user@example.com")

        # First call to create the address
        response = client_session.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json

        # Second should not fail
        # this was once a bug as the address could not be recreated (constraint)
        # nor fetched (because float<->decimal approximation made the match on coords fails)
        response = client_session.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert response.json["id"] == offer.id

    def test_patch_offer_with_extra_data_should_not_remove_extra_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            extraData={"gtl_id": "01010101", "author": "Kewis Larol"},
        )

        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id
        assert response.json["venue"]["street"] == offer.venue.offererAddress.address.street

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.extraData["gtl_id"] == "01010101"
        assert updated_offer.extraData["author"] == "Kewis Larol"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert not updated_offer.product

    def test_patch_offer_with_product_with_ean(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean="1111111111111",
            name="New name",
            description="description",
        )
        offer = offers_factories.OfferFactory(venue=venue)

        data = {"extraData": {"ean": "1111111111111"}}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.extraData == {}
        assert updated_offer.ean == "1111111111111"

    def test_patch_offer_with_product_with_gtl_id(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean="1111111111111",
            name="New name",
            description="description",
        )
        offer = offers_factories.OfferFactory(venue=venue)

        data = {"extraData": {"gtl_id": "010101010"}}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200, response.json
        assert response.json["id"] == offer.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.extraData == {"gtl_id": "010101010"}

    def test_patch_offer_with_product_with_same_ean(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean="1111111111111",
            name="New name",
            description="description",
        )
        offer = offers_factories.OfferFactory(venue=venue, product=product)

        data = {"extraData": {"ean": "1111111111111"}}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.ean == "1111111111111"
        assert updated_offer.extraData == {}

    def test_patch_offer_with_provider_extra_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venue=venue)
        allocine_provider = providers_factories.AllocineProviderFactory(venue=venue_provider.venue)
        offer = offers_factories.OfferFactory(
            name="Film",
            venue=venue,
            lastProvider=allocine_provider,
            subcategoryId=subcategories.SEANCE_CINE.id,
            isDuo=False,
            description="description",
            extraData={
                "cast": ["Joan Baez", "Joe Cocker", "David Crosby"],
                "eidr": "10.5240/ADBD-3CAA-43A0-7BF0-86E2-K",
                "type": "FEATURE_FILM",
                "visa": "37205",
                "title": "Woodstock",
                "genres": ["DOCUMENTARY", "HISTORICAL", "MUSIC"],
                "credits": [
                    {"person": {"lastName": "Wadleigh", "firstName": "Michael"}, "position": {"name": "DIRECTOR"}}
                ],
                "runtime": 185,
                "theater": {"allocine_room_id": "W0135", "allocine_movie_id": 2634},
                "backlink": "https://www.allocine.fr/film/fichefilm_gen_cfilm=2634.html",
                "synopsis": "Le plus important rassemblement de la musique pop de ces vingt derni\u00e8res ann\u00e9es. Des groupes qui ont marqu\u00e9 leur \u00e9poque et une jeunesse qui a marqu\u00e9 la sienne.",
                "companies": [{"name": "Wadleigh-Maurice", "activity": "Production"}],
                "countries": ["USA"],
                "posterUrl": "https://fr.web.img2.acsta.net/pictures/14/06/20/12/25/387023.jpg",
                "allocineId": 2634,
                "originalTitle": "Woodstock",
                "stageDirector": "Michael Wadleigh",
                "productionYear": 1970,
            },
        )

        data = {
            "externalTicketOfficeUrl": "http://example.net",
            "extraData": {
                "cast": ["Joan Baez", "Joe Cocker", "David Crosby"],
                "eidr": "10.5240/ADBD-3CAA-43A0-7BF0-86E2-K",
                "type": "FEATURE_FILM",
                "visa": "37205",
                "title": "Woodstock",
                "genres": ["DOCUMENTARY", "HISTORICAL", "MUSIC"],
                "credits": [
                    {"person": {"lastName": "Wadleigh", "firstName": "Michael"}, "position": {"name": "DIRECTOR"}}
                ],
                "runtime": 185,
                "theater": {"allocine_room_id": "W0135", "allocine_movie_id": 2634},
                "backlink": "https://www.allocine.fr/film/fichefilm_gen_cfilm=2634.html",
                "synopsis": "Le plus important rassemblement de la musique pop de ces vingt derni\u00e8res ann\u00e9es. Des groupes qui ont marqu\u00e9 leur \u00e9poque et une jeunesse qui a marqu\u00e9 la sienne.",
                "companies": [{"name": "Wadleigh-Maurice", "activity": "Production"}],
                "countries": ["USA"],
                "posterUrl": "https://fr.web.img2.acsta.net/pictures/14/06/20/12/25/387023.jpg",
                "allocineId": 2634,
                "originalTitle": "Woodstock",
                "stageDirector": "Michael Wadleigh",
                "productionYear": 1970,
            },
        }
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200, response.json
        assert response.json["id"] == offer.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.externalTicketOfficeUrl == "http://example.net"
        assert updated_offer.extraData == {
            "cast": ["Joan Baez", "Joe Cocker", "David Crosby"],
            "eidr": "10.5240/ADBD-3CAA-43A0-7BF0-86E2-K",
            "type": "FEATURE_FILM",
            "visa": "37205",
            "title": "Woodstock",
            "genres": ["DOCUMENTARY", "HISTORICAL", "MUSIC"],
            "credits": [{"person": {"lastName": "Wadleigh", "firstName": "Michael"}, "position": {"name": "DIRECTOR"}}],
            "runtime": 185,
            "theater": {"allocine_room_id": "W0135", "allocine_movie_id": 2634},
            "backlink": "https://www.allocine.fr/film/fichefilm_gen_cfilm=2634.html",
            "synopsis": "Le plus important rassemblement de la musique pop de ces vingt derni\u00e8res ann\u00e9es. Des groupes qui ont marqu\u00e9 leur \u00e9poque et une jeunesse qui a marqu\u00e9 la sienne.",
            "companies": [{"name": "Wadleigh-Maurice", "activity": "Production"}],
            "countries": ["USA"],
            "posterUrl": "https://fr.web.img2.acsta.net/pictures/14/06/20/12/25/387023.jpg",
            "allocineId": 2634,
            "originalTitle": "Woodstock",
            "stageDirector": "Michael Wadleigh",
            "productionYear": 1970,
        }

    @pytest.mark.parametrize(
        "label, offer_has_oa, address_update_exist",
        [
            ["label", True, True],
            ["label", False, True],
            ["label", False, False],
            ["label", True, False],
            [None, True, True],
            [None, False, True],
            [None, False, False],
            [None, True, False],
        ],
    )
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_patch_offer_with_address(self, get_address_mock, label, offer_has_oa, address_update_exist, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        oa = None
        if offer_has_oa:
            oa = offerers_factories.OfferLocationFactory(offerer=user_offerer.offerer, venue=venue, label=label)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_MEDIATHEQUE.id,
            venue=venue,
            name="New name",
            description="description",
            offererAddress=oa,
        )
        if address_update_exist:
            existant_oa = offerers_factories.OfferLocationFactory(
                offerer=user_offerer.offerer,
                venue=venue,
                label=label,
                address__street="1 rue de la paix",
                address__city="Paris",
                address__banId="75102_7560_00001",
                address__postalCode="75102",
                address__latitude=48.8566,
                address__longitude=2.3522,
            )

        # When
        data = {
            "name": "New name",
            "externalTicketOfficeUrl": "http://example.net",
            "mentalDisabilityCompliant": True,
            "location": {
                "isVenueLocation": False,
                "street": "1 rue de la paix",
                "city": "Paris",
                "postalCode": "75102",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "label": label,
                "inseeCode": "75102",
                "banId": "75102_7560_00001",
            },
        }
        get_address_mock.return_value = api_adresse.AddressInfo(
            street="1 rue de la paix",
            city="Paris",
            citycode="75102",
            postcode="75102",
            latitude=48.8566,
            longitude=2.3522,
            score=0.9,
            id="75102_7560_00001",
            label=label if label else "",
        )
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200, response.json
        assert response.json["id"] == offer.id
        updated_offer = db.session.get(Offer, offer.id)
        address = updated_offer.offererAddress.address
        if address_update_exist:
            assert updated_offer.offererAddress == existant_oa
        assert updated_offer.offererAddress.label == label
        assert address.street == "1 rue de la paix"
        assert address.city == "Paris"
        assert address.postalCode == "75102"
        assert address.latitude == Decimal("48.85660")
        assert address.longitude == Decimal("2.3522")
        assert address.isManualEdition is False

    @patch("pcapi.connectors.api_adresse.get_address")
    def test_user_can_link_offer_to_the_address_of_venue(self, get_address_mock, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_MEDIATHEQUE.id,
            venue=venue,
            name="New name",
            description="description",
            offererAddress=None,
        )
        data = {
            "location": {
                "isVenueLocation": True,
            },
        }
        offer_id = offer.id
        http_client = client.with_session_auth("user@example.com")

        # select user + session
        # select offer + artists (2 queries)
        # select user_offerer
        # select offerer_address in get_or_create_offer_location (1 query)
        # insert new offerer_address in get_or_create_offer_location (1 query)
        # update offer
        # select offer + artists (2 queries)
        # select mediation (1 query)
        # select headline
        # select artist offer link
        # select highlight request
        # select price category
        with assert_num_queries(14):
            response = http_client.patch(self.endpoint.format(offer_id=offer_id), json=data)
        get_address_mock.assert_not_called()

        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert offer.offererAddress.address == venue.offererAddress.address

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    def test_patch_offer_with_manual_address_edition(self, mocked_get_centroid, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.RENCONTRE.id,
            venue=venue,
            name="New name",
            description="description",
        )
        mocked_get_centroid.return_value = api_adresse.AddressInfo(
            id="98826",
            label="Poum",
            postcode="98826",
            citycode="98826",
            latitude=-20.203,
            longitude=164.073,
            score=0.9371472727272726,
            city="Poum",
            street="unused",
        )

        # When
        data = {
            "name": "Visite des Marais Salins de Kô",
            "externalTicketOfficeUrl": "http://example.net",
            "mentalDisabilityCompliant": True,
            "location": {
                "isVenueLocation": False,
                "street": "3, Chemin de la Plage",
                "city": "Poum, Tiabet",
                "postalCode": "98826",
                "latitude": -20.08521415490879,
                "longitude": 164.03239215718415,
                "label": "Marais Salins de Kô",
                "isManualEdition": True,
            },
        }

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["id"] == offer.id
        updated_offer = db.session.get(Offer, offer.id)
        address = updated_offer.offererAddress.address
        assert updated_offer.offererAddress.label == "Marais Salins de Kô"
        assert address.street == data["location"]["street"]
        assert address.city == data["location"]["city"]
        assert address.postalCode == data["location"]["postalCode"]
        assert address.inseeCode == "98826"
        assert address.latitude == Decimal("-20.08521")
        assert address.longitude == Decimal("164.03239")
        assert address.isManualEdition is True

    @patch("pcapi.connectors.api_adresse.get_municipality_centroid")
    def test_unknown_result_from_api_adresse_doesnt_block_offer_creation(self, mocked_get_centroid, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.RENCONTRE.id,
            venue=venue,
            name="New name",
            description="description",
        )
        mocked_get_centroid.side_effect = api_adresse.NoResultException
        # When
        data = {
            "name": "Visite des Marais Salins de Kô",
            "externalTicketOfficeUrl": "http://example.net",
            "mentalDisabilityCompliant": True,
            "location": {
                "isVenueLocation": False,
                "street": "3, Chemin de la Plage",
                "city": "Poum, Tiabet",
                "postalCode": "98826",
                "latitude": -20.08521415490879,
                "longitude": 164.03239215718415,
                "label": "Marais Salins de Kô",
                "isManualEdition": True,
            },
        }

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["id"] == offer.id
        updated_offer = db.session.get(Offer, offer.id)
        address = updated_offer.offererAddress.address
        assert updated_offer.offererAddress.label == "Marais Salins de Kô"
        assert address.street == data["location"]["street"]
        assert address.city == data["location"]["city"]
        assert address.postalCode == data["location"]["postalCode"]
        assert address.inseeCode == None
        assert address.latitude == Decimal("-20.08521")
        assert address.longitude == Decimal("164.03239")
        assert address.isManualEdition is True

    def test_withdrawal_can_be_updated(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            bookingContact="booking@conta.ct",
            name="New name",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "withdrawalDetails": "Veuillez récuperer vos billets à l'accueil :)",
            "withdrawalType": "no_ticket",
        }
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        offer = db.session.get(Offer, offer.id)
        assert offer.withdrawalDetails == "Veuillez récuperer vos billets à l'accueil :)"
        assert offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET

    def test_withdrawal_update_send_email_to_each_related_booker(self, client):
        # given
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            bookingContact="booking@conta.ct",
            name="New name",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        stock = offers_factories.StockFactory(offer=offer)
        bookings = [bookings_factories.BookingFactory(stock=stock) for _ in range(3)]

        data = {
            "withdrawalDetails": "conditions de retrait",
            "withdrawalType": "no_ticket",
            "shouldSendMail": "true",
        }

        # when
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        # then
        assert response.status_code == 200
        assert len(mails_testing.outbox) == 3

        outbox = sorted(mails_testing.outbox, key=lambda mail: mail["params"]["OFFER_TOKEN"])
        bookings.sort(key=lambda b: b.activationCode.code if getattr(b, "activationCode") else b.token)
        assert [mail["To"] for mail in outbox] == [b.user.email for b in bookings]
        assert [mail["params"]["USER_FIRST_NAME"] for mail in outbox] == [b.user.firstName for b in bookings]
        assert [mail["params"]["OFFER_NAME"] for mail in outbox] == [b.stock.offer.name for b in bookings]
        assert [mail["params"]["OFFER_TOKEN"] for mail in outbox] == [
            b.activationCode.code if b.activationCode else b.token for b in bookings
        ]
        assert [mail["params"]["OFFER_WITHDRAWAL_DELAY"] for mail in outbox] == [None] * 3
        assert [mail["params"]["OFFER_WITHDRAWAL_DETAILS"] for mail in outbox] == ["conditions de retrait"] * 3
        assert [mail["params"]["OFFER_WITHDRAWAL_TYPE"] for mail in outbox] == ["no_ticket"] * 3
        assert [mail["params"]["OFFERER_NAME"] for mail in outbox] == [offer.venue.managingOfferer.name] * 3

    def test_withdrawal_update_does_not_send_email_if_not_specified_so(self, client):
        # given
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            bookingContact="booking@conta.ct",
            name="New name",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        stock = offers_factories.StockFactory(offer=offer)
        _ = [bookings_factories.BookingFactory(stock=stock) for _ in range(3)]

        data = {
            "withdrawalDetails": "conditions de retrait",
            "withdrawalType": "no_ticket",
            "shouldSendMail": "false",
        }

        # when
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        # then
        assert response.status_code == 200
        assert len(mails_testing.outbox) == 0

    @pytest.mark.parametrize("should_send_mail", [True, False])
    @pytest.mark.parametrize("is_manual_edition", [True, False])
    def test_withdrawal_update_send_email_at_address_modification(self, is_manual_edition, should_send_mail, client):
        # given
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            bookingContact="booking@conta.ct",
            name="New name",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        stock = offers_factories.StockFactory(offer=offer)
        _ = [bookings_factories.BookingFactory(stock=stock) for _ in range(3)]

        data = {
            "location": {
                "longitude": 1.3522,
                "isVenueLocation": False,
                "city": "Paris",
                "label": "New label",
                "latitude": 1.3040,
                "postalCode": "75001",
                "street": "1 rue de la paix",
                "isManualEdition": is_manual_edition,
            },
            "shouldSendMail": should_send_mail,
        }

        # when
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        # then
        assert response.status_code == 200
        if should_send_mail == False:
            assert len(mails_testing.outbox) == 0
        else:
            assert len(mails_testing.outbox) == 3

    @time_machine.travel(datetime.datetime(2026, 4, 21, 12, 0, 0), tick=False)
    def test_patch_offer_turns_cultural_outreach_claim_to_true(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.ESCAPE_GAME.id)
        cultural_outreach_factories.CulturalOutreachFactory(offer=offer)

        data = {
            "hasCulturalOutreachClaim": True,
        }
        response = client.with_session_auth(user_offerer.user.email).patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["hasCulturalOutreachClaim"] is True

    def test_patch_offer_turns_cultural_outreach_claim_to_false(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.ESCAPE_GAME.id)
        cultural_outreach_factories.ClaimedCulturalOutreachFactory(offer=offer)

        data = {
            "hasCulturalOutreachClaim": False,
        }

        response = client.with_session_auth(user_offerer.user.email).patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["hasCulturalOutreachClaim"] is False

    def test_patch_offer_creates_cultural_outreach_claim(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.ESCAPE_GAME.id)

        data = {
            "hasCulturalOutreachClaim": True,
        }
        response = client.with_session_auth(user_offerer.user.email).patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200
        assert response.json["hasCulturalOutreachClaim"] is True

    def test_patch_offer_with_empty_body_does_not_change_the_offer(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            name="Un nom",
            description="Une description",
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={})

        assert response.status_code == 200, response.json
        assert response.json["id"] == offer.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.name == "Un nom"
        assert updated_offer.description == "Une description"

    def test_patch_offer_simple_fields(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            name="Un nom",
            description="Une description",
            bookingEmail="old@example.com",
            isNational=False,
            isDuo=False,
            durationMinutes=None,
        )

        data = {
            "description": "Une toute nouvelle description",
            "bookingEmail": "new@example.com",
            "isNational": True,
            "isDuo": True,
            "durationMinutes": 90,
        }
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert response.json["description"] == "Une toute nouvelle description"
        assert response.json["bookingEmail"] == "new@example.com"
        assert response.json["isNational"] is True
        assert response.json["isDuo"] is True
        assert response.json["durationMinutes"] == 90

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.description == "Une toute nouvelle description"
        assert updated_offer.bookingEmail == "new@example.com"
        assert updated_offer.isNational is True
        assert updated_offer.isDuo is True
        assert updated_offer.durationMinutes == 90

    def test_patch_offer_accessibility_fields(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            audioDisabilityCompliant=False,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=False,
            visualDisabilityCompliant=False,
        )

        data = {
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.audioDisabilityCompliant is True
        assert updated_offer.mentalDisabilityCompliant is True
        assert updated_offer.motorDisabilityCompliant is True
        assert updated_offer.visualDisabilityCompliant is True

    def test_patch_offer_subcategory_id_on_draft_offer(self, client, venue, auth_client):
        offer = offers_factories.DraftOfferFactory(
            subcategoryId=subcategories.CARTE_MUSEE.id,
            venue=venue,
        )

        data = {"subcategoryId": subcategories.ESCAPE_GAME.id}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert response.json["subcategoryId"] == subcategories.ESCAPE_GAME.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.subcategoryId == subcategories.ESCAPE_GAME.id

    def test_patch_offer_creates_artist_offer_links(self, client, venue, auth_client):
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id, venue=venue)

        data = {
            "artistOfferLinks": [
                {"artistId": artist.id, "artistType": "performer", "artistName": artist.name},
                {"artistId": None, "artistType": "author", "artistName": "Artiste inconnu"},
            ]
        }
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert sorted(response.json["artistOfferLinks"], key=lambda link: link["artistType"]) == [
            {"artistId": None, "artistName": "Artiste inconnu", "artistType": "author"},
            {"artistId": artist.id, "artistName": artist.name, "artistType": "performer"},
        ]

        links = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer.id).all()
        assert len(links) == 2

    def test_patch_offer_replaces_artist_offer_links(self, client, venue, auth_client):
        artist = artist_factories.ArtistFactory()
        new_artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id, venue=venue)
        artist_factories.ArtistOfferLinkFactory(
            offer_id=offer.id,
            artist_id=artist.id,
            artist_type=artist_models.ArtistType.PERFORMER,
        )

        data = {
            "artistOfferLinks": [
                {"artistId": new_artist.id, "artistType": "author", "artistName": new_artist.name},
            ]
        }
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert response.json["artistOfferLinks"] == [
            {"artistId": new_artist.id, "artistName": new_artist.name, "artistType": "author"},
        ]

        links = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer.id).all()
        assert len(links) == 1
        assert links[0].artist_id == new_artist.id
        assert links[0].artist_type == artist_models.ArtistType.AUTHOR

    def test_patch_offer_removes_artist_offer_links(self, client, venue, auth_client):
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id, venue=venue)
        artist_factories.ArtistOfferLinkFactory(
            offer_id=offer.id,
            artist_id=artist.id,
            artist_type=artist_models.ArtistType.PERFORMER,
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"artistOfferLinks": []})

        assert response.status_code == 200, response.json
        assert response.json["artistOfferLinks"] == []
        assert db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer.id).count() == 0

    def test_withdrawal_type_on_site_requires_a_delay(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            bookingContact="booking@conta.ct",
            withdrawalType=WithdrawalTypeEnum.NO_TICKET,
            withdrawalDelay=None,
        )

        data = {"withdrawalType": "on_site", "withdrawalDelay": 60 * 30}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.withdrawalType == WithdrawalTypeEnum.ON_SITE
        assert updated_offer.withdrawalDelay == 60 * 30

    def test_should_send_mail_without_withdrawal_nor_address_change_sends_nothing(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            bookingContact="booking@conta.ct",
            name="Un nom",
        )
        stock = offers_factories.StockFactory(offer=offer)
        bookings_factories.BookingFactory(stock=stock)

        data = {"name": "Un autre nom", "shouldSendMail": True}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).name == "Un autre nom"
        assert len(mails_testing.outbox) == 0

    def test_patch_offer_does_not_update_an_already_claimed_cultural_outreach(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.ESCAPE_GAME.id)
        claimed_datetime = datetime.datetime(2026, 4, 20, 12, 0, 0)
        cultural_outreach_factories.ClaimedCulturalOutreachFactory(offer=offer, claimedDatetime=claimed_datetime)

        response = client.with_session_auth(user_offerer.user.email).patch(
            self.endpoint.format(offer_id=offer.id), json={"hasCulturalOutreachClaim": True}
        )

        assert response.status_code == 200
        assert response.json["hasCulturalOutreachClaim"] is True

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.culturalOutreach.claimedDatetime == claimed_datetime

    def test_patch_offer_notifies_users_who_asked_for_a_reminder(self, client, venue, auth_client):
        offer = offers_factories.EventOfferFactory(
            venue=venue,
            name="Super Future Offer",
            publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            bookingAllowedDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=10),
        )
        user = users_factories.BeneficiaryGrant18Factory()
        reminders_factories.OfferReminderFactory(offer=offer, user=user)

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"bookingAllowedDatetime": None})

        assert response.status_code == 200, response.json
        assert response.json["bookingAllowedDatetime"] is None

        assert len(push_testing.requests) == 1
        assert push_testing.requests[0]["payload"] == [
            {
                "id": str(user.id),
                "events": [
                    {
                        "name": "ue.future_offer_activated",
                        "attributes": {
                            "offer_id": offer.id,
                            "offer_name": "Super Future Offer",
                            "offer_category": "CINEMA",
                            "offer_subcategory": "SEANCE_CINE",
                            "offer_type": "solo",
                        },
                    }
                ],
            }
        ]
        assert db.session.query(reminders_models.OfferReminder).filter_by(offerId=offer.id).count() == 0

    def test_patch_draft_offer_skips_url_and_address_coherence_checks(self, client, venue, auth_client):
        # The creation tunnel is split into several steps: a draft may be
        # inconsistent (no url and no address) until it is finalized.
        offer = offers_factories.DraftOfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            url=None,
            offererAddress=None,
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"name": "Un brouillon"})

        assert response.status_code == 200, response.json

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.name == "Un brouillon"
        assert updated_offer.url is None
        assert updated_offer.offererAddress is None

    def test_patch_offer_withdrawing_a_cultural_outreach_claim_that_does_not_exist_is_a_noop(self, client):
        # `update_cultural_outreach_claim` is only called when the offer
        # already has a cultural outreach, so nothing happens here.
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.ESCAPE_GAME.id)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"hasCulturalOutreachClaim": False}
        )

        assert response.status_code == 200, response.json
        assert response.json["hasCulturalOutreachClaim"] is False
        assert db.session.get(Offer, offer.id).culturalOutreach is None

    def test_patch_offer_derives_gtl_id_from_music_type(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            venue=venue,
            extraData={},
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"extraData": {"musicType": "501"}})

        assert response.status_code == 200, response.json

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.extraData == {"musicType": "501", "gtl_id": "02000000"}

    def test_patch_draft_offer_does_not_derive_gtl_id_when_subcategory_becomes_musical(
        self, client, venue, auth_client
    ):
        # `deserialize_extra_data` is called with the subcategory the offer
        # currently has, not the one sent in the body: switching to a musical
        # subcategory and sending a musicType in the same request does not
        # derive the gtl_id.
        offer = offers_factories.DraftOfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            extraData={},
        )

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id),
            json={
                "subcategoryId": subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
                "extraData": {"musicType": "501"},
            },
        )

        assert response.status_code == 200, response.json

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id
        assert updated_offer.extraData == {"musicType": "501"}

    def test_patch_offer_extracts_the_ean_from_extra_data(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            extraData={},
            ean=None,
        )

        data = {"extraData": {"ean": "1234567890123", "author": "Kewis Larol"}}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert response.json["extraData"] == {"author": "Kewis Larol", "ean": "1234567890123"}

        # the EAN has its own column, it is not kept in `extraData`
        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.ean == "1234567890123"
        assert updated_offer.extraData == {"author": "Kewis Larol"}
        assert updated_offer.product is None

    def test_patch_offer_stores_extra_data_outside_of_the_subcategory_conditional_fields(
        self, client, venue, auth_client
    ):
        # ESCAPE_GAME has no conditional field: `_format_extra_data` filters
        # them for the validation only, the payload is persisted as is.
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            extraData={},
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"extraData": {"author": "Moi"}})

        assert response.status_code == 200, response.json
        assert response.json["extraData"] == {"author": "Moi"}
        assert db.session.get(Offer, offer.id).extraData == {"author": "Moi"}

    def test_patch_extra_data_ignores_the_fields_only_mandatory_for_the_public_api(self, client, venue, auth_client):
        # musicType and ean are only required in the external form: this route
        # updates the offer with `is_from_private_api=True`.
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            venue=venue,
            extraData={},
            ean=None,
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"extraData": {"performer": "Toi"}})

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).extraData == {"performer": "Toi"}

    def test_patch_offer_does_not_notify_users_when_booking_is_still_not_allowed(self, client, venue, auth_client):
        offer = offers_factories.EventOfferFactory(
            venue=venue,
            publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            bookingAllowedDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=10),
        )
        user = users_factories.BeneficiaryGrant18Factory()
        reminders_factories.OfferReminderFactory(offer=offer, user=user)

        data = {
            "bookingAllowedDatetime": format_into_utc_date(date_utils.get_naive_utc_now() + datetime.timedelta(days=20))
        }
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json

        # the offer is still not bookable: nobody is notified and the reminders are kept
        assert push_testing.requests == []
        assert db.session.query(reminders_models.OfferReminder).filter_by(offerId=offer.id).count() == 1

    def test_patch_offer_response_contains_headline_bookings_and_location_data(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            name="Un nom",
        )
        offers_factories.MediationFactory(offer=offer)
        offers_factories.HeadlineOfferFactory(offer=offer, venue=venue)
        stock = offers_factories.StockFactory(offer=offer, price=Decimal("12.00"), quantity=10)
        bookings_factories.BookingFactory(stock=stock)

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"name": "Un autre nom"})

        assert response.status_code == 200, response.json
        assert response.json["name"] == "Un autre nom"
        assert response.json["isHeadlineOffer"] is True
        assert response.json["hasPendingBookings"] is True
        assert response.json["bookingsCount"] == 1
        assert response.json["isNonFreeOffer"] is True
        assert response.json["location"]["street"] == venue.offererAddress.address.street
        assert response.json["location"]["isVenueLocation"] is True

    def test_patch_url_does_not_change_is_national(self, client, venue, auth_client):
        # `isNational` is only recomputed from the url when it is part of the
        # body: an offer keeps its value otherwise.
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            url="https://example.com/offer",
            offererAddress=None,
            isNational=False,
        )

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id), json={"url": "https://example.com/another-offer"}
        )

        assert response.status_code == 200, response.json
        assert response.json["isNational"] is False

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.url == "https://example.com/another-offer"
        assert updated_offer.isNational is False

    def test_patch_url_forces_is_national_when_both_are_sent(self, client, venue, auth_client):
        # `UpdateOffer.validate_is_national` (core/offers/schemas.py) is declared
        # after `url` so that it can read it: the value sent in the body is
        # overridden as soon as an url is part of the same request.
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            url="https://example.com/offer",
            offererAddress=None,
            isNational=False,
        )

        data = {"url": "https://example.com/another-offer", "isNational": False}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert response.json["isNational"] is True
        assert db.session.get(Offer, offer.id).isNational is True

    def test_patch_draft_offer_changes_subcategory_and_artist_offer_links_together(self, client, venue, auth_client):
        # artist links are checked against the subcategory sent in the body,
        # not the one the offer currently has: `performer` is allowed by
        # CONCERT but not by LIVRE_PAPIER.
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.DraftOfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, venue=venue)

        data = {
            "subcategoryId": subcategories.CONCERT.id,
            "artistOfferLinks": [{"artistId": artist.id, "artistType": "performer", "artistName": artist.name}],
        }
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert response.json["subcategoryId"] == subcategories.CONCERT.id

        links = db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer.id).all()
        assert len(links) == 1
        assert links[0].artist_type == artist_models.ArtistType.PERFORMER

    def test_patch_draft_offer_becoming_withdrawable_does_not_check_the_withdrawal_data(
        self, client, venue, auth_client
    ):
        # `check_offer_withdrawal` only runs when a withdrawal field is part of
        # the update: switching to a withdrawable subcategory alone leaves the
        # offer without a withdrawal type nor a booking contact.
        offer = offers_factories.DraftOfferFactory(
            subcategoryId=subcategories.CARTE_MUSEE.id,
            venue=venue,
            url=None,
            withdrawalType=None,
            bookingContact=None,
        )

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id), json={"subcategoryId": subcategories.CONCERT.id}
        )

        assert response.status_code == 200, response.json

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.subcategoryId == subcategories.CONCERT.id
        assert updated_offer.withdrawalType is None
        assert updated_offer.bookingContact is None

    def test_patch_offer_with_an_ean_used_by_an_offer_of_another_venue(self, client, venue, user_offerer, auth_client):
        # EAN unicity is scoped to the venue
        other_venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offers_factories.OfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=other_venue,
            ean="1111111111111",
        )
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, venue=venue, ean=None)

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id), json={"extraData": {"ean": "1111111111111"}}
        )

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).ean == "1111111111111"

    def test_patch_offer_does_not_track_updated_fields_of_a_non_allocine_offer(self, client, venue, auth_client):
        # `fieldsUpdated` is only maintained for Allocine offers
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue, name="Un nom")

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"name": "Un autre nom"})

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).fieldsUpdated == []

    def test_patch_offer_does_not_check_a_lower_bound_for_duration_minutes(self, client, venue, auth_client):
        # `check_duration_minutes` only rejects durations of 24 hours or more
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue, durationMinutes=60
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"durationMinutes": -30})

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).durationMinutes == -30

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_patch_offer_with_unchanged_values_does_not_reindex_the_offer(
        self, mocked_async_index_offer_ids, client, venue, auth_client
    ):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            name="Un nom",
            withdrawalDetails="Retrait à l'accueil",
        )
        stock = offers_factories.StockFactory(offer=offer)
        bookings_factories.BookingFactory(stock=stock)

        data = {"name": "Un nom", "withdrawalDetails": "Retrait à l'accueil", "shouldSendMail": True}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).name == "Un nom"
        mocked_async_index_offer_ids.assert_not_called()
        assert len(mails_testing.outbox) == 0

    def test_patch_offer_logs_message(self, client, caplog, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            name="Un nom",
            description="Une description",
        )

        # `description` is left unchanged: only the modified fields are indexed
        data = {"name": "Un autre nom", "description": "Une description"}
        with caplog.at_level(logging.INFO):
            response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert len([log for log in caplog.records if log.message == "Offer has been updated"]) == 1
        log = next(log for log in caplog.records if log.message == "Offer has been updated")
        assert log.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "product_id": offer.productId,
            "changes": {"name": {"newValue": "Un autre nom", "oldValue": "Un nom"}},
        }

        assert log.technical_message_id == "offer.updated"

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_patch_offer_reindexes_the_offer(self, mocked_async_index_offer_ids, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            name="Un nom",
            description="Une description",
        )

        # `description` is left unchanged: only the modified fields are indexed
        data = {"name": "Un autre nom", "description": "Une description"}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        mocked_async_index_offer_ids.assert_called_once_with(
            [offer.id],
            reason=IndexationReason.OFFER_UPDATE,
            log_extra={"changes": {"name"}},
        )

    def test_patch_offer_with_an_ean_already_used_by_an_inactive_offer(self, client, venue, auth_client):
        # only *active* offers of the venue make an EAN unavailable
        offers_factories.OfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            ean="1111111111111",
            publicationDatetime=None,
        )
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, venue=venue, ean=None)

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id), json={"extraData": {"ean": "1111111111111"}}
        )

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).ean == "1111111111111"

    def test_patch_offer_removes_the_ean(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            ean="1111111111111",
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"extraData": {"ean": None}})

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).ean is None

    def test_patch_offer_removes_the_extra_data(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue=venue,
            extraData={"author": "Un auteur", "visa": "123456"},
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"extraData": None})

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).extraData is None

    def test_patch_offer_update_extra_data_removes_the_previous_value(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue=venue,
            extraData={"author": "Un auteur", "visa": "123456"},
        )

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id), json={"extraData": {"author": "deux auteur"}}
        )

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).extraData == {"author": "deux auteur"}

    def test_patch_offer_removes_the_external_ticket_office_url(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            externalTicketOfficeUrl="https://example.com/tickets",
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"externalTicketOfficeUrl": None})

        assert response.status_code == 200, response.json
        assert response.json["externalTicketOfficeUrl"] is None
        assert db.session.get(Offer, offer.id).externalTicketOfficeUrl is None

    def test_patch_offer_name_with_the_maximum_length(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue, name="Un nom")
        name = "a" * 90

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"name": name})

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).name == name

    def test_patch_offer_withdrawal_delay_alone(self, client, venue, auth_client):
        # the withdrawal type is not part of the body: it is read back from the offer
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            bookingContact="booking@conta.ct",
            withdrawalType=WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"withdrawalDelay": 60 * 60})

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).withdrawalDelay == 60 * 60

    def test_booking_contact_update_sends_email_to_each_related_booker(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            bookingContact="old@conta.ct",
            withdrawalType=WithdrawalTypeEnum.NO_TICKET,
        )
        stock = offers_factories.StockFactory(offer=offer)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)

        data = {"bookingContact": "new@conta.ct", "shouldSendMail": True}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).bookingContact == "new@conta.ct"
        assert len(mails_testing.outbox) == 2

    def test_patch_offer_response_contains_video_highlight_and_cultural_outreach_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue, name="Un nom")
        offers_factories.OfferMetaDataFactory(
            offer=offer,
            videoDuration=262,
            videoExternalId="lm20v6ASSFI",
            videoThumbnailUrl="https://example.com/thumbnail.jpg",
            videoTitle="Un titre de vidéo",
            videoUrl="https://www.youtube.com/watch?v=lm20v6ASSFI",
        )
        highlight = highlights_factories.HighlightFactory(name="Un temps fort")
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight)
        cultural_outreach_factories.ClaimedCulturalOutreachFactory(offer=offer)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"name": "Un autre nom"}
        )

        assert response.status_code == 200, response.json
        assert response.json["videoData"] == {
            "videoDuration": 262,
            "videoExternalId": "lm20v6ASSFI",
            "videoThumbnailUrl": "https://example.com/thumbnail.jpg",
            "videoTitle": "Un titre de vidéo",
            "videoUrl": "https://www.youtube.com/watch?v=lm20v6ASSFI",
        }
        assert response.json["highlightRequests"] == [{"id": highlight.id, "name": "Un temps fort"}]
        assert response.json["hasCulturalOutreachClaim"] is True

    @time_machine.travel(datetime.datetime(2025, 6, 24, tzinfo=datetime.timezone.utc), tick=False)
    @pytest.mark.parametrize(
        "request_publication_datetime,expected_status",
        [
            ("2025-06-28T14:30:00Z", "SCHEDULED"),
            ("now", "ACTIVE"),
            (None, "INACTIVE"),
        ],
    )
    def test_patch_publication_datetime_changes_the_offer_status(
        self, request_publication_datetime, expected_status, client
    ):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            publicationDatetime=datetime.datetime(2025, 6, 26),
        )
        offers_factories.StockFactory(offer=offer, quantity=10)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id),
            json={"publicationDatetime": request_publication_datetime},
        )

        assert response.status_code == 200, response.json
        assert response.json["status"] == expected_status

    def test_patch_publication_datetime_on_a_draft_does_not_publish_it(self, client, venue, auth_client):
        # a draft is published through the dedicated route: patching its
        # publicationDatetime stores the value but keeps the DRAFT status
        offer = offers_factories.DraftOfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            venue=venue,
            publicationDatetime=None,
        )
        publication_datetime = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=2)

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id),
            json={"publicationDatetime": format_into_utc_date(publication_datetime)},
        )

        assert response.status_code == 200, response.json
        assert response.json["status"] == "DRAFT"

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.publicationDatetime == publication_datetime
        assert updated_offer.validation == OfferValidationStatus.DRAFT

    def test_patch_the_editable_fields_of_a_synchronized_offer(self, client):
        provider = providers_factories.PublicApiProviderFactory()
        providers_factories.OffererProviderFactory(provider=provider)
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.PERFORMANCE_HALL
        )
        offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=provider,
            audioDisabilityCompliant=False,
            externalTicketOfficeUrl="http://old.com",
        )

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id),
            json={"audioDisabilityCompliant": True, "externalTicketOfficeUrl": "http://new.com"},
        )

        assert response.status_code == 200, response.json
        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.audioDisabilityCompliant is True
        assert updated_offer.externalTicketOfficeUrl == "http://new.com"

    def test_patch_a_read_only_field_with_its_current_value(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.PERFORMANCE_HALL
        )
        offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=providers_factories.ProviderFactory(),
            name="Un nom",
        )

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"name": "Un nom"}
        )

        assert response.status_code == 200, response.json

    def test_patch_the_name_of_a_synchronized_offer_in_a_museum(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=providers_factories.ProviderFactory(),
            name="Un nom",
        )

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"name": "Un autre nom"}
        )

        assert response.status_code == 200, response.json
        assert db.session.get(Offer, offer.id).name == "Un autre nom"


class Returns400Test:
    endpoint = "/offers/{offer_id}"

    def _assert_patch_is_rejected(self, client, patch_body, expected_response_json, offer_data=None):
        default_offer_data = {
            "subcategoryId": subcategories.CARTE_MUSEE.id,
            "name": "New name",
            "url": "test@test.com",
            "description": "description",
        }
        default_offer_data.update(**(offer_data or {}))
        offer = offers_factories.OfferFactory(**default_offer_data)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=patch_body
        )

        assert response.status_code == 400
        assert response.json == expected_response_json

    def when_sending_non_editable_fields(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "dateCreated": format_into_utc_date(datetime.datetime(2019, 1, 1)),
                "dateModifiedAtLastProvider": format_into_utc_date(datetime.datetime(2019, 1, 1)),
                "id": 1,
                "idAtProviders": 1,
                "lastProviderId": 1,
                "thumbCount": 2,
                "subcategoryId": subcategories.LIVRE_PAPIER.id,
            },
            expected_response_json={
                "dateCreated": ["Vous ne pouvez pas changer cette information"],
                "dateModifiedAtLastProvider": ["Vous ne pouvez pas changer cette information"],
                "id": ["Vous ne pouvez pas changer cette information"],
                "idAtProviders": ["Vous ne pouvez pas changer cette information"],
                "lastProviderId": ["Vous ne pouvez pas changer cette information"],
                "thumbCount": ["Vous ne pouvez pas changer cette information"],
            },
        )

    def when_sending_urls_without_a_scheme(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "url": "missing.something",
                "externalTicketOfficeUrl": "missing.something",
            },
            expected_response_json={
                "url": ['L\'URL doit commencer par "http://" ou "https://"'],
                "externalTicketOfficeUrl": ['L\'URL doit commencer par "http://" ou "https://"'],
            },
        )

    def when_sending_urls_without_a_domain(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "url": "https:///not/domain",
                "externalTicketOfficeUrl": "https:///not/domain",
            },
            expected_response_json={
                "url": ["Relative path are forbidden."],
                "externalTicketOfficeUrl": ["Relative path are forbidden."],
            },
        )

    def when_sending_urls_with_an_ip_address(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "url": "https://10.11.12.13",
                "externalTicketOfficeUrl": "https://10.11.12.13",
            },
            expected_response_json={
                "url": ["IP address are forbidden."],
                "externalTicketOfficeUrl": ["IP address are forbidden."],
            },
        )

    def when_sending_urls_with_a_relative_path(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "url": "https://example.com/../../etc/password",
                "externalTicketOfficeUrl": "https://example.com/../../etc/password",
            },
            expected_response_json={
                "url": ["Relative path are forbidden."],
                "externalTicketOfficeUrl": ["Relative path are forbidden."],
            },
        )

    def when_sending_authenticated_urls(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "url": "https://login:password@example.com",
                "externalTicketOfficeUrl": "https://login:password@example.com",
            },
            expected_response_json={
                "url": ["Authenticated urls are forbidden."],
                "externalTicketOfficeUrl": ["Authenticated urls are forbidden."],
            },
        )

    def when_sending_urls_with_an_ipv6_address(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "url": "https://[::1]",
                "externalTicketOfficeUrl": "https://[::1]",
            },
            expected_response_json={
                "url": ["IP address are forbidden."],
                "externalTicketOfficeUrl": ["IP address are forbidden."],
            },
        )

    def when_sending_urls_without_an_extension(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "url": "https://missing",
                "externalTicketOfficeUrl": "https://missing",
            },
            expected_response_json={
                "url": ["Top level domains are forbidden."],
                "externalTicketOfficeUrl": ["Top level domains are forbidden."],
            },
        )

    def when_sending_a_name_containing_an_ean(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256"},
            expected_response_json={"name": ["Le titre d'une offre ne peut contenir l'EAN"]},
        )

    def when_sending_a_name_longer_than_90_characters(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "name": "Le nom d'une histoire qui est quand même sacrément longue, ce qui est pratique si on lit trop vite, mais ce qui est dommage si on n'a qu'un seul oeil, parce qu'on lit deux fois plus lentement, c'est bien connu"
            },
            expected_response_json={
                "name": ["Cette chaîne de caractères doit avoir une taille maximum de 90 caractères"]
            },
        )

    def when_sending_datetimes_without_a_timezone(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "publicationDatetime": (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat(),
                "bookingAllowedDatetime": (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat(),
            },
            expected_response_json={
                "publicationDatetime": ["The datetime must be timezone-aware."],
                "bookingAllowedDatetime": ["The datetime must be timezone-aware."],
            },
        )

    def when_sending_datetimes_in_the_past(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "publicationDatetime": format_into_utc_date(datetime.datetime.now() - datetime.timedelta(days=2)),
                "bookingAllowedDatetime": format_into_utc_date(datetime.datetime.now() - datetime.timedelta(days=2)),
            },
            expected_response_json={
                "publicationDatetime": ["The datetime must be in the future."],
                "bookingAllowedDatetime": ["The datetime must be in the future."],
            },
        )

    def when_updating_an_offer_pending_validation(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"validation": OfferValidationStatus.PENDING},
            patch_body={"visualDisabilityCompliant": True},
            expected_response_json={
                "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
            },
        )

    def when_updating_a_rejected_offer(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"validation": OfferValidationStatus.REJECTED},
            patch_body={"visualDisabilityCompliant": True},
            expected_response_json={
                "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
            },
        )

    def when_removing_the_booking_contact_of_a_withdrawable_offer(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={
                "subcategoryId": subcategories.CONCERT.id,
                "withdrawalType": WithdrawalTypeEnum.BY_EMAIL,
                "withdrawalDelay": 60 * 15,
                "bookingContact": "booking@conta.ct",
            },
            patch_body={"bookingContact": None},
            expected_response_json={
                "offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]
            },
        )

    def when_setting_a_no_ticket_withdrawal_type_while_keeping_a_withdrawal_delay(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={
                "subcategoryId": subcategories.CONCERT.id,
                "withdrawalType": WithdrawalTypeEnum.BY_EMAIL,
                "withdrawalDelay": 60 * 15,
                "bookingContact": "booking@conta.ct",
            },
            patch_body={"withdrawalType": "no_ticket"},
            expected_response_json={
                "offer": ["Il ne peut pas y avoir de délai de retrait lorsqu'il s'agit d'un évènement sans ticket"]
            },
        )

    # TODO (igabriele, 2025-08-22): Investigate this dubious case and comment it if valid.
    def when_setting_a_no_ticket_withdrawal_type_without_a_booking_contact(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.FESTIVAL_MUSIQUE.id, "url": None},
            patch_body={"withdrawalType": WithdrawalTypeEnum.NO_TICKET.value},
            expected_response_json={
                "offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]
            },
        )

    def when_sending_a_duration_of_24_hours_or_more(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.FESTIVAL_MUSIQUE.id},
            patch_body={"durationMinutes": 1440},
            expected_response_json={
                "durationMinutes": [
                    "La durée doit être inférieure à 24 heures. Pour les événements durant 24 heures ou plus (par exemple, un pass festival de 3 jours), veuillez laisser ce champ vide."
                ]
            },
        )

    def when_sending_an_unknown_extra_data_field(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id, "url": None},
            patch_body={
                "extraData": {
                    "malicious_data": ["a", "very", "large", "dict"],
                },
            },
            expected_response_json={
                "extraData.malicious_data": ["Vous ne pouvez pas changer cette information"],
            },
        )

    def when_sending_an_extra_data_field_larger_than_64_ko(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id, "url": None},
            patch_body={"extraData": {"cast": ["A" * 70000]}},
            expected_response_json={
                "extraData": ["extraData field is too big (maximum 64 Ko)."],
            },
        )

    def when_sending_an_extra_data_field_containing_a_script(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id, "url": None},
            patch_body={"extraData": {"cast": ["><img+stc=x+oneerror=alert(document.cookie)>"]}},
            expected_response_json={
                "extraData": ["extraData field includes forbidden caracters or scripts"],
            },
        )

    def when_sending_extra_data_that_is_not_a_dict(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id, "url": None},
            patch_body={"extraData": 1312},
            expected_response_json={
                "extraData": ["Input should be a valid dictionary"],
            },
        )

    def when_sending_an_unknown_subcategory(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"subcategoryId": "UNKNOWN_SUBCATEGORY"},
            expected_response_json={"subcategory": ["La sous-catégorie de cette offre est inconnue"]},
        )

    def when_sending_a_non_selectable_subcategory(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"subcategoryId": subcategories.ABO_LUDOTHEQUE.id},
            expected_response_json={
                "subcategory": ["Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"]
            },
        )

    def when_changing_the_subcategory_of_an_offer_that_is_no_longer_a_draft(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"subcategoryId": subcategories.ESCAPE_GAME.id},
            expected_response_json={"UnallowedUpdate": ["unallowed update: subcategoryId"]},
        )

    def when_enabling_double_bookings_on_a_subcategory_that_does_not_allow_them(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id, "url": None},
            patch_body={"isDuo": True},
            expected_response_json={"enableDoubleBookings": ["the category chosen does not allow double bookings"]},
        )

    def when_unsetting_an_accessibility_field(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"audioDisabilityCompliant": None},
            expected_response_json={"global": ["L’accessibilité de l’offre doit être définie"]},
        )

    def when_sending_an_artist_type_not_allowed_by_the_subcategory(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={
                "artistOfferLinks": [{"artistId": None, "artistType": "author", "artistName": "Artiste inconnu"}]
            },
            expected_response_json={
                "artistOfferLinks": ["Le type d'artiste n'est pas autorisé pour cette sous catégorie"]
            },
        )

    def when_updating_a_withdrawable_offer_that_has_no_withdrawal_type(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={
                "subcategoryId": subcategories.CONCERT.id,
                "url": None,
                "bookingContact": "booking@conta.ct",
                "withdrawalType": None,
            },
            patch_body={"withdrawalDetails": "Retrait à l'accueil"},
            expected_response_json={
                "offer": ["Une offre qui a un ticket retirable doit avoir un type de retrait renseigné"]
            },
        )

    def when_setting_an_on_site_withdrawal_type_without_a_delay(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={
                "subcategoryId": subcategories.CONCERT.id,
                "url": None,
                "bookingContact": "booking@conta.ct",
                "withdrawalType": WithdrawalTypeEnum.NO_TICKET,
            },
            patch_body={"withdrawalType": "on_site"},
            expected_response_json={"offer": ["Un évènement avec ticket doit avoir un délai de renseigné"]},
        )

    def when_setting_a_by_email_withdrawal_type_without_a_delay(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={
                "subcategoryId": subcategories.CONCERT.id,
                "url": None,
                "bookingContact": "booking@conta.ct",
                "withdrawalType": WithdrawalTypeEnum.NO_TICKET,
            },
            patch_body={"withdrawalType": "by_email"},
            expected_response_json={"offer": ["Un évènement avec ticket doit avoir un délai de renseigné"]},
        )

    def when_setting_an_in_app_withdrawal_type_without_a_ticketing_system(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={
                "subcategoryId": subcategories.CONCERT.id,
                "url": None,
                "bookingContact": "booking@conta.ct",
                "withdrawalType": WithdrawalTypeEnum.NO_TICKET,
            },
            patch_body={"withdrawalType": "in_app"},
            expected_response_json={
                "offer": ["Vous devez supporter l'interface de billeterie pour créer des offres avec billet"]
            },
        )

    def when_removing_a_mandatory_conditional_extra_data_field(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id, "url": None},
            patch_body={"extraData": {"showType": "100"}},
            expected_response_json={"showSubType": ["Ce champ est obligatoire"]},
        )

    def when_sending_a_show_type_outside_of_the_allowed_values(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id, "url": None},
            patch_body={"extraData": {"showType": "999999", "showSubType": "101"}},
            expected_response_json={"showType": ["should be in allowed values"]},
        )

    @pytest.mark.xfail(
        reason=(
            "Known bug: `deserialize_extra_data` (offers/api.py) derives `gtl_id` from `musicType` "
            "before any validation and raises a KeyError on an unknown code, so the route answers 500 "
            "instead of 400. Remove this marker once the lookup is guarded."
        ),
        strict=True,
    )
    def when_sending_a_music_type_outside_of_the_allowed_values(self, client):
        default_offer_data = {
            "subcategoryId": subcategories.CONCERT.id,
            "name": "New name",
            "url": None,
            "description": "description",
        }
        offer = offers_factories.OfferFactory(**default_offer_data)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"extraData": {"musicType": "999999"}}
        )

        assert response.status_code == 500
        assert response.json == {
            "global": ["Il semble que nous ayons des problèmes techniques :( On répare ça au plus vite"]
        }

    def when_sending_an_invalid_gtl_id(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.LIVRE_PAPIER.id, "url": None},
            patch_body={"extraData": {"gtl_id": "99999999"}},
            expected_response_json={"gtl_id": ["should be a valid GTL id"]},
        )

    def when_sending_an_ean_that_is_not_made_of_13_digits(self, client):
        self._assert_patch_is_rejected(
            client,
            offer_data={"subcategoryId": subcategories.LIVRE_PAPIER.id, "url": None},
            patch_body={"extraData": {"ean": "123"}},
            expected_response_json={"ean": ["L'EAN doit être composé de 13 chiffres"]},
        )

    def when_unsetting_the_name(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"name": None},
            expected_response_json={"name": ["cannot be null"]},
        )

    def when_sending_an_invalid_booking_email(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"bookingEmail": "not-an-email"},
            expected_response_json={"bookingEmail": ["Saisissez un email valide"]},
        )

    def when_sending_an_invalid_booking_contact(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"bookingContact": "not-an-email"},
            expected_response_json={"bookingContact": ["Saisissez un email valide"]},
        )

    def when_sending_a_withdrawal_type_outside_of_the_enum(self, client):
        self._assert_patch_is_rejected(
            client,
            patch_body={"withdrawalType": "by_carrier_pigeon"},
            expected_response_json={
                "withdrawalType": ["Input should be 'by_email', 'in_app', 'no_ticket' or 'on_site'"]
            },
        )

    def when_trying_to_change_the_withdrawalType_of_a_synchronized_offer(self, client):
        provider = providers_factories.PublicApiProviderFactory()
        providers_factories.OffererProviderFactory(provider=provider)
        offer = offers_factories.EventOfferFactory(
            lastProviderId=provider.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        response = client.with_session_auth("user@example.com").patch(
            f"offers/{offer.id}",
            json={"withdrawalType": "no_ticket"},
        )

        assert response.status_code == 400
        assert response.json == {"withdrawalType": ["Vous ne pouvez pas modifier ce champ"]}

    def when_trying_to_change_a_non_editable_field_of_an_allocine_offer(self, client):
        venue = offerers_factories.VenueFactory()
        allocine_provider = providers_factories.AllocineProviderFactory()
        offer = offers_factories.OfferFactory(
            venue=venue,
            lastProvider=allocine_provider,
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="Film",
            durationMinutes=90,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"durationMinutes": 120}
        )

        assert response.status_code == 400
        assert response.json == {"durationMinutes": ["Vous ne pouvez pas modifier ce champ"]}
        assert db.session.get(Offer, offer.id).durationMinutes == 90

    def when_removing_the_url_of_an_online_only_offer(self, client):
        offer = offers_factories.DigitalOfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            url="https://example.com/streaming",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"url": None}
        )

        assert response.status_code == 400
        assert response.json == {
            "url": [
                f'Une offre de catégorie "{subcategories.ABO_PLATEFORME_VIDEO.pro_label}" doit contenir un champ `url`'
            ]
        }
        assert db.session.get(Offer, offer.id).url == "https://example.com/streaming"

    def when_setting_an_url_on_an_offline_only_offer(self, client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, url=None)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"url": "https://example.com/escape"}
        )

        assert response.status_code == 400
        assert response.json == {
            "url": [
                f'Une offre de sous-catégorie "{subcategories.ESCAPE_GAME.pro_label}" ne peut contenir un champ `url`'
            ]
        }
        assert db.session.get(Offer, offer.id).url is None

    def when_setting_a_location_on_a_digital_offer(self, client):
        offer = offers_factories.DigitalOfferFactory(
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            url="https://example.com/streaming",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "location": {
                "street": "1 rue de la paix",
                "city": "Paris",
                "postalCode": "75102",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "banId": "75102_7560_00001",
                "inseeCode": "75102",
                "label": None,
                "isManualEdition": True,
                "isVenueLocation": False,
            }
        }
        with patch(
            "pcapi.connectors.api_adresse.get_municipality_centroid",
            return_value=api_adresse.AddressInfo(
                id="75102",
                label="Paris",
                postcode="75102",
                citycode="75102",
                latitude=48.8566,
                longitude=2.3522,
                score=0.9,
                city="Paris",
                street="unused",
            ),
        ):
            response = client.with_session_auth("user@example.com").patch(
                self.endpoint.format(offer_id=offer.id), json=data
            )

        assert response.status_code == 400
        assert response.json == {"offererAddress": ["Une offre numérique ne peut pas avoir d'adresse"]}
        assert db.session.get(Offer, offer.id).offererAddress is None

    def when_the_venue_activity_does_not_allow_cultural_outreach(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.RECORD_STORE
        )
        offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.ESCAPE_GAME.id)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"hasCulturalOutreachClaim": True}
        )

        assert response.status_code == 400
        assert response.json == {
            "global": ["L'activité principale de la structure ne permet pas de déclarer une action de médiation"]
        }
        assert db.session.get(Offer, offer.id).culturalOutreach is None

    def when_trying_to_change_a_non_editable_field_of_an_offer_from_a_generic_provider(self, client):
        provider = providers_factories.ProviderFactory()
        offer = offers_factories.EventOfferFactory(lastProvider=provider, isDuo=False)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"isDuo": True}
        )

        assert response.status_code == 400
        assert response.json == {"isDuo": ["Vous ne pouvez pas modifier ce champ"]}
        assert db.session.get(Offer, offer.id).isDuo is False

    @pytest.mark.parametrize(
        "patch_body, expected_error_key",
        [
            ({"unknownField": "whatever"}, "unknownField"),
            ({"durationMinutes": "not-an-int"}, "durationMinutes"),
            ({"isDuo": "not-a-bool"}, "isDuo"),
        ],
    )
    def when_the_body_does_not_match_the_schema(self, patch_body, expected_error_key, client, venue, auth_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue)

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=patch_body)

        assert response.status_code == 400
        assert expected_error_key in response.json

    @pytest.mark.parametrize(
        "location",
        [
            # city is missing
            {"street": "1 rue de la paix", "postalCode": "75102", "latitude": 48.8566, "longitude": 2.3522},
            # postal code is not a french one
            {
                "street": "1 rue de la paix",
                "city": "Paris",
                "postalCode": "AB",
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
        ],
    )
    def when_the_location_is_invalid(self, location, client, venue, auth_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue)

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"location": location})

        assert response.status_code == 400

    def when_removing_the_url_of_an_offer_that_has_no_address(self, client, venue, auth_client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
            venue=venue,
            url="https://example.com/offer",
            offererAddress=None,
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"url": None})

        assert response.status_code == 400
        assert response.json == {"offererAddress": ["Une offre physique doit avoir une adresse"]}
        assert db.session.get(Offer, offer.id).url == "https://example.com/offer"

    def when_the_update_fails_the_artist_offer_links_are_rolled_back(self, client, venue, auth_client):
        # artist links are upserted before most of the validations: the whole
        # request must be rolled back when a later check fails.
        artist = artist_factories.ArtistFactory()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONCERT.id, venue=venue, name="Un nom")

        data = {
            "artistOfferLinks": [{"artistId": artist.id, "artistType": "performer", "artistName": artist.name}],
            "name": None,
        }
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 400
        assert response.json == {"name": ["cannot be null"]}
        assert db.session.query(artist_models.ArtistOfferLink).filter_by(offer_id=offer.id).count() == 0
        assert db.session.get(Offer, offer.id).name == "Un nom"

    def when_the_update_fails_the_cultural_outreach_claim_is_rolled_back(self, client):
        # the claim is created before most of the validations: the whole
        # request must be rolled back when a later check fails.
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.MUSEUM
        )
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue, name="Un nom")

        data = {"hasCulturalOutreachClaim": True, "name": None}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 400
        assert response.json == {"name": ["cannot be null"]}
        assert db.session.get(Offer, offer.id).culturalOutreach is None
        assert db.session.get(Offer, offer.id).name == "Un nom"

    def should_fail_when_trying_to_update_offer_with_product_with_new_ean(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean="1111111111111",
            name="New name",
            description="description",
        )
        offer = offers_factories.OfferFactory(
            venue=venue,
            url="test@test.com",
            product=product,
        )

        data = {"extraData": {"ean": "2222222222222"}}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 400
        assert response.json == {"ean": ["Vous ne pouvez pas modifier ce champ"]}

    def should_fail_when_updating_a_non_ean_extra_data_of_an_offer_with_a_product(self, client, venue, auth_client):
        # no extraData of an offer with a product can be changed, not only its EAN
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean="1111111111111",
            name="New name",
            description="description",
        )
        offer = offers_factories.OfferFactory(venue=venue, product=product, extraData={})

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id), json={"extraData": {"author": "Kewis Larol"}}
        )

        assert response.status_code == 400
        assert response.json == {"extraData": ["Vous ne pouvez pas modifier ce champ"]}
        assert db.session.get(Offer, offer.id).extraData == {}

    def when_only_the_venue_provider_has_a_ticketing_service(self, client, venue, auth_client):
        # the route does not pass any venue_provider to `update_offer`, so
        # `check_offer_withdrawal` only ever looks at the offer provider: a
        # ticketing service set at the venue level does not unlock `in_app`.
        venue_provider = providers_factories.VenueProviderFactory(venue=venue)
        providers_factories.VenueProviderExternalUrlsFactory(venueProvider=venue_provider)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            url=None,
            bookingContact="booking@conta.ct",
            withdrawalType=WithdrawalTypeEnum.NO_TICKET,
        )

        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json={"withdrawalType": "in_app"})

        assert response.status_code == 400
        assert response.json == {
            "offer": ["Vous devez supporter l'interface de billeterie pour créer des offres avec billet"]
        }
        assert db.session.get(Offer, offer.id).withdrawalType == WithdrawalTypeEnum.NO_TICKET

    @patch("pcapi.core.search.async_index_offer_ids")
    def when_the_update_fails_the_offer_is_not_reindexed(
        self, mocked_async_index_offer_ids, client, venue, auth_client
    ):
        # the indexation is scheduled with `on_commit`: a rolled back request
        # must not reach the search index.
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ESCAPE_GAME.id, venue=venue, name="Un nom")

        data = {"name": "Un autre nom", "audioDisabilityCompliant": None}
        response = auth_client.patch(self.endpoint.format(offer_id=offer.id), json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["L’accessibilité de l’offre doit être définie"]}
        assert db.session.get(Offer, offer.id).name == "Un nom"
        mocked_async_index_offer_ids.assert_not_called()

    def test_returns_400_if_ean_already_exists_in_same_venue(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        ean = "1234567890123"
        offers_factories.OfferFactory(venue=venue, ean=ean)
        offer2 = offers_factories.OfferFactory(venue=venue, ean="9876543210987")

        data = {"extraData": {"ean": ean}}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer2.id), json=data
        )

        assert response.status_code == 400
        assert "ean" in response.json
        assert "Une offre avec cet EAN existe déjà" in response.json["ean"][0]

    def test_returns_400_if_updating_forbidden_field_on_imported_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        provider = providers_factories.ProviderFactory(localClass="TiteliveMusicProvider")
        offer = offers_factories.OfferFactory(venue=venue, lastProvider=provider)

        # bookingEmail is not in EDITABLE_FIELDS_FOR_OFFER_FROM_PROVIDER
        data = {"bookingEmail": "test@example.com"}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 400
        assert "bookingEmail" in response.json
        assert "Vous ne pouvez pas modifier ce champ" in response.json["bookingEmail"][0]

    def when_updating_a_read_only_field_of_a_synchronized_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, activity=offerers_models.Activity.PERFORMANCE_HALL
        )
        offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=providers_factories.ProviderFactory(),
            name="Un nom",
            isDuo=False,
        )

        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"name": "Un autre nom", "isDuo": True}
        )

        assert response.status_code == 400
        assert response.json == {
            "isDuo": ["Vous ne pouvez pas modifier ce champ"],
            "name": ["Vous ne pouvez pas modifier ce champ"],
        }
        assert db.session.get(Offer, offer.id).name == "Un nom"

    def when_updating_a_read_only_field_of_a_product_based_offer(self, client, venue, auth_client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer = offers_factories.OfferFactory(venue=venue, product=product)

        response = auth_client.patch(
            self.endpoint.format(offer_id=offer.id), json={"description": "Une autre description."}
        )

        assert response.status_code == 400
        assert response.json == {"description": ["Vous ne pouvez pas modifier ce champ"]}


class Returns401Test:
    endpoint = "/offers/{offer_id}"

    def when_user_is_not_logged_in(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.ESCAPE_GAME.id,
            name="Old name",
        )

        response = client.patch(self.endpoint.format(offer_id=offer.id), json={"name": "New name"})

        assert response.status_code == 401
        assert db.session.get(Offer, offer.id).name == "Old name"


class Returns404Test:
    endpoint = "/offers/{offer_id}"

    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            name="Old name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            url="test@test.com",
            description="description",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        # Then
        assert response.status_code == 404
        assert response.json["global"] == [OBJECT_NOT_FOUND_ERROR_MESSAGE]
        assert db.session.get(Offer, offer.id).name == "Old name"

    @pytest.mark.parametrize(
        "user_offerer_factory_name",
        ["NewUserOffererFactory", "PendingUserOffererFactory", "RejectedUserOffererFactory"],
    )
    def when_the_user_offerer_link_is_not_validated(self, user_offerer_factory_name, app, client):
        offer = offers_factories.OfferFactory(
            name="Old name",
            subcategoryId=subcategories.ESCAPE_GAME.id,
        )
        user_offerer_factory = getattr(offerers_factories, user_offerer_factory_name)
        user_offerer = user_offerer_factory(offerer=offer.venue.managingOfferer)

        response = client.with_session_auth(user_offerer.user.email).patch(
            self.endpoint.format(offer_id=offer.id), json={"name": "New name"}
        )

        assert response.status_code == 404
        assert response.json["global"] == [OBJECT_NOT_FOUND_ERROR_MESSAGE]
        assert db.session.get(Offer, offer.id).name == "Old name"

    def test_returns_404_if_offer_does_not_exist(self, app, client):
        # given
        users_factories.UserFactory(email="user@example.com")

        # when
        response = client.with_session_auth("user@example.com").patch(self.endpoint.format(offer_id=123456789), json={})

        # then
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    def test_returns_404_if_user_has_no_access_to_offerer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="authorized@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        users_factories.UserFactory(email="unauthorized@example.com")

        response = client.with_session_auth("unauthorized@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json={"name": "New Name"}
        )

        assert response.status_code == 404


@pytest.fixture(name="user_offerer")
def user_offerer_fixture():
    return offerers_factories.UserOffererFactory(user__email="user@example.com")


@pytest.fixture(name="venue")
def venue_fixture(user_offerer):
    return offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)


@pytest.fixture(name="auth_client")
def auth_client_fixture(user_offerer, client):
    return client.with_session_auth(user_offerer.user.email)
