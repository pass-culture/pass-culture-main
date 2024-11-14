import datetime

from flask import url_for
import pytest

from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features

from .helpers import html_parser
from .helpers.get import GetEndpointHelper


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
