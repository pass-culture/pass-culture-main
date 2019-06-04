from datetime import datetime, timedelta

from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_user, \
    create_offer_with_event_product, \
    create_mediation, \
    create_offerer, \
    create_user_offerer, \
    create_venue, create_recommendation
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
            PcObject.save(mediation)
            PcObject.save(user, venue, offerer, user_offerer)

            auth_request = TestClient().with_auth(email=user.email)
            data = {'frontText': 'new front text', 'backText': 'new back text', 'isActive': False}

            # when
            response = auth_request.patch(API_URL + '/mediations/%s' % humanize(mediation.id), json=data)

            # then
            db.session.refresh(mediation)
            assert response.status_code == 200
            assert response.json()['id'] == humanize(mediation.id)
            assert response.json()['frontText'] == mediation.frontText
            assert response.json()['backText'] == mediation.backText
            assert response.json()['isActive'] == mediation.isActive
            assert response.json()['thumbUrl'] == mediation.thumbUrl
            assert mediation.isActive == data['isActive']
            assert mediation.frontText == data['frontText']
            assert mediation.backText == data['backText']

        @clean_database
        def when_mediation_is_deactivated(self, app):
            # given
            user_pro = create_user()
            other_user = create_user(email='other@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user_pro, offerer)
            mediation1 = create_mediation(offer)
            mediation2 = create_mediation(offer)
            original_validity_date = datetime.utcnow() + timedelta(days=7)
            recommendation1 = create_recommendation(offer, user_pro, mediation1,
                                                    valid_until_date=original_validity_date)
            recommendation2 = create_recommendation(offer, other_user, mediation1,
                                                    valid_until_date=original_validity_date)
            other_recommendation = create_recommendation(offer, other_user, mediation2,
                                                         valid_until_date=original_validity_date)
            PcObject.save(other_user, user_offerer, recommendation1, recommendation2, other_recommendation)

            auth_request = TestClient().with_auth(email=user_pro.email)
            data = {'isActive': False}

            # when
            response = auth_request.patch(API_URL + '/mediations/%s' % humanize(mediation1.id), json=data)

            # then
            db.session.refresh(mediation1)
            assert response.status_code == 200
            assert response.json()['isActive'] == mediation1.isActive
            assert mediation1.isActive == data['isActive']
            db.session.refresh(recommendation1)
            db.session.refresh(recommendation2)
            db.session.refresh(other_recommendation)
            assert recommendation1.validUntilDate < datetime.utcnow()
            assert recommendation2.validUntilDate < datetime.utcnow()
            assert other_recommendation.validUntilDate == original_validity_date

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
            PcObject.save(mediation)
            PcObject.save(other_user, current_user, venue, offerer, user_offerer)

            auth_request = TestClient().with_auth(email=current_user.email)

            # when
            response = auth_request.patch(API_URL + '/mediations/%s' % humanize(mediation.id), json={})

            # then
            assert response.status_code == 403

    class Returns404:
        @clean_database
        def when_mediation_does_not_exist(self, app):
            # given
            user = create_user()
            PcObject.save(user)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.patch(API_URL + '/mediations/ADFGA', json={})

            # then
            assert response.status_code == 404
