import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Mediation
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200:
    def when_mediation_is_edited(self, app):
        # given
        mediation = offers_factories.MediationFactory()
        offerer = mediation.offer.venue.managingOfferer
        offers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )

        # when
        client = TestClient(app.test_client()).with_auth(email="user@example.com")
        data = {"isActive": False}
        response = client.patch(f"/mediations/{humanize(mediation.id)}", json=data)

        # then
        mediation = Mediation.query.one()
        assert not mediation.isActive
        assert response.status_code == 200
        assert response.json["id"] == humanize(mediation.id)
        assert response.json["thumbUrl"] == mediation.thumbUrl

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
            "offerId": humanize(mediation.offer.id),
            "thumbCount": 0,
            "thumbUrl": None,
        }


@pytest.mark.usefixtures("db_session")
class Returns403:
    def when_current_user_is_not_attached_to_offerer_of_mediation(self, app):
        mediation = offers_factories.MediationFactory()
        offers_factories.UserOffererFactory(user__email="user@example.com")

        # when
        client = TestClient(app.test_client()).with_auth(email="user@example.com")
        data = {"isActive": False}
        response = client.patch(f"/mediations/{humanize(mediation.id)}", json=data)

        # then
        mediation = Mediation.query.one()
        assert mediation.isActive
        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
        }


@pytest.mark.usefixtures("db_session")
class Returns404:
    def when_mediation_does_not_exist(self, app):
        # given
        user = users_factories.UserFactory()

        # when
        client = TestClient(app.test_client()).with_auth(email=user.email)
        data = {"isActive": False}
        response = client.patch("/mediations/ADFGA", json=data)

        # then
        assert response.status_code == 404
