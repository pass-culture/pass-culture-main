from unittest.mock import patch

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @patch("pcapi.routes.webapp.bookings.FeatureToggle.is_active", return_value=False)
    @pytest.mark.usefixtures("db_session")
    def test_when_user_has_bookings_and_qr_code_feature_is_inactive_does_not_return_qr_code(
        self, qr_code_is_active, app
    ):
        # Given
        user1 = BeneficiaryFactory(email="user1+plus@example.com")
        user2 = BeneficiaryFactory(email="user2+plus@example.com")
        venue = VenueFactory(latitude=None, longitude=None)
        offer = ThingOfferFactory(venue=venue)
        offer2 = ThingOfferFactory()
        stock = ThingStockFactory(offer=offer, price=0, quantity=None)
        stock2 = ThingStockFactory(offer=offer2, price=0)
        booking1 = BookingFactory(user=user1, stock=stock, token="ABCDEF")
        BookingFactory(user=user2, stock=stock, token="GHIJK")
        booking3 = BookingFactory(user=user1, stock=stock2, token="BBBBB")

        # When
        response = TestClient(app.test_client()).with_auth(user1.email).get("/bookings")

        # Then
        assert response.status_code == 200
        bookings = response.json
        assert len(bookings) == 2
        assert {b["id"] for b in bookings} == set(humanize(b.id) for b in {booking1, booking3})
        assert "qrCode" not in bookings[0]
        assert "validationToken" not in bookings[0]["stock"]["offer"]["venue"]
        assert bookings[0]["id"] == humanize(booking1.id)
        assert bookings[0] == {
            "activationCode": None,
            "amount": 0.0,
            "cancellationDate": None,
            "completedUrl": None,
            "dateCreated": format_into_utc_date(booking1.dateCreated),
            "dateUsed": None,
            "displayAsEnded": None,
            "id": humanize(booking1.id),
            "isCancelled": False,
            "isEventExpired": False,
            "isUsed": False,
            "quantity": 1,
            "stock": {
                "beginningDatetime": None,
                "id": humanize(stock.id),
                "isEventExpired": False,
                "offer": {
                    "description": offer.description,
                    "durationMinutes": None,
                    "extraData": offer.extraData,
                    "id": humanize(offer.id),
                    "isBookable": True,
                    "isDigital": False,
                    "isDuo": False,
                    "isEvent": False,
                    "isNational": False,
                    "name": offer.product.name,
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
                        "proLabel": "Audiovisuel - films sur " "supports physiques et VOD",
                        "sublabel": "Regarder",
                        "type": "Thing",
                        "value": "ThingType.AUDIOVISUEL",
                    },
                    "stocks": [
                        {
                            "beginningDatetime": None,
                            "bookingLimitDatetime": None,
                            "dateCreated": format_into_utc_date(stock.dateCreated),
                            "dateModified": format_into_utc_date(stock.dateModified),
                            "id": humanize(stock.id),
                            "isBookable": True,
                            "offerId": humanize(offer.id),
                            "price": 0.0,
                            "quantity": None,
                            "remainingQuantity": "unlimited",
                        }
                    ],
                    "thumbUrl": None,
                    "venue": {
                        "address": venue.address,
                        "city": venue.city,
                        "departementCode": venue.departementCode,
                        "id": humanize(venue.id),
                        "latitude": None,
                        "longitude": None,
                        "name": venue.name,
                        "postalCode": venue.postalCode,
                    },
                    "venueId": humanize(venue.id),
                    "withdrawalDetails": None,
                },
                "offerId": humanize(offer.id),
                "price": 0.0,
            },
            "stockId": humanize(stock.id),
            "token": "ABCDEF",
            "userId": humanize(booking1.userId),
        }

    @patch("pcapi.routes.webapp.bookings.FeatureToggle.is_active", return_value=True)
    @pytest.mark.usefixtures("db_session")
    def when_user_has_bookings_and_qr_code_feature_is_active(self, qr_code_is_active, app):
        # Given
        user1 = BeneficiaryFactory(email="user1+plus@example.com")
        user2 = BeneficiaryFactory(email="user2+plus@example.com")
        venue = VenueFactory(latitude=None, longitude=None)
        offer = ThingOfferFactory(venue=venue)
        offer2 = ThingOfferFactory()
        stock = ThingStockFactory(offer=offer, price=0, quantity=None)
        stock2 = ThingStockFactory(offer=offer2, price=0)
        BookingFactory(user=user1, stock=stock, token="ABCDEF")
        BookingFactory(user=user2, stock=stock, token="GHIJK")
        BookingFactory(user=user1, stock=stock2, token="BBBBB")

        # When
        response = TestClient(app.test_client()).with_auth(user1.email).get("/bookings")

        # Then
        all_bookings = response.json
        assert len(all_bookings) == 2
        first_booking = all_bookings[0]
        assert response.status_code == 200
        assert "qrCode" in first_booking
        assert "completedUrl" in first_booking
        assert "isEventExpired" in first_booking
        assert "offer" in first_booking["stock"]
        assert "isEventExpired" in first_booking["stock"]
        assert "isDigital" in first_booking["stock"]["offer"]
        assert "isEvent" in first_booking["stock"]["offer"]
        assert "offerType" in first_booking["stock"]["offer"]
        assert "thumbUrl" in first_booking["stock"]["offer"]
        assert "stocks" in first_booking["stock"]["offer"]
        assert "venue" in first_booking["stock"]["offer"]
        assert "validationToken" not in first_booking["stock"]["offer"]["venue"]
