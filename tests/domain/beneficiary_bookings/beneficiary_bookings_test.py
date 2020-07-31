from datetime import datetime, timedelta

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBooking


class BeneficiaryBookingTest:
    class BookingAccessUrlTest:
        def should_return_booking_completed_url(self):
            # Given
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
                token='ABCDEF',
                userId=12,
                offerId=45,
                name='Ma super offre',
                type='EventType.PRATIQUE_ARTISTIQUE',
                url='http://javascript:alert("plop")?token={token}&email={email}',
                email='bob@example.com',
                beginningDatetime=None,
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
            completed_url = beneficiary_booking.booking_access_url

            # Then
            assert completed_url == 'http://javascript:alert("plop")?token=ABCDEF&email=bob@example.com'

    class IsEventExpiredTest:
        def test_is_not_expired_when_stock_is_not_an_event(self):
            # Given
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
                beginningDatetime=None,
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
            is_event_expired = beneficiary_booking.is_event_expired

            # Then
            assert is_event_expired is False

        def test_is_not_expired_when_stock_is_an_event_in_the_future(self):
            # Given
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
                beginningDatetime=datetime.now() + timedelta(days=2),
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
            is_event_expired = beneficiary_booking.is_event_expired

            # Then
            assert is_event_expired is False

        def test_is_expired_when_stock_is_an_event_in_the_past(self):
            # Given
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
            is_event_expired = beneficiary_booking.is_event_expired

            # Then
            assert is_event_expired is True
