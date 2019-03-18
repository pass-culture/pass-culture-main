import pytest

from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, create_offerer, create_user_offerer, create_venue, \
    create_thing_offer, API_URL, create_event, create_event_offer
from utils.human_ids import humanize


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_updating_offer_booking_email(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_thing_offer(venue, booking_email='old@email.com')

            PcObject.check_and_save(offer, user, user_offerer)

            json = {
                'bookingEmail': 'offer@email.com',
            }

            # When
            response = TestClient().with_auth(user.email).patch(
                f'{API_URL}/offer/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(offer)
            assert offer.bookingEmail == 'offer@email.com'



    class Returns403:
        @clean_database
        def when_user_is_not_attached_to_offerer(self, app):
                # Given
                user = create_user()
                offerer = create_offerer()
                event = create_event(event_name='Old name')
                venue = create_venue(offerer)
                offer = create_event_offer(venue, event)

                PcObject.check_and_save(event, offer, user, venue)

                json = {
                    'name': 'New name',
                    'venueId': humanize(venue.id)
                }

                # When
                response = TestClient().with_auth(user.email).patch(
                    f'{API_URL}/offer/{humanize(offer.id)}',
                    json=json)

                # Then
                assert response.status_code == 403
                assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]