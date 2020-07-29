from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBooking
from domain.beneficiary_bookings.stock import Stock
from routes.serialization.beneficiary_bookings_serialize import serialize_stock_for_beneficiary_booking, \
    serialize_beneficiary_booking, serialize_stocks_for_beneficiary_bookings
from utils.human_ids import humanize


class BeneficiaryBookingsSerializeTest:
    class SerializeStocksForBeneficiaryBookingsTest:
        @patch('routes.serialization.beneficiary_bookings_serialize.serialize_stock_for_beneficiary_booking')
        def should_call_serialize_stock_for_beneficiary(self, mock_serialize_stock_for_beneficiary):
            # Given
            matched_offer_id = 54
            matching_stock = Stock(id=2, quantity=8, offerId=54, price=8.99, dateCreated=datetime(2019, 1, 5),
                                   dateModified=datetime(2019, 1, 7), beginningDatetime=datetime(2019, 1, 7),
                                   bookingLimitDatetime=datetime(2019, 2, 7), isSoftDeleted=False, isOfferActive=True)
            stocks = [
                Stock(
                    id=1,
                    quantity=3,
                    offerId=12,
                    price=10.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    beginningDatetime=datetime(2019, 1, 7),
                    bookingLimitDatetime=datetime(2019, 2, 7),
                    isSoftDeleted=False,
                    isOfferActive=True,
                ),
                matching_stock
            ]

            # When
            serialize_stocks_for_beneficiary_bookings(matched_offer_id, stocks)

            # Then
            mock_serialize_stock_for_beneficiary.assert_called_once_with(matching_stock)

    class SerializeStockForBeneficiaryBookingTest:
        def should_return_expected_json(self):
            # Given
            stock = Stock(
                id=1,
                quantity=34,
                offerId=4,
                price=10.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime(2019, 1, 7),
                bookingLimitDatetime=datetime(2019, 2, 7),
                isSoftDeleted=False,
                isOfferActive=True,
            )

            # When
            serialized_stock = serialize_stock_for_beneficiary_booking(stock)

            # Then
            assert serialized_stock == {
                'beginningDatetime': '2019-01-07T00:00:00Z',
                'bookingLimitDatetime': '2019-02-07T00:00:00Z',
                'dateCreated': '2019-01-05T00:00:00Z',
                'dateModified': '2019-01-07T00:00:00Z',
                'id': humanize(stock.id),
                'offerId': humanize(stock.offerId),
                'price': 10.99,
                'quantity': 34
            }

    class SerializeBeneficiaryBookingTest:
        def should_return_expected_json_without_qr_code(self):
            # Given
            serialized_stocks = [{
                'beginningDatetime': '2019-01-07T00:00:00Z',
                'bookingLimitDatetime': '2019-02-07T00:00:00Z',
                'dateCreated': '2019-01-05T00:00:00Z',
                'dateModified': '2019-01-07T00:00:00Z',
                'id': 'AE',
                'offerId': 'EF',
                'price': 10.99,
                'quantity': 4,
            }]
            beneficiary_booking = BeneficiaryBooking(
                amount=12,
                cancellationDate=datetime(2019, 3, 12),
                dateCreated=datetime(2019, 2, 7),
                dateUsed=datetime(2019, 4, 7),
                id=4,
                isCancelled=False,
                isUsed=True,
                quantity=2,
                recommendationId=None,
                stockId=56,
                token='TOKEN',
                userId=12,
                offerId=45,
                name='Ma super offre',
                type='EventType.PRATIQUE_ARTISTIQUE',
                url='http://url.com',
                email='john@example.com',
                beginningDatetime=datetime(2019, 3, 8),
                venueId=87,
                departementCode='70',
                withdrawalDetails=None,
                isDuo=True,
                extraData={'isbn': '9876543678'},
                durationMinutes=180,
                description='Ma super decription',
                isNational=False,
                mediaUrls=[],
                venueName='Théâtre',
                address='5 rue du cinéma',
                postalCode='70200',
                city='Lure',
                latitude=9.45678,
                longitude=45.0987654,
                price=12.89,
            )

            # When
            serialized_beneficiary_booking = serialize_beneficiary_booking(
                beneficiary_booking,
                serialized_stocks,
                with_qr_code=False)

            # Then
            assert serialized_beneficiary_booking == {
                'amount': 12,
                'cancellationDate': '2019-03-12T00:00:00Z',
                'completedUrl': 'http://url.com',
                'dateCreated': '2019-02-07T00:00:00Z',
                'dateUsed': '2019-04-07T00:00:00Z',
                'id': 'AQ',
                'isCancelled': False,
                'isEventExpired': True,
                'isUsed': True,
                'quantity': 2,
                'recommendationId': None,
                'stock': {
                    'beginningDatetime': '2019-03-08T00:00:00Z',
                    'id': 'HA',
                    'isEventExpired': True,
                    'offer': {
                        'description': 'Ma super decription',
                        'durationMinutes': 180,
                        'extraData': {'isbn': '9876543678'},
                        'id': 'FU',
                        'isDigital': True,
                        'isDuo': True,
                        'isEvent': True,
                        'isNational': False,
                        'name': 'Ma super offre',
                        'offerType': {
                            'appLabel': 'Pratique artistique',
                            'conditionalFields': ['speaker'],
                            'description': 'Jamais osé monter sur les '
                                           'planches ? Tenter '
                                           'd’apprendre la guitare, le '
                                           'piano ou la photographie ? '
                                           'Partir cinq jours découvrir '
                                           'un autre monde ? Bricoler '
                                           'dans un fablab, ou pourquoi '
                                           'pas, enregistrer votre '
                                           'premier titre ?',
                            'isActive': True,
                            'offlineOnly': True,
                            'onlineOnly': False,
                            'proLabel': 'Pratique artistique - séances '
                                        "d'essai et stages ponctuels",
                            'sublabel': 'Pratiquer',
                            'type': 'Event',
                            'value': 'EventType.PRATIQUE_ARTISTIQUE'},
                        'stocks': [{
                            'beginningDatetime': '2019-01-07T00:00:00Z',
                            'bookingLimitDatetime': '2019-02-07T00:00:00Z',
                            'dateCreated': '2019-01-05T00:00:00Z',
                            'dateModified': '2019-01-07T00:00:00Z',
                            'id': 'AE',
                            'offerId': 'EF',
                            'price': 10.99,
                            'quantity': 4
                        }],
                        'thumb_url': '',
                        'venue': {
                            'address': '5 rue du cinéma',
                            'city': 'Lure',
                            'departementCode': '70',
                            'id': 'K4',
                            'latitude': 9.45678,
                            'longitude': 45.0987654,
                            'name': 'Théâtre',
                            'postalCode': '70200'
                        },
                        'venueId': 'K4',
                        'withdrawalDetails': None
                    },
                    'offerId': 'FU',
                    'price': 12.89
                },
                'stockId': 'HA',
                'token': 'TOKEN',
                'userId': 'BQ'
            }

        @freeze_time('2020-1-1')
        @patch('domain.beneficiary_bookings.beneficiary_bookings.generate_qr_code')
        def should_return_expected_json_with_qr_code(self, mock_generate_qr_code):
            # Given
            mock_generate_qr_code.return_value = 'fake_qr_code'
            serialized_stocks = [{
                'beginningDatetime': '2019-01-07T00:00:00Z',
                'bookingLimitDatetime': '2019-02-07T00:00:00Z',
                'dateCreated': '2019-01-05T00:00:00Z',
                'dateModified': '2019-01-07T00:00:00Z',
                'id': 'AE',
                'offerId': 'EF',
                'price': 10.99,
                'quantity': 4,
            }]
            beneficiary_booking = BeneficiaryBooking(
                amount=12,
                cancellationDate=datetime(2019, 3, 12),
                dateCreated=datetime(2019, 2, 7),
                dateUsed=datetime(2019, 4, 7),
                id=4,
                isCancelled=False,
                isUsed=True,
                quantity=2,
                recommendationId=None,
                stockId=56,
                token='TOKEN',
                userId=12,
                offerId=45,
                name='Ma super offre',
                type='EventType.PRATIQUE_ARTISTIQUE',
                url='http://url.com',
                email='john@example.com',
                beginningDatetime=datetime(2020, 3, 8),
                venueId=87,
                departementCode='70',
                withdrawalDetails=None,
                isDuo=True,
                extraData={'isbn': '9876543678'},
                durationMinutes=180,
                description='Ma super decription',
                isNational=False,
                mediaUrls=[],
                venueName='Théâtre',
                address='5 rue du cinéma',
                postalCode='70200',
                city='Lure',
                latitude=9.45678,
                longitude=45.0987654,
                price=12.89,
            )

            # When
            serialized_beneficiary_booking = serialize_beneficiary_booking(
                beneficiary_booking,
                serialized_stocks,
                with_qr_code=True)

            # Then
            assert serialized_beneficiary_booking == {
                'amount': 12,
                'cancellationDate': '2019-03-12T00:00:00Z',
                'completedUrl': 'http://url.com',
                'dateCreated': '2019-02-07T00:00:00Z',
                'dateUsed': '2019-04-07T00:00:00Z',
                'id': 'AQ',
                'isCancelled': False,
                'isEventExpired': False,
                'isUsed': True,
                'qrCode': 'fake_qr_code',
                'quantity': 2,
                'recommendationId': None,
                'stock': {
                    'beginningDatetime': '2020-03-08T00:00:00Z',
                    'id': 'HA',
                    'isEventExpired': False,
                    'offer': {
                        'description': 'Ma super decription',
                        'durationMinutes': 180,
                        'extraData': {'isbn': '9876543678'},
                        'id': 'FU',
                        'isDigital': True,
                        'isDuo': True,
                        'isEvent': True,
                        'isNational': False,
                        'name': 'Ma super offre',
                        'offerType': {
                            'appLabel': 'Pratique artistique',
                            'conditionalFields': ['speaker'],
                            'description': 'Jamais osé monter sur les '
                                           'planches ? Tenter '
                                           'd’apprendre la guitare, le '
                                           'piano ou la photographie ? '
                                           'Partir cinq jours découvrir '
                                           'un autre monde ? Bricoler '
                                           'dans un fablab, ou pourquoi '
                                           'pas, enregistrer votre '
                                           'premier titre ?',
                            'isActive': True,
                            'offlineOnly': True,
                            'onlineOnly': False,
                            'proLabel': 'Pratique artistique - séances '
                                        "d'essai et stages ponctuels",
                            'sublabel': 'Pratiquer',
                            'type': 'Event',
                            'value': 'EventType.PRATIQUE_ARTISTIQUE'},
                        'stocks': [{
                            'beginningDatetime': '2019-01-07T00:00:00Z',
                            'bookingLimitDatetime': '2019-02-07T00:00:00Z',
                            'dateCreated': '2019-01-05T00:00:00Z',
                            'dateModified': '2019-01-07T00:00:00Z',
                            'id': 'AE',
                            'offerId': 'EF',
                            'price': 10.99,
                            'quantity': 4
                        }],
                        'thumb_url': '',
                        'venue': {
                            'address': '5 rue du cinéma',
                            'city': 'Lure',
                            'departementCode': '70',
                            'id': 'K4',
                            'latitude': 9.45678,
                            'longitude': 45.0987654,
                            'name': 'Théâtre',
                            'postalCode': '70200'
                        },
                        'venueId': 'K4',
                        'withdrawalDetails': None
                    },
                    'offerId': 'FU',
                    'price': 12.89
                },
                'stockId': 'HA',
                'token': 'TOKEN',
                'userId': 'BQ'
            }
