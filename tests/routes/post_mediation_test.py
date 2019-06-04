from os import path
from pathlib import Path

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_user, \
    create_offer_with_event_product, \
    create_offerer, \
    create_user_offerer, \
    create_venue
from utils.human_ids import humanize


class Post:
    class Returns201:
        @clean_database
        def when_mediation_is_created_with_thumb_url(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            PcObject.save(offer)
            PcObject.save(user, venue, offerer, user_offerer)

            auth_request = TestClient().with_auth(email=user.email)

            data = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumbUrl': 'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
            }

            # when
            response = auth_request.post(API_URL + '/mediations', form=data)

            # then
            assert response.status_code == 201

        @clean_database
        def when_mediation_is_created_with_with_thumb_file(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)

            PcObject.save(offer)
            PcObject.save(user, venue, offerer, user_offerer)

            auth_request = TestClient().with_auth(email=user.email)

            with open(Path(path.dirname(path.realpath(__file__))) / '..' / '..'
                      / 'sandboxes' / 'thumbs' / 'mediations' / 'FranckLepage', 'rb') as thumb_file:
                data = {
                    'offerId': humanize(offer.id),
                    'offererId': humanize(offerer.id)
                }
                # WE NEED TO GIVE AN EXTENSION TO THE FILE
                # IF WE WANT TO MAKE THE TEST PASS
                files = {'thumb': ('FranckLepage.jpg', thumb_file)}

                # when
                response = auth_request.post(API_URL + '/mediations', form=data, files=files)

            # then
            assert response.status_code == 201

    class Returns400:
        @clean_database
        def when_mediation_is_created_with_thumb_url_pointing_to_not_an_image(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.save(user, venue, user_offerer)

            auth_request = TestClient().with_auth(email=user.email)

            data = {
                'offerId': humanize(offer.id),
                'offererId': humanize(offerer.id),
                'thumbUrl': 'https://beta.gouv.fr/'
            }

            # when
            response = auth_request.post(API_URL + '/mediations', form=data)

            # then
            assert response.status_code == 400
            assert response.json()['thumbUrl'] == ["L'adresse saisie n'est pas valide"]
