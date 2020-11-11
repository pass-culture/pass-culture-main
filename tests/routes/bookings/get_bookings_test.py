from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Get:
    class Returns200:
        @patch("pcapi.routes.bookings.feature_queries.is_active", return_value=False)
        @pytest.mark.usefixtures("db_session")
        def when_user_has_bookings_and_qr_code_feature_is_inactive_does_not_return_qr_code(
            self, qr_code_is_active, app
        ):
            # Given
            user1 = create_user(email="user1+plus@example.com")
            user2 = create_user(email="user2+plus@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock(offer=offer, price=0)
            offer2 = create_offer_with_thing_product(venue)
            stock2 = create_stock(offer=offer2, price=0)
            booking1 = create_booking(user=user1, stock=stock, token="ABCDEF", venue=venue)
            booking2 = create_booking(user=user2, stock=stock, token="GHIJK", venue=venue)
            booking3 = create_booking(user=user1, stock=stock2, token="BBBBB", venue=venue)

            repository.save(booking1, booking2, booking3)

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
                "amount": 0.0,
                "cancellationDate": None,
                "completedUrl": None,
                "dateCreated": format_into_utc_date(booking1.dateCreated),
                "dateUsed": None,
                "id": humanize(booking1.id),
                "isCancelled": False,
                "isEventExpired": False,
                "isUsed": False,
                "quantity": 1,
                "recommendationId": None,
                "stock": {
                    "beginningDatetime": None,
                    "id": humanize(stock.id),
                    "isEventExpired": False,
                    "offer": {
                        "description": None,
                        "durationMinutes": None,
                        "extraData": {"author": "Test Author"},
                        "id": humanize(offer.id),
                        "isBookable": True,
                        "isDigital": False,
                        "isDuo": False,
                        "isEvent": False,
                        "isNational": False,
                        "name": "Test Book",
                        "offerType": {
                            "appLabel": "Film",
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
                            "address": "123 rue de Paris",
                            "city": "Montreuil",
                            "departementCode": "93",
                            "id": humanize(venue.id),
                            "latitude": None,
                            "longitude": None,
                            "name": "La petite librairie",
                            "postalCode": "93100",
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

        @patch("pcapi.routes.bookings.feature_queries.is_active", return_value=True)
        @pytest.mark.usefixtures("db_session")
        def when_user_has_bookings_and_qr_code_feature_is_active(self, qr_code_is_active, app):
            # Given
            user1 = create_user(email="user1+plus@example.com")
            user2 = create_user(email="user2+plus@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer=offerer)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, offer=offer, price=0)
            offer2 = create_offer_with_thing_product(venue)
            stock2 = create_stock_with_thing_offer(offerer=offerer, venue=venue, offer=offer2, price=0)
            booking1 = create_booking(user=user1, stock=stock, venue=venue, token="ABCDEF")
            booking2 = create_booking(user=user2, stock=stock, venue=venue, token="GHIJK")
            booking3 = create_booking(user=user1, stock=stock2, venue=venue, token="BBBBB")

            repository.save(booking1, booking2, booking3)

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
