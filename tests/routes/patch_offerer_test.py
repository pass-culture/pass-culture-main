""" routes offerer """
from datetime import datetime

from models import Offerer
from repository import repository
from routes.serialization import serialize
import pytest
from tests.conftest import TestClient
from model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer, \
    create_recommendation
from model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import humanize


class Patch:
    class Returns403:
        @pytest.mark.usefixtures("db_session")
        def when_user_does_not_have_rights_on_offerer(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, is_admin=False)
            repository.save(user_offerer)
            body = {'isActive': False}

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch('/offerers/%s' % humanize(offerer.id), json=body)

            # then
            assert response.status_code == 403

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_editing_non_authorised_fields(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            repository.save(user_offerer)
            body = {'thumbCount': 0, 'idAtProviders': 'zfeej',
                    'dateModifiedAtLastProvider': serialize(datetime(2016, 2, 1)), 'address': '123 nouvelle adresse',
                    'postalCode': '75001',
                    'city': 'Paris', 'validationToken': 'ozieghieof', 'id': humanize(10),
                    'dateCreated': serialize(datetime(2015, 2, 1)),
                    'name': 'Nouveau Nom', 'siren': '989807829', 'lastProviderId': humanize(1)}

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch('/offerers/%s' % humanize(offerer.id), json=body)

            # then
            assert response.status_code == 400
            for key in body:
                assert response.json[key] == ['Vous ne pouvez pas modifier ce champ']

    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_deactivating_offerer(self, app):
            # given
            user = create_user()
            other_user = create_user(email='other@email.fr')
            offerer = create_offerer(siren='987654321')
            other_offerer = create_offerer()
            venue1 = create_venue(offerer, siret=offerer.siren + '12345')
            venue2 = create_venue(offerer, siret=offerer.siren + '12346')
            other_venue = create_venue(other_offerer)
            offer_venue1_1 = create_offer_with_event_product(venue1)
            offer_venue2_1 = create_offer_with_event_product(venue2)
            offer_venue2_2 = create_offer_with_thing_product(venue2)
            other_offer = create_offer_with_event_product(other_venue)
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            recommendation1 = create_recommendation(offer_venue1_1, other_user)
            recommendation2 = create_recommendation(offer_venue2_1, other_user)
            recommendation3 = create_recommendation(offer_venue2_2, other_user)
            recommendation4 = create_recommendation(offer_venue2_2, user)
            other_recommendation = create_recommendation(other_offer, user)
            repository.save(recommendation1, recommendation2, recommendation3, recommendation4,
                          other_recommendation,
                          user_offerer)
            offerer_id = offerer.id

            data = {'isActive': False}

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch('/offerers/%s' % humanize(offerer.id), json=data)

            # then
            offerer = Offerer.query.get(offerer_id)

            assert response.status_code == 200
            assert response.json['isActive'] == offerer.isActive
            assert offerer.isActive == data['isActive']
