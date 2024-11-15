import datetime

from flask import url_for
import pytest

from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.history import models as history_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.models import db

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class ListChroniclesTest(GetEndpointHelper):
    endpoint = "backoffice_web.chronicles.list_chronicles"
    needed_permission = perm_models.Permissions.READ_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # list chronicles
    # count chronicles
    expected_num_queries = 5

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_without_filters(self, authenticated_client):
        product = offers_factories.ProductFactory()
        chronicle_with_product = chronicles_factories.ChronicleFactory(products=[product])
        chronicle_without_product = chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["ID"] == str(chronicle_without_product.id)
        assert rows[0]["Titres des œuvres"] == ""
        assert rows[0]["Contenu"] == chronicle_without_product.content
        assert rows[0]["Date de création"] == chronicle_without_product.dateCreated.strftime("%d/%m/%Y")
        assert rows[1]["ID"] == str(chronicle_with_product.id)
        assert rows[1]["Titres des œuvres"] == product.name
        assert rows[1]["Contenu"] == chronicle_with_product.content
        assert rows[1]["Date de création"] == chronicle_with_product.dateCreated.strftime("%d/%m/%Y")

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_ean(self, authenticated_client):
        ean = "1234567890123"
        product = offers_factories.ProductFactory(extraData={"ean": ean})
        chronicle_with_product = chronicles_factories.ChronicleFactory(products=[product])
        chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=ean))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_with_product.id)

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_content(self, authenticated_client):
        chronicle_to_find = chronicles_factories.ChronicleFactory(
            content="Deux hommes, et même dix, peuvent bien en craindre un ;",
        )
        chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="HomMe bien",
                    research_type="CHRONICLE_CONTENT",
                ),
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_to_find.id)

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_product_name(self, authenticated_client):
        product = offers_factories.ProductFactory(name="My super product")
        chronicle_with_product = chronicles_factories.ChronicleFactory(products=[product])
        chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="SUPER",
                    research_type="PRODUCT_NAME",
                ),
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_with_product.id)

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_creation_date(self, authenticated_client):
        chronicle_to_find = chronicles_factories.ChronicleFactory()
        chronicles_factories.ChronicleFactory(dateCreated=datetime.date(1999, 12, 12))
        chronicles_factories.ChronicleFactory(dateCreated=datetime.date(2038, 1, 19))
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, date_range="01/01/2000 - 18/01/2038"),
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_to_find.id)


class PublishChronicleTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.publish_chronicle"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # get chronicle
    # update chronicle
    # reload chronicle
    # ListChroniclesTest.expected_num_queries (follow redirect)
    expected_num_queries = 6 + ListChroniclesTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_publish_chronicle(self, authenticated_client, legit_user):
        chronicle = chronicles_factories.ChronicleFactory(
            isActive=False,
        )

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            client=authenticated_client,
        )
        db.session.refresh(chronicle)

        assert response.status_code == 200
        assert chronicle.isActive
        action_log = history_models.ActionHistory.query.one()
        assert action_log.actionType == history_models.ActionType.CHRONICLE_PUBLISHED
        assert action_log.chronicle is chronicle
        assert action_log.authorUser is legit_user

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_publish_chronicle_does_not_exist(self, authenticated_client):
        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries - (1 + ListChroniclesTest.expected_num_queries),
            chronicle_id=0,
            client=authenticated_client,
        )
        assert response.status_code == 404


class UnpublishChronicleTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.unpublish_chronicle"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # get chronicle
    # update chronicle
    # reload chronicle
    # ListChroniclesTest.expected_num_queries (follow redirect)
    expected_num_queries = 6 + ListChroniclesTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_unpublish_chronicle(self, authenticated_client, legit_user):
        chronicle = chronicles_factories.ChronicleFactory(
            isActive=True,
        )

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            client=authenticated_client,
        )
        db.session.refresh(chronicle)

        assert response.status_code == 200
        assert not chronicle.isActive
        action_log = history_models.ActionHistory.query.one()
        assert action_log.actionType == history_models.ActionType.CHRONICLE_UNPUBLISHED
        assert action_log.chronicle is chronicle
        assert action_log.authorUser is legit_user

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_unpublish_chronicle_does_not_exist(self, authenticated_client):
        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries - (1 + ListChroniclesTest.expected_num_queries),
            chronicle_id=0,
            client=authenticated_client,
        )
        assert response.status_code == 404
