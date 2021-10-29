from unittest.mock import patch

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient
from tests.conftest import clean_database


class CriteriaViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_criterion(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="admin@example.com")

        offer = offers_factories.OfferFactory()
        criterion = offers_factories.CriterionFactory(name="test_delete_criterion")
        offers_factories.OfferCriterionFactory(offer=offer, criterion=criterion)

        assert len(offer.criteria) == 1

        data = dict(id=criterion.id)
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")

        response = client.post("/pc/back-office/criterion/delete/", form=data)

        assert response.status_code == 302
        assert len(offer.criteria) == 0
