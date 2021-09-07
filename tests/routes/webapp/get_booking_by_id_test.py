import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_expect_booking_to_have_completed_url(self, app):
        # Given
        user = BeneficiaryGrant18Factory(email="user@example.com")
        offerer = OffererFactory()
        product = ThingProductFactory()
        offer = ThingOfferFactory(
            url="https://host/path/{token}?offerId={offerId}&email={email}",
            audioDisabilityCompliant=None,
            bookingEmail="booking@example.net",
            extraData={"author": "Test Author"},
            mediaUrls=["test/urls"],
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            name="Test Book",
            venue__managingOfferer=offerer,
            product=product,
        )
        stock = ThingStockFactory(offer=offer, price=0, quantity=None)
        booking = BookingFactory(user=user, stock=stock, token="ABCDEF")

        # When
        response = TestClient(app.test_client()).with_session_auth(user.email).get("/bookings/" + humanize(booking.id))

        # Then
        assert response.status_code == 200
        completed_url = "https://host/path/ABCDEF?offerId={}&email=user@example.com".format(humanize(offer.id))

        assert "validationToken" not in response.json["stock"]["offer"]
        assert response.json == {
            "amount": 0.0,
            "cancellationDate": None,
            "cancellationReason": None,
            "completedUrl": completed_url,
            "cancellationLimitDate": None,
            "dateCreated": format_into_utc_date(booking.dateCreated),
            "dateUsed": None,
            "id": humanize(booking.id),
            "isCancelled": False,
            "isEventExpired": False,
            "isUsed": False,
            "mediation": None,
            "offererId": humanize(offer.venue.managingOffererId),
            "quantity": 1,
            "stock": {
                "beginningDatetime": None,
                "bookingLimitDatetime": None,
                "dateCreated": format_into_utc_date(stock.dateCreated),
                "dateModified": format_into_utc_date(stock.dateModified),
                "dateModifiedAtLastProvider": format_into_utc_date(stock.dateModifiedAtLastProvider),
                "fieldsUpdated": [],
                "id": humanize(stock.id),
                "idAtProviders": None,
                "isBookable": True,
                "isEventExpired": False,
                "isSoftDeleted": False,
                "lastProviderId": None,
                "offer": {
                    "ageMax": None,
                    "ageMin": None,
                    "audioDisabilityCompliant": None,
                    "bookingEmail": "booking@example.net",
                    "conditions": None,
                    "dateCreated": format_into_utc_date(offer.dateCreated),
                    "dateModifiedAtLastProvider": format_into_utc_date(offer.dateModifiedAtLastProvider),
                    "description": product.description,
                    "durationMinutes": None,
                    "externalTicketOfficeUrl": None,
                    "extraData": {"author": "Test Author"},
                    "fieldsUpdated": [],
                    "hasBookingLimitDatetimesPassed": False,
                    "id": humanize(offer.id),
                    "idAtProviders": offer.idAtProviders,
                    "isActive": True,
                    "isBookable": True,
                    "isDigital": True,
                    "isDuo": False,
                    "isEducational": False,
                    "isEvent": False,
                    "isNational": False,
                    "lastProviderId": None,
                    "mediaUrls": ["test/urls"],
                    "mentalDisabilityCompliant": None,
                    "motorDisabilityCompliant": None,
                    "name": "Test Book",
                    "offerType": {
                        "appLabel": "Film",
                        "canExpire": True,
                        "conditionalFields": [],
                        "description": (
                            "Action, science-fiction, documentaire ou comédie "
                            "sentimentale ? En salle, en plein air ou bien au chaud "
                            "chez soi ? Et si c’était plutôt cette exposition qui "
                            "allait faire son cinéma ?"
                        ),
                        "isActive": True,
                        "offlineOnly": False,
                        "onlineOnly": False,
                        "proLabel": "Audiovisuel - films sur supports physiques et VOD",
                        "sublabel": "Regarder",
                        "type": "Thing",
                        "value": "ThingType.AUDIOVISUEL",
                    },
                    "productId": humanize(offer.product.id),
                    "stocks": [
                        {
                            "beginningDatetime": None,
                            "bookingLimitDatetime": None,
                            "dateCreated": format_into_utc_date(stock.dateCreated),
                            "dateModified": format_into_utc_date(stock.dateModified),
                            "dateModifiedAtLastProvider": format_into_utc_date(stock.dateModifiedAtLastProvider),
                            "fieldsUpdated": [],
                            "id": humanize(stock.id),
                            "idAtProviders": None,
                            "isBookable": True,
                            "isEventExpired": False,
                            "isSoftDeleted": False,
                            "lastProviderId": None,
                            "offerId": humanize(offer.id),
                            "price": 0.0,
                            "quantity": None,
                            "remainingQuantity": "unlimited",
                        }
                    ],
                    "subcategoryId": "SUPPORT_PHYSIQUE_FILM",
                    "thumbUrl": None,
                    "type": "ThingType.AUDIOVISUEL",
                    "url": "https://host/path/{token}?offerId={offerId}&email={email}",
                    "validation": "APPROVED",
                    "venue": {
                        "address": "1 boulevard Poissonnière",
                        "audioDisabilityCompliant": None,
                        "bookingEmail": None,
                        "city": "Paris",
                        "comment": None,
                        "dateCreated": format_into_utc_date(offer.venue.dateCreated),
                        "dateModifiedAtLastProvider": format_into_utc_date(offer.venue.dateModifiedAtLastProvider),
                        "departementCode": "75",
                        "description": offer.venue.description,
                        "fieldsUpdated": [],
                        "id": humanize(offer.venue.id),
                        "idAtProviders": None,
                        "isPermanent": True,
                        "isVirtual": False,
                        "lastProviderId": None,
                        "latitude": 48.87004,
                        "longitude": 2.3785,
                        "managingOffererId": humanize(offer.venue.managingOffererId),
                        "mentalDisabilityCompliant": None,
                        "motorDisabilityCompliant": None,
                        "name": offer.venue.name,
                        "postalCode": "75000",
                        "publicName": offer.venue.publicName,
                        "siret": offer.venue.siret,
                        "thumbCount": 0,
                        "venueLabelId": None,
                        "venueTypeId": None,
                        "visualDisabilityCompliant": None,
                        "venueTypeCode": "OTHER",
                        "withdrawalDetails": None,
                    },
                    "venueId": humanize(offer.venue.id),
                    "visualDisabilityCompliant": False,
                    "withdrawalDetails": None,
                },
                "offerId": humanize(offer.id),
                "price": 0.0,
                "quantity": None,
                "remainingQuantity": "unlimited",
            },
            "stockId": humanize(stock.id),
            "token": booking.token,
            "userId": humanize(user.id),
            "venueId": humanize(offer.venue.id),
        }
