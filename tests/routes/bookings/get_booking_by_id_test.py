from pcapi.repository import repository
import pytest
from tests.conftest import TestClient
from pcapi.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_stock
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def expect_booking_to_have_completed_url(self, app):
            # Given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue,
                                                    url='https://host/path/{token}?offerId={offerId}&email={email}')
            stock = create_stock(offer=offer, price=0)
            booking = create_booking(user=user, stock=stock, token='ABCDEF', venue=venue)
            repository.save(booking)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/bookings/' + humanize(booking.id))

            # Then
            assert response.status_code == 200
            completed_url = 'https://host/path/ABCDEF?offerId={}&email=user@example.com'.format(
                humanize(offer.id)
            )

            assert 'validationToken' not in response.json['stock']['offer']
            assert response.json == {
                'amount': 0.0,
                'cancellationDate': None,
                'completedUrl': completed_url,
                'confirmationDate': None,
                'dateCreated': format_into_utc_date(booking.dateCreated),
                'dateUsed': None,
                'id': humanize(booking.id),
                'isCancelled': False,
                'isEventExpired': False,
                'isUsed': False,
                'mediation': None,
                'quantity': 1,
                'recommendationId': None,
                'stock': {
                    'beginningDatetime': None,
                    'bookingLimitDatetime': None,
                    'dateCreated': format_into_utc_date(stock.dateCreated),
                    'dateModified': format_into_utc_date(stock.dateModified),
                    'dateModifiedAtLastProvider': format_into_utc_date(stock.dateModifiedAtLastProvider),
                    'fieldsUpdated': [],
                    'hasBeenMigrated': None,
                    'id': humanize(stock.id),
                    'idAtProviders': None,
                    'isBookable': True,
                    'isEventExpired': False,
                    'isSoftDeleted': False,
                    'lastProviderId': None,
                    'offer': {
                        'ageMax': None,
                        'ageMin': None,
                        'bookingEmail': 'booking@example.net',
                        'conditions': None,
                        'dateCreated': format_into_utc_date(offer.dateCreated),
                        'dateModifiedAtLastProvider': format_into_utc_date(offer.dateModifiedAtLastProvider),
                        'description': None,
                        'durationMinutes': None,
                        'extraData': {'author': 'Test Author'},
                        'fieldsUpdated': [],
                        'hasBookingLimitDatetimesPassed': False,
                        'id': humanize(offer.id),
                        'idAtProviders': offer.idAtProviders,
                        'isActive': True,
                        'isBookable': True,
                        'isDigital': True,
                        'isDuo': False,
                        'isEvent': False,
                        'isNational': False,
                        'lastProviderId': None,
                        'mediaUrls': ['test/urls'],
                        'name': 'Test Book',
                        'offerType': {
                            'appLabel': 'Film',
                            'conditionalFields': [],
                            'description': (
                                'Action, science-fiction, documentaire ou comédie '
                                'sentimentale ? En salle, en plein air ou bien au chaud '
                                'chez soi ? Et si c’était plutôt cette exposition qui '
                                'allait faire son cinéma ?'
                            ),
                            'isActive': True,
                            'offlineOnly': False,
                            'onlineOnly': False,
                            'proLabel': 'Audiovisuel - films sur supports physiques et VOD',
                            'sublabel': 'Regarder',
                            'type': 'Thing',
                            'value': 'ThingType.AUDIOVISUEL',
                        },
                        'productId': humanize(offer.product.id),
                        'stocks': [
                            {
                                'beginningDatetime': None,
                                'bookingLimitDatetime': None,
                                'dateCreated': format_into_utc_date(stock.dateCreated),
                                'dateModified': format_into_utc_date(stock.dateModified),
                                'dateModifiedAtLastProvider': format_into_utc_date(stock.dateModifiedAtLastProvider),
                                'fieldsUpdated': [],
                                'hasBeenMigrated': None,
                                'id': humanize(stock.id),
                                'idAtProviders': None,
                                'isBookable': True,
                                'isEventExpired': False,
                                'isSoftDeleted': False,
                                'lastProviderId': None,
                                'offerId': humanize(offer.id),
                                'price': 0.0,
                                'quantity': None,
                                'remainingQuantity': 'unlimited',
                            }
                        ],
                        'thumbUrl': None,
                        'type': 'ThingType.AUDIOVISUEL',
                        'url': 'https://host/path/{token}?offerId={offerId}&email={email}',
                        'venue': {
                            'address': '123 rue de Paris',
                            'bookingEmail': None,
                            'city': 'Montreuil',
                            'comment': None,
                            'dateCreated': format_into_utc_date(venue.dateCreated),
                            'dateModifiedAtLastProvider': format_into_utc_date(venue.dateModifiedAtLastProvider),
                            'departementCode': '93',
                            'fieldsUpdated': [],
                            'id': humanize(venue.id),
                            'idAtProviders': None,
                            'isVirtual': False,
                            'lastProviderId': None,
                            'latitude': None,
                            'longitude': None,
                            'managingOffererId': humanize(offerer.id),
                            'name': 'La petite librairie',
                            'postalCode': '93100',
                            'publicName': None,
                            'siret': '12345678912345',
                            'thumbCount': 0,
                            'venueLabelId': None,
                            'venueTypeId': None,
                        },
                        'venueId': humanize(venue.id),
                        'withdrawalDetails': None,
                    },
                    'offerId': humanize(offer.id),
                    'price': 0.0,
                    'quantity': None,
                    'remainingQuantity': 'unlimited',
                },
                'stockId': humanize(stock.id),
                'token': booking.token,
                'userId': humanize(user.id),
            }
