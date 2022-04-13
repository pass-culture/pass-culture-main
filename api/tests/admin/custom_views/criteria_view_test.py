from unittest.mock import patch

import pytest

import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories

from tests.conftest import clean_database


class CriteriaViewTest:
    @pytest.mark.parametrize("name", ["tag", "tag_with_underscores", "[tag]!", "tag_140ch_" * 14])
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_create_criterion(self, mocked_validate_csrf_token, client, name):
        users_factories.AdminFactory(email="admin@example.com")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            "/pc/back-office/criterion/new/",
            form={"name": name, "description": "My description", "startDateTime": None, "endDateTime": None},
        )

        assert response.status_code == 302
        assert criteria_models.Criterion.query.count() == 1
        criterion = criteria_models.Criterion.query.first()
        assert criterion.name == name
        assert criterion.description == "My description"

    @pytest.mark.parametrize(
        "name", ["tag ", " tag", "t ag", "tag\t", "\ttag", "ta\tg", "\ntag", "t\nag", "\rtag", "tag\r", "t\rag"]
    )
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_create_criterion_with_whitespace(self, mocked_validate_csrf_token, client, name):
        users_factories.AdminFactory(email="admin@example.com")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            "/pc/back-office/criterion/new/",
            form={"name": name, "description": "My description", "startDateTime": None, "endDateTime": None},
        )

        assert response.status_code == 200
        assert "Le nom ne doit contenir aucun caractère d&#39;espacement" in response.data.decode("utf8")
        assert criteria_models.Criterion.query.count() == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_create_criterion_too_long(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            "/pc/back-office/criterion/new/",
            form={"name": "x" * 141, "description": "My description", "startDateTime": None, "endDateTime": None},
        )

        assert response.status_code == 200
        assert "Le nom d&#39;un tag ne peut excéder 140 caractères" in response.data.decode("utf8")
        assert criteria_models.Criterion.query.count() == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_criterion(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        offer = offers_factories.OfferFactory()
        criterion = criteria_factories.CriterionFactory(name="test_delete_criterion")
        criteria_factories.OfferCriterionFactory(offer=offer, criterion=criterion)

        assert len(offer.criteria) == 1

        data = dict(id=criterion.id)
        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post("/pc/back-office/criterion/delete/", form=data)

        assert response.status_code == 302
        assert len(offer.criteria) == 0
