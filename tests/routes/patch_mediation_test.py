from unittest.mock import patch

from models import Mediation
from repository.repository import Repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer, \
    create_mediation
from tests.model_creators.specific_creators import create_offer_with_event_product
from utils.human_ids import humanize


class Patch:
    class Returns200:
        @clean_database
        def when_mediation_is_edited(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            mediation = create_mediation(offer)
            Repository.save(mediation)
            Repository.save(user, venue, offerer, user_offerer)
            mediation_id = mediation.id
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
            data = {'frontText': 'new front text', 'backText': 'new back text', 'isActive': False}

            # when
            response = auth_request.patch('/mediations/%s' % humanize(mediation.id), json=data)

            # then
            mediation = Mediation.query.get(mediation_id)
            assert response.status_code == 200
            assert response.json['id'] == humanize(mediation.id)
            assert response.json['frontText'] == mediation.frontText
            assert response.json['backText'] == mediation.backText
            assert response.json['isActive'] == mediation.isActive
            assert response.json['thumbUrl'] == mediation.thumbUrl
            assert mediation.isActive == data['isActive']
            assert mediation.frontText == data['frontText']
            assert mediation.backText == data['backText']

        @clean_database
        @patch('routes.mediations.redis.add_offer_id')
        def should_add_offer_id_to_redis_when_mediation_is_edited(self, mock_redis, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            mediation = create_mediation(offer)
            PcObject.save(mediation)
            PcObject.save(user, venue, offerer, user_offerer)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
            data = {'frontText': 'new front text', 'backText': 'new back text', 'isActive': False}

            # when
            response = auth_request.patch('/mediations/%s' % humanize(mediation.id), json=data)

            # then
            assert response.status_code == 200
            mock_redis.assert_called_once()
            mock_args, mock_kwargs = mock_redis.call_args
            assert mock_kwargs['offer_id'] == offer.id


    class Returns403:
        @clean_database
        def when_current_user_is_not_attached_to_offerer_of_mediation(self, app):
            # given
            current_user = create_user(email='bobby@test.com')
            other_user = create_user(email='jimmy@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(other_user, offerer)
            mediation = create_mediation(offer)
            Repository.save(mediation)
            Repository.save(other_user, current_user, venue, offerer, user_offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=current_user.email)

            # when
            response = auth_request.patch('/mediations/%s' % humanize(mediation.id), json={})

            # then
            assert response.status_code == 403

    class Returns404:
        @clean_database
        def when_mediation_does_not_exist(self, app):
            # given
            user = create_user()
            Repository.save(user)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/mediations/ADFGA', json={})

            # then
            assert response.status_code == 404
