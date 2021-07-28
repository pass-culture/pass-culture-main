from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from pcapi.domain.beneficiary_bookings.beneficiary_booking import BeneficiaryBooking
from pcapi.domain.beneficiary_bookings.beneficiary_bookings_with_stocks import BeneficiaryBookingsWithStocks
from pcapi.domain.beneficiary_bookings.stock import Stock
from pcapi.routes.serialization.beneficiary_bookings_serialize import serialize_beneficiary_bookings


class BeneficiaryBookingsSerializeTest:
    class SerializeBeneficiaryBookingsTest:
        @freeze_time("2019-1-1")
        def test_should_return_expected_json_without_qr_code(self):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=34,
                    offerId=45,
                    price=10.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=False,
                    isOfferActive=True,
                )
            ]

            beneficiary_booking = BeneficiaryBooking(
                amount=12,
                cancellationDate=datetime(2019, 3, 12),
                dateCreated=datetime(2019, 2, 7),
                dateUsed=datetime(2019, 4, 7),
                id=4,
                isCancelled=False,
                isUsed=True,
                quantity=2,
                stockId=56,
                token="TOKEN",
                userId=12,
                offerId=45,
                name="Ma super offre",
                type="EventType.PRATIQUE_ARTISTIQUE",
                url="http://url.com",
                email="john@example.com",
                beginningDatetime=datetime(2019, 3, 8),
                venueId=87,
                departementCode="70",
                withdrawalDetails=None,
                isDuo=True,
                extraData={"isbn": "9876543678"},
                durationMinutes=180,
                description="Ma super decription",
                isNational=False,
                mediaUrls=[],
                venueName="Théâtre",
                address="5 rue du cinéma",
                postalCode="70200",
                city="Lure",
                latitude=9.45678,
                longitude=45.0987654,
                price=12.89,
                productId=12,
                thumbCount=1,
                active_mediations=[],
                displayAsEnded=False,
                activationCode=None,
            )
            beneficiary_bookings = BeneficiaryBookingsWithStocks(bookings=[beneficiary_booking], stocks=stocks)

            # When
            serialized_beneficiary_booking = serialize_beneficiary_bookings(
                beneficiary_bookings=beneficiary_bookings, with_qr_code=False
            )

            # Then
            assert serialized_beneficiary_booking == [
                {
                    "activationCode": None,
                    "amount": 12,
                    "cancellationDate": "2019-03-12T00:00:00Z",
                    "completedUrl": "http://url.com",
                    "dateCreated": "2019-02-07T00:00:00Z",
                    "dateUsed": "2019-04-07T00:00:00Z",
                    "id": "AQ",
                    "isCancelled": False,
                    "isEventExpired": False,
                    "isUsed": True,
                    "quantity": 2,
                    "displayAsEnded": False,
                    "stock": {
                        "beginningDatetime": "2019-03-08T00:00:00Z",
                        "id": "HA",
                        "isEventExpired": False,
                        "offer": {
                            "description": "Ma super decription",
                            "durationMinutes": 180,
                            "extraData": {"isbn": "9876543678"},
                            "id": "FU",
                            "isDigital": True,
                            "isDuo": True,
                            "isEvent": True,
                            "isNational": False,
                            "name": "Ma super offre",
                            "isBookable": True,
                            "offerType": {
                                "appLabel": "Pratique artistique",
                                "conditionalFields": ["speaker"],
                                "description": "Jamais osé monter sur les "
                                "planches ? Tenter "
                                "d’apprendre la guitare, le "
                                "piano ou la photographie ? "
                                "Partir cinq jours découvrir "
                                "un autre monde ? Bricoler "
                                "dans un fablab, ou pourquoi "
                                "pas, enregistrer votre "
                                "premier titre ?",
                                "isActive": True,
                                "offlineOnly": True,
                                "onlineOnly": False,
                                "proLabel": "Pratique artistique - séances " "d'essai et stages ponctuels",
                                "sublabel": "Pratiquer",
                                "type": "Event",
                                "value": "EventType.PRATIQUE_ARTISTIQUE",
                            },
                            "stocks": [
                                {
                                    "beginningDatetime": "2019-01-07T00:00:00Z",
                                    "bookingLimitDatetime": "2019-02-07T00:00:00Z",
                                    "dateCreated": "2019-01-05T00:00:00Z",
                                    "dateModified": "2019-01-07T00:00:00Z",
                                    "id": "AE",
                                    "offerId": "FU",
                                    "price": 10.99,
                                    "quantity": 34,
                                    "isBookable": True,
                                    "remainingQuantity": "unlimited",
                                }
                            ],
                            "thumbUrl": "http://localhost/storage/thumbs/products/BQ",
                            "venue": {
                                "address": "5 rue du cinéma",
                                "city": "Lure",
                                "departementCode": "70",
                                "id": "K4",
                                "latitude": 9.45678,
                                "longitude": 45.0987654,
                                "name": "Théâtre",
                                "postalCode": "70200",
                            },
                            "venueId": "K4",
                            "withdrawalDetails": None,
                        },
                        "offerId": "FU",
                        "price": 12.89,
                    },
                    "stockId": "HA",
                    "token": "TOKEN",
                    "userId": "BQ",
                }
            ]

        @freeze_time("2019-1-1")
        @patch("pcapi.core.bookings.api.generate_qr_code", return_value="fake_qr_code")
        def test_should_return_expected_json_with_qr_code(self, mock_generate_qr_code):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=34,
                    offerId=45,
                    price=10.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=False,
                    isOfferActive=True,
                )
            ]

            beneficiary_booking = BeneficiaryBooking(
                amount=12,
                cancellationDate=datetime(2019, 3, 12),
                dateCreated=datetime(2019, 2, 7),
                dateUsed=datetime(2019, 4, 7),
                id=4,
                isCancelled=False,
                isUsed=True,
                quantity=2,
                stockId=56,
                token="TOKEN",
                userId=12,
                offerId=45,
                name="Ma super offre",
                type="EventType.PRATIQUE_ARTISTIQUE",
                url="http://url.com",
                email="john@example.com",
                beginningDatetime=datetime(2019, 3, 8),
                venueId=87,
                departementCode="70",
                withdrawalDetails=None,
                isDuo=True,
                extraData={"isbn": "9876543678"},
                durationMinutes=180,
                description="Ma super decription",
                isNational=False,
                mediaUrls=[],
                venueName="Théâtre",
                address="5 rue du cinéma",
                postalCode="70200",
                city="Lure",
                latitude=9.45678,
                longitude=45.0987654,
                price=12.89,
                productId=12,
                thumbCount=1,
                active_mediations=[],
                displayAsEnded=False,
                activationCode=None,
            )
            beneficiary_bookings = BeneficiaryBookingsWithStocks(bookings=[beneficiary_booking], stocks=stocks)

            # When
            serialized_beneficiary_booking = serialize_beneficiary_bookings(
                beneficiary_bookings=beneficiary_bookings, with_qr_code=True
            )

            # Then
            assert serialized_beneficiary_booking == [
                {
                    "activationCode": None,
                    "amount": 12,
                    "cancellationDate": "2019-03-12T00:00:00Z",
                    "completedUrl": "http://url.com",
                    "dateCreated": "2019-02-07T00:00:00Z",
                    "dateUsed": "2019-04-07T00:00:00Z",
                    "id": "AQ",
                    "isCancelled": False,
                    "isEventExpired": False,
                    "isUsed": True,
                    "qrCode": "fake_qr_code",
                    "quantity": 2,
                    "displayAsEnded": False,
                    "stock": {
                        "beginningDatetime": "2019-03-08T00:00:00Z",
                        "id": "HA",
                        "isEventExpired": False,
                        "offer": {
                            "description": "Ma super decription",
                            "durationMinutes": 180,
                            "extraData": {"isbn": "9876543678"},
                            "id": "FU",
                            "isDigital": True,
                            "isDuo": True,
                            "isEvent": True,
                            "isNational": False,
                            "name": "Ma super offre",
                            "isBookable": True,
                            "offerType": {
                                "appLabel": "Pratique artistique",
                                "conditionalFields": ["speaker"],
                                "description": "Jamais osé monter sur les "
                                "planches ? Tenter "
                                "d’apprendre la guitare, le "
                                "piano ou la photographie ? "
                                "Partir cinq jours découvrir "
                                "un autre monde ? Bricoler "
                                "dans un fablab, ou pourquoi "
                                "pas, enregistrer votre "
                                "premier titre ?",
                                "isActive": True,
                                "offlineOnly": True,
                                "onlineOnly": False,
                                "proLabel": "Pratique artistique - séances " "d'essai et stages ponctuels",
                                "sublabel": "Pratiquer",
                                "type": "Event",
                                "value": "EventType.PRATIQUE_ARTISTIQUE",
                            },
                            "stocks": [
                                {
                                    "beginningDatetime": "2019-01-07T00:00:00Z",
                                    "bookingLimitDatetime": "2019-02-07T00:00:00Z",
                                    "dateCreated": "2019-01-05T00:00:00Z",
                                    "dateModified": "2019-01-07T00:00:00Z",
                                    "id": "AE",
                                    "offerId": "FU",
                                    "price": 10.99,
                                    "quantity": 34,
                                    "isBookable": True,
                                    "remainingQuantity": "unlimited",
                                }
                            ],
                            "thumbUrl": "http://localhost/storage/thumbs/products/BQ",
                            "venue": {
                                "address": "5 rue du cinéma",
                                "city": "Lure",
                                "departementCode": "70",
                                "id": "K4",
                                "latitude": 9.45678,
                                "longitude": 45.0987654,
                                "name": "Théâtre",
                                "postalCode": "70200",
                            },
                            "venueId": "K4",
                            "withdrawalDetails": None,
                        },
                        "offerId": "FU",
                        "price": 12.89,
                    },
                    "stockId": "HA",
                    "token": "TOKEN",
                    "userId": "BQ",
                }
            ]

        @freeze_time("2019-1-1")
        def test_should_return_expected_json_with_activation_code(self):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=34,
                    offerId=45,
                    price=10.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=False,
                    isOfferActive=True,
                )
            ]

            beneficiary_booking = BeneficiaryBooking(
                amount=12,
                cancellationDate=datetime(2019, 3, 12),
                dateCreated=datetime(2019, 2, 7),
                dateUsed=datetime(2019, 4, 7),
                id=4,
                isCancelled=False,
                isUsed=True,
                quantity=2,
                stockId=56,
                token="TOKEN",
                userId=12,
                offerId=45,
                name="Ma super offre",
                type="EventType.PRATIQUE_ARTISTIQUE",
                url="http://url.com",
                email="john@example.com",
                beginningDatetime=datetime(2019, 3, 8),
                venueId=87,
                departementCode="70",
                withdrawalDetails=None,
                isDuo=True,
                extraData={"isbn": "9876543678"},
                durationMinutes=180,
                description="Ma super decription",
                isNational=False,
                mediaUrls=[],
                venueName="Théâtre",
                address="5 rue du cinéma",
                postalCode="70200",
                city="Lure",
                latitude=9.45678,
                longitude=45.0987654,
                price=12.89,
                productId=12,
                thumbCount=1,
                active_mediations=[],
                displayAsEnded=False,
                activationCode="code-lEkcmMSBW",
            )
            beneficiary_bookings = BeneficiaryBookingsWithStocks(bookings=[beneficiary_booking], stocks=stocks)

            # When
            serialized_beneficiary_booking = serialize_beneficiary_bookings(beneficiary_bookings=beneficiary_bookings)

            # Then
            assert serialized_beneficiary_booking == [
                {
                    "activationCode": "code-lEkcmMSBW",
                    "amount": 12,
                    "cancellationDate": "2019-03-12T00:00:00Z",
                    "completedUrl": "http://url.com",
                    "dateCreated": "2019-02-07T00:00:00Z",
                    "dateUsed": "2019-04-07T00:00:00Z",
                    "id": "AQ",
                    "isCancelled": False,
                    "isEventExpired": False,
                    "isUsed": True,
                    "quantity": 2,
                    "displayAsEnded": False,
                    "stock": {
                        "beginningDatetime": "2019-03-08T00:00:00Z",
                        "id": "HA",
                        "isEventExpired": False,
                        "offer": {
                            "description": "Ma super decription",
                            "durationMinutes": 180,
                            "extraData": {"isbn": "9876543678"},
                            "id": "FU",
                            "isDigital": True,
                            "isDuo": True,
                            "isEvent": True,
                            "isNational": False,
                            "name": "Ma super offre",
                            "isBookable": True,
                            "offerType": {
                                "appLabel": "Pratique artistique",
                                "conditionalFields": ["speaker"],
                                "description": "Jamais osé monter sur les "
                                "planches ? Tenter "
                                "d’apprendre la guitare, le "
                                "piano ou la photographie ? "
                                "Partir cinq jours découvrir "
                                "un autre monde ? Bricoler "
                                "dans un fablab, ou pourquoi "
                                "pas, enregistrer votre "
                                "premier titre ?",
                                "isActive": True,
                                "offlineOnly": True,
                                "onlineOnly": False,
                                "proLabel": "Pratique artistique - séances " "d'essai et stages ponctuels",
                                "sublabel": "Pratiquer",
                                "type": "Event",
                                "value": "EventType.PRATIQUE_ARTISTIQUE",
                            },
                            "stocks": [
                                {
                                    "beginningDatetime": "2019-01-07T00:00:00Z",
                                    "bookingLimitDatetime": "2019-02-07T00:00:00Z",
                                    "dateCreated": "2019-01-05T00:00:00Z",
                                    "dateModified": "2019-01-07T00:00:00Z",
                                    "id": "AE",
                                    "offerId": "FU",
                                    "price": 10.99,
                                    "quantity": 34,
                                    "isBookable": True,
                                    "remainingQuantity": "unlimited",
                                }
                            ],
                            "thumbUrl": "http://localhost/storage/thumbs/products/BQ",
                            "venue": {
                                "address": "5 rue du cinéma",
                                "city": "Lure",
                                "departementCode": "70",
                                "id": "K4",
                                "latitude": 9.45678,
                                "longitude": 45.0987654,
                                "name": "Théâtre",
                                "postalCode": "70200",
                            },
                            "venueId": "K4",
                            "withdrawalDetails": None,
                        },
                        "offerId": "FU",
                        "price": 12.89,
                    },
                    "stockId": "HA",
                    "token": "TOKEN",
                    "userId": "BQ",
                }
            ]

        @freeze_time("2019-1-1")
        def test_offer_should_not_be_bookable_when_all_stock_are_not_bookable(self):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=34,
                    offerId=45,
                    price=10.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=True,
                    isOfferActive=True,
                ),
                Stock(
                    id=2,
                    quantity=3,
                    offerId=12,
                    price=12.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=False,
                    isOfferActive=False,
                ),
            ]

            beneficiary_booking = BeneficiaryBooking(
                amount=12,
                cancellationDate=datetime(2019, 3, 12),
                dateCreated=datetime(2019, 2, 7),
                dateUsed=datetime(2019, 4, 7),
                id=4,
                isCancelled=False,
                isUsed=True,
                quantity=2,
                stockId=56,
                token="TOKEN",
                userId=12,
                offerId=45,
                name="Ma super offre",
                type="EventType.PRATIQUE_ARTISTIQUE",
                url="http://url.com",
                email="john@example.com",
                beginningDatetime=datetime(2019, 3, 8),
                venueId=87,
                departementCode="70",
                withdrawalDetails=None,
                isDuo=True,
                extraData={"isbn": "9876543678"},
                durationMinutes=180,
                description="Ma super decription",
                isNational=False,
                mediaUrls=[],
                venueName="Théâtre",
                address="5 rue du cinéma",
                postalCode="70200",
                city="Lure",
                latitude=9.45678,
                longitude=45.0987654,
                price=12.89,
                productId=12,
                thumbCount=1,
                active_mediations=[],
                displayAsEnded=False,
                activationCode=None,
            )
            beneficiary_bookings = BeneficiaryBookingsWithStocks(bookings=[beneficiary_booking], stocks=stocks)

            # When
            serialized_beneficiary_booking = serialize_beneficiary_bookings(
                beneficiary_bookings=beneficiary_bookings, with_qr_code=True
            )

            # Then
            assert serialized_beneficiary_booking[0]["stock"]["offer"]["isBookable"] is False

        @freeze_time("2019-1-1")
        def test_offer_should_be_bookable_when_at_least_one_stock_is_bookable(self):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=34,
                    offerId=45,
                    price=10.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=False,
                    isOfferActive=True,
                ),
                Stock(
                    id=2,
                    quantity=3,
                    offerId=12,
                    price=12.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=False,
                    isOfferActive=False,
                ),
            ]

            beneficiary_booking = BeneficiaryBooking(
                amount=12,
                cancellationDate=datetime(2019, 3, 12),
                dateCreated=datetime(2019, 2, 7),
                dateUsed=datetime(2019, 4, 7),
                id=4,
                isCancelled=False,
                isUsed=True,
                quantity=2,
                stockId=56,
                token="TOKEN",
                userId=12,
                offerId=45,
                name="Ma super offre",
                type="EventType.PRATIQUE_ARTISTIQUE",
                url="http://url.com",
                email="john@example.com",
                beginningDatetime=datetime(2019, 3, 8),
                venueId=87,
                departementCode="70",
                withdrawalDetails=None,
                isDuo=True,
                extraData={"isbn": "9876543678"},
                durationMinutes=180,
                description="Ma super decription",
                isNational=False,
                mediaUrls=[],
                venueName="Théâtre",
                address="5 rue du cinéma",
                postalCode="70200",
                city="Lure",
                latitude=9.45678,
                longitude=45.0987654,
                price=12.89,
                productId=12,
                thumbCount=1,
                active_mediations=[],
                displayAsEnded=False,
                activationCode=None,
            )
            beneficiary_bookings = BeneficiaryBookingsWithStocks(bookings=[beneficiary_booking], stocks=stocks)

            # When
            serialized_beneficiary_booking = serialize_beneficiary_bookings(
                beneficiary_bookings=beneficiary_bookings, with_qr_code=True
            )

            # Then
            assert serialized_beneficiary_booking[0]["stock"]["offer"]["isBookable"] is True
