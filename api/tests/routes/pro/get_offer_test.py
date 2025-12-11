from datetime import date
from datetime import datetime
from datetime import timedelta

import pytest
import time_machine

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.highlights.factories as highlights_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    # get user_session + user
    # get offer
    # get artist
    # check user_offerer exists
    # rollback
    # rollback
    num_queries = 6

    def test_access_by_beneficiary(self, client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory()

        auth_client = client.with_session_auth(email=beneficiary.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = 1  # session + user
    num_queries += 1  # payload (joined query)
    num_queries += 1  # get artist
    num_queries += 1  # user offerer

    def test_access_by_pro_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        assert "iban" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
        assert "thumbUrl" in response_json
        assert response_json["id"] == offer.id

    def test_returns_an_active_mediation(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        mediation = offers_factories.MediationFactory(offer=offer)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert f"/thumbs/mediations/{humanize(mediation.id)}" in response.json["activeMediation"]["thumbUrl"]

    @time_machine.travel("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, client):
        ean = "1111111111111"
        now = datetime(2020, 10, 15)
        user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=now,
            offerer__siren="123456789",
            offerer__name="Test Offerer",
        )
        meta_data = offers_factories.OfferMetaDataFactory(videoUrl="https://www.youtube.com/watch?v=WtM4OW2qVjY")
        offer = offers_factories.EventOfferFactory(
            dateCreated=now,
            dateModifiedAtLastProvider=now,
            bookingEmail="offer.booking.email@example.com",
            name="Derrick",
            description="Tatort, but slower",
            durationMinutes=60,
            ean=ean,
            extraData=None,
            mentalDisabilityCompliant=True,
            externalTicketOfficeUrl="http://example.net",
            withdrawalDetails="Veuillez chercher votre billet au guichet",
            withdrawalType=WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
            venue__siret="12345678912345",
            venue__name="La petite librairie",
            venue__dateCreated=now,
            venue__bookingEmail="test@test.com",
            venue__managingOfferer=user_offerer.offerer,
            offererAddress=None,
            publicationDatetime=datetime(year=2020, month=10, day=1),
            bookingAllowedDatetime=datetime(year=2020, month=12, day=15),
            metaData=meta_data,
        )

        stock = offers_factories.EventStockFactory(
            offer=offer,
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=now + timedelta(hours=1),
            bookingLimitDatetime=now + timedelta(hours=1),
            priceCategory__priceCategoryLabel__label="Au pied du mur",
        )
        venue = offer.venue
        offerer = venue.managingOfferer

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json == {
            "activeMediation": None,
            "artistOfferLinks": [],
            "bookingContact": None,
            "bookingsCount": 0,
            "bookingEmail": "offer.booking.email@example.com",
            "dateCreated": "2020-10-15T00:00:00Z",
            "productId": None,
            "publicationDate": "2020-10-01T00:00:00Z",
            "publicationDatetime": "2020-10-01T00:00:00Z",
            "bookingAllowedDatetime": "2020-12-15T00:00:00Z",
            "description": "Tatort, but slower",
            "durationMinutes": 60,
            "extraData": {"ean": "1111111111111"},
            "externalTicketOfficeUrl": "http://example.net",
            "hasBookingLimitDatetimesPassed": False,
            "hasPendingBookings": False,
            "hasStocks": True,
            "highlightRequests": [],
            "isActive": True,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "isDigital": False,
            "isDuo": False,
            "isEditable": True,
            "isEvent": True,
            "canBeEvent": True,
            "isHeadlineOffer": False,
            "isNational": False,
            "isThing": False,
            "lastProvider": None,
            "name": "Derrick",
            "id": stock.offer.id,
            "status": "PUBLISHED",
            "isNonFreeOffer": None,
            "priceCategories": [{"label": "Au pied du mur", "price": 10.1, "id": stock.priceCategoryId}],
            "subcategoryId": "SEANCE_CINE",
            "thumbUrl": None,
            "url": None,
            "location": {
                "label": venue.common_name,
                "id": venue.offererAddress.address.id,
                "banId": venue.offererAddress.address.banId,
                "departmentCode": venue.offererAddress.address.departmentCode,
                "inseeCode": venue.offererAddress.address.inseeCode,
                "city": venue.offererAddress.address.city,
                "latitude": float(venue.offererAddress.address.latitude),
                "longitude": float(venue.offererAddress.address.longitude),
                "postalCode": venue.offererAddress.address.postalCode,
                "street": venue.offererAddress.address.street,
                "isManualEdition": venue.offererAddress.address.isManualEdition,
                "isVenueLocation": True,
            },
            "venue": {
                "street": venue.offererAddress.address.street,
                "audioDisabilityCompliant": False,
                "bookingEmail": "test@test.com",
                "city": venue.offererAddress.address.city,
                "departementCode": venue.offererAddress.address.departmentCode,
                "id": venue.id,
                "managingOfferer": {
                    "id": offerer.id,
                    "name": "Test Offerer",
                },
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "name": "La petite librairie",
                "postalCode": venue.offererAddress.address.postalCode,
                "publicName": "La petite librairie",
                "visualDisabilityCompliant": False,
                "isVirtual": False,
            },
            "videoData": {
                "videoDuration": None,
                "videoExternalId": None,
                "videoThumbnailUrl": None,
                "videoTitle": None,
                "videoUrl": "https://www.youtube.com/watch?v=WtM4OW2qVjY",
            },
            "withdrawalDetails": "Veuillez chercher votre billet au guichet",
            "withdrawalType": "on_site",
            "withdrawalDelay": 60 * 30,
        }

    @time_machine.travel("2019-10-15 00:00:00")
    def test_returns_a_thing_stock(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer = offers_factories.OfferFactory(
            product=product, venue__managingOfferer=user_offerer.offerer, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer)
        offer_id = offer.id

        client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        data = response.json
        assert data["subcategoryId"] == "LIVRE_PAPIER"

    def test_returns_a_movie_with_product(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=120)
        offer = offers_factories.OfferFactory(product=product, venue__managingOfferer=user_offerer.offerer)
        offers_factories.EventStockFactory(offer=offer)
        offer_id = offer.id

        client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        data = response.json
        assert data["subcategoryId"] == subcategories.SEANCE_CINE.id

    @time_machine.travel("2019-10-15 00:00:00")
    def test_returns_a_thing_with_activation_code_stock(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            stocks=[offers_factories.StockWithActivationCodesFactory()],
            subcategoryId=subcategories.ABO_PLATEFORME_MUSIQUE.id,
            url="fake-url",
            venue__managingOfferer=user_offerer.offerer,
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        data = response.json
        assert data["subcategoryId"] == "ABO_PLATEFORME_MUSIQUE"
        assert data["hasStocks"] == True

    @time_machine.travel("2020-10-15 00:00:00")
    def test_should_not_return_soft_deleted_stock(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        deleted_stock = offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = deleted_stock.offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["hasStocks"] == False

    def test_returns_positive_booking_count(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.EventStockFactory(offer=offer)
        bookings_factories.BookingFactory.create_batch(2, stock=stock)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["bookingsCount"] == 2
        assert response.json["hasStocks"] == True

    @pytest.mark.parametrize("offer_oa_label", ["label", None, ""])
    def test_return_offer_offerer_address(self, offer_oa_label, client):
        """If offer has an offererAddress, it should be used"""
        user_offerer = offerers_factories.UserOffererFactory()
        offer_offerer_address = offerers_factories.OffererAddressFactory(
            offerer=user_offerer.offerer,
        )
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            offererAddress=offer_offerer_address,
        )
        assert offer.venue.offererAddress != offer.offererAddress

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["location"] == {
            "label": offer_offerer_address.label,
            "id": offer_offerer_address.address.id,
            "banId": offer_offerer_address.address.banId,
            "departmentCode": offer_offerer_address.address.departmentCode,
            "inseeCode": offer_offerer_address.address.inseeCode,
            "city": offer_offerer_address.address.city,
            "latitude": float(offer_offerer_address.address.latitude),
            "longitude": float(offer_offerer_address.address.longitude),
            "postalCode": offer_offerer_address.address.postalCode,
            "street": offer_offerer_address.address.street,
            "isVenueLocation": False,
            "isManualEdition": offer_offerer_address.address.isManualEdition,
        }

    def test_return_venue_offerer_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            offererAddress=None,
        )
        offerer_address = offer.venue.offererAddress
        assert offer.offererAddress is None

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["location"] == {
            "label": offer.venue.common_name,
            "id": offerer_address.address.id,
            "banId": offerer_address.address.banId,
            "departmentCode": offerer_address.address.departmentCode,
            "inseeCode": offerer_address.address.inseeCode,
            "city": offerer_address.address.city,
            "latitude": float(offerer_address.address.latitude),
            "longitude": float(offerer_address.address.longitude),
            "postalCode": offerer_address.address.postalCode,
            "street": offerer_address.address.street,
            "isManualEdition": offerer_address.address.isManualEdition,
            "isVenueLocation": True,
        }

    @time_machine.travel("2020-10-15 00:00:00")
    def test_future_offer(self, client):
        now = date_utils.get_naive_utc_now()
        user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=now,
            offerer__siren="123456789",
            offerer__name="Test Offerer",
        )
        publication_date = now.replace(minute=0, second=0, microsecond=0) + timedelta(days=30)
        offer = offers_factories.EventOfferFactory(
            dateCreated=now,
            dateModifiedAtLastProvider=now,
            bookingEmail="offer.booking.email@example.com",
            name="Derrick",
            description="Tatort, but slower",
            durationMinutes=60,
            extraData=None,
            mentalDisabilityCompliant=True,
            externalTicketOfficeUrl="http://example.net",
            withdrawalDetails="Veuillez chercher votre billet au guichet",
            withdrawalType=WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
            venue__siret="12345678912345",
            venue__name="La petite librairie",
            venue__dateCreated=now,
            venue__bookingEmail="test@test.com",
            venue__managingOfferer=user_offerer.offerer,
            offererAddress=None,
            publicationDatetime=publication_date,
        )
        offer_id = offer.id

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["publicationDate"] == publication_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    @pytest.mark.parametrize("has_pending_bookings", [True, False])
    def test_pending_booking(self, client, has_pending_bookings):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.EventStockFactory(offer=offer)
        if has_pending_bookings:
            bookings_factories.BookingFactory(stock=stock)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["hasPendingBookings"] == has_pending_bookings

    def test_returns_highlight_requests(self, client):
        today = date.today()
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offer_id = offer.id

        highlight = highlights_factories.HighlightFactory()
        highlight_name = highlight.name
        highlight_id = highlight.id
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight)

        highlight2 = highlights_factories.HighlightFactory()
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight2)
        highlight2_name = highlight2.name
        highlight2_id = highlight2.id

        highlight3 = highlights_factories.HighlightFactory(
            highlight_datespan=db_utils.make_inclusive_daterange(
                start=today - timedelta(days=10), end=today - timedelta(days=9)
            )
        )
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight3)

        client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        data = response.json
        assert {"name": highlight_name, "id": highlight_id} in data["highlightRequests"]
        assert {"name": highlight2_name, "id": highlight2_id} in data["highlightRequests"]

    def test_returns_artists_linked_to_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offer_id = offer.id
        artist = artist_factories.ArtistFactory()
        another_artist = artist_factories.ArtistFactory()
        artist_factories.ArtistOfferLinkFactory(
            offer_id=offer_id,
            artist_id=artist.id,
        )
        artist_factories.ArtistOfferLinkFactory(
            offer_id=offer_id,
            artist_id=another_artist.id,
        )
        custom_name = "Simone"
        artist_factories.ArtistOfferLinkFactory(
            offer_id=offer_id,
            custom_name=custom_name,
            artist_type=artist_models.ArtistType.AUTHOR,
        )

        client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}")
            assert response.status_code == 200
        assert len(response.json["artistOfferLinks"]) == 3

        # to avoid flakiness
        assert {"artistId": artist.id, "artistName": artist.name, "artistType": "performer"} in response.json[
            "artistOfferLinks"
        ]
        assert {
            "artistId": another_artist.id,
            "artistName": another_artist.name,
            "artistType": "performer",
        } in response.json["artistOfferLinks"]
        assert {"artistId": None, "artistName": "Simone", "artistType": "author"} in response.json["artistOfferLinks"]
