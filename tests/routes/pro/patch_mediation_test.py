from unittest.mock import patch

import pytest

from pcapi.core.offers.models import MediationSQLEntity
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200:
    def when_mediation_is_edited(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user_offerer = create_user_offerer(user, offerer)
        mediation = create_mediation(offer)
        repository.save(mediation)
        repository.save(user, venue, offerer, user_offerer)
        mediation_id = mediation.id
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        data = {"isActive": False}

        # when
        response = auth_request.patch("/mediations/%s" % humanize(mediation.id), json=data)

        # then
        mediation = MediationSQLEntity.query.get(mediation_id)
        assert response.status_code == 200
        assert response.json["id"] == humanize(mediation.id)
        assert response.json["thumbUrl"] == mediation.thumbUrl
        assert mediation.isActive == data["isActive"]

        assert response.json == {
            "authorId": None,
            "credit": None,
            "dateCreated": format_into_utc_date(mediation.dateCreated),
            "dateModifiedAtLastProvider": format_into_utc_date(mediation.dateModifiedAtLastProvider),
            "fieldsUpdated": [],
            "id": humanize(mediation.id),
            "idAtProviders": None,
            "isActive": data["isActive"],
            "lastProviderId": None,
            "offerId": humanize(offer.id),
            "thumbCount": 0,
            "thumbUrl": None,
        }

    def should_match_a_mediation_description(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user_offerer = create_user_offerer(user, offerer)
        mediation = create_mediation(offer)
        repository.save(mediation)
        repository.save(user, venue, offerer, user_offerer)
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        data = {"isActive": False}

        # when
        response = auth_request.patch("/mediations/%s" % humanize(mediation.id), json=data)

        # then
        assert response.status_code == 200
        assert set(response.json) == {
            "authorId",
            "credit",
            "dateCreated",
            "dateModifiedAtLastProvider",
            "fieldsUpdated",
            "id",
            "idAtProviders",
            "isActive",
            "lastProviderId",
            "offerId",
            "thumbCount",
            "thumbUrl",
        }

    @patch("pcapi.routes.pro.mediations.feature_queries.is_active", return_value=True)
    @patch("pcapi.routes.pro.mediations.redis.add_offer_id")
    def should_add_offer_id_to_redis_when_mediation_is_edited(self, mock_redis, mock_feature, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user_offerer = create_user_offerer(user, offerer)
        mediation = create_mediation(offer)
        repository.save(mediation)
        repository.save(user, venue, offerer, user_offerer)
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        data = {"isActive": False}

        # when
        response = auth_request.patch("/mediations/%s" % humanize(mediation.id), json=data)

        # then
        assert response.status_code == 200
        mock_redis.assert_called_once()
        mock_kwargs = mock_redis.call_args[1]
        assert mock_kwargs["offer_id"] == offer.id


@pytest.mark.usefixtures("db_session")
class Returns403:
    def when_current_user_is_not_attached_to_offerer_of_mediation(self, app):
        # given
        current_user = create_user(email="bobby@test.com")
        other_user = create_user(email="jimmy@test.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        user_offerer = create_user_offerer(other_user, offerer)
        mediation = create_mediation(offer)
        repository.save(mediation)
        repository.save(other_user, current_user, venue, offerer, user_offerer)

        auth_request = TestClient(app.test_client()).with_auth(email=current_user.email)
        data = {"isActive": False}

        # when
        response = auth_request.patch("/mediations/%s" % humanize(mediation.id), json=data)

        # then
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


@pytest.mark.usefixtures("db_session")
class Returns404:
    def when_mediation_does_not_exist(self, app):
        # given
        user = create_user()
        repository.save(user)
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        data = {"isActive": False}

        # when
        response = auth_request.patch("/mediations/ADFGA", json=data)

        # then
        assert response.status_code == 404
        assert response.json == {}
