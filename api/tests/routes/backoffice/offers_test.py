import dataclasses
import datetime
import decimal
from io import BytesIO
from operator import itemgetter
from unittest import mock
from unittest.mock import patch

from flask import g
from flask import url_for
import openpyxl
import pytest

from pcapi.core import search
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.backoffice.filters import format_date

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(scope="function", name="criteria")
def criteria_fixture() -> list:
    return criteria_factories.CriterionFactory.create_batch(4)


@pytest.fixture(scope="function", name="offers")
def offers_fixture(criteria) -> tuple:
    offer_with_unlimited_stock = offers_factories.OfferFactory(
        criteria=[criteria[0]],
        venue__postalCode="47000",
        venue__departementCode="47",
        subcategoryId=subcategories.MATERIEL_ART_CREATIF.id,
        author=users_factories.ProFactory(),
        extraData={"musicType": 501, "musicSubType": 510},
    )
    offer_with_limited_stock = offers_factories.EventOfferFactory(
        name="A Very Specific Name",
        lastValidationDate=datetime.date(2022, 2, 22),
        venue__postalCode="97400",
        venue__departementCode="974",
        subcategoryId=subcategories.FESTIVAL_LIVRE.id,
        validation=offers_models.OfferValidationStatus.APPROVED,
        extraData={"visa": "2023123456", "showType": 100, "showSubType": 104},
    )
    offer_with_two_criteria = offers_factories.OfferFactory(
        name="A Very Specific Name That Is Longer",
        criteria=[criteria[0], criteria[1]],
        dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        validation=offers_models.OfferValidationStatus.REJECTED,
        venue__postalCode="74000",
        venue__departementCode="74",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"ean": "9781234567890"},
    )
    offer_with_a_lot_of_types = offers_factories.OfferFactory(
        criteria=[criteria[3]],
        venue__postalCode="10000",
        venue__departementCode="10",
        subcategoryId=subcategories.JEU_EN_LIGNE.id,
        author=users_factories.ProFactory(),
        extraData={"musicType": 870, "musicSubType": 871, "showType": 1510, "showSubType": 1511},
    )
    offers_factories.StockFactory(quantity=None, offer=offer_with_unlimited_stock, price=10.1)
    offers_factories.StockFactory(offer=offer_with_unlimited_stock, price=15)
    offers_factories.EventStockFactory(
        quantity=10,
        dnBookedQuantity=0,
        offer=offer_with_limited_stock,
        beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=1),
    )
    offers_factories.EventStockFactory(
        quantity=10,
        dnBookedQuantity=5,
        offer=offer_with_limited_stock,
        beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=3),
    )
    return offer_with_unlimited_stock, offer_with_limited_stock, offer_with_two_criteria, offer_with_a_lot_of_types


class ListOffersTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.list_offers"
    needed_permission = perm_models.Permissions.READ_OFFERS

    def _get_query_args_by_id(self, id_: int) -> dict[str, str]:
        return {
            "search-0-search_field": "ID",
            "search-0-operator": "IN",
            "search-0-string": str(id_),
        }

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch offers with joinedload including extra data (1 query)
    expected_num_queries = 3

    def test_list_offers_without_filter(self, authenticated_client, offers):
        # no filter => no query to fetch offers
        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    @pytest.mark.parametrize(
        "admin_user,stock_data_expected,tag_data_expected,fraud_data_expected",
        [
            ("read_only_bo_user", True, False, False),
            ("pro_fraud_admin", False, False, True),
            ("support_pro_n2_admin", True, True, False),
        ],
    )
    def test_list_offers_by_id(
        self,
        client,
        read_only_bo_user,
        pro_fraud_admin,
        support_pro_n2_admin,
        offers,
        admin_user,
        stock_data_expected,
        tag_data_expected,
        fraud_data_expected,
    ):
        user = locals()[admin_user]
        client = client.with_bo_session_auth(user)
        query_args = self._get_query_args_by_id(offers[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(offers[0].id)
        assert rows[0]["Nom de l'offre"] == offers[0].name
        assert rows[0]["Catégorie"] == offers[0].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[0].subcategory.pro_label
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today()).strftime("%d/%m/%Y")
        assert rows[0]["Dernière validation"] == ""
        assert rows[0]["Dép."] == offers[0].venue.departementCode
        assert rows[0]["Structure"] == offers[0].venue.managingOfferer.name
        assert rows[0]["Lieu"] == offers[0].venue.name

        if stock_data_expected:
            assert rows[0]["Stock réservé"] == "0"
            assert rows[0]["Stock restant"] == "Illimité"
            assert rows[0]["Créateur de l'offre"] == offers[0].author.full_name
        else:
            assert "Stock réservé" not in rows[0]
            assert "Stock restant" not in rows[0]
            assert "Créateur de l'offre" not in rows[0]

        if tag_data_expected:
            assert rows[0]["Tag"] == offers[0].criteria[0].name
            assert rows[0]["Pond."] == ""
        else:
            assert "Tag" not in rows[0]
            assert "Pond." not in rows[0]

        if fraud_data_expected:
            assert rows[0]["Règles de conformité"] == ""
            assert rows[0]["Score data"] == ""
            assert rows[0]["Tarif"] == "10,10 € - 15,00 €"
        else:
            assert "Règles de conformité" not in rows[0]
            assert "Score data" not in rows[0]
            assert "Tarif" not in rows[0]

    def test_list_offers_by_ids_list(self, authenticated_client, offers):
        query_args = self._get_query_args_by_id(f"{offers[0].id}, {offers[2].id}\n")
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert set(int(row["ID"]) for row in rows) == {offers[0].id, offers[2].id}

    def test_list_offers_by_name(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "NAME",
            "search-0-operator": "CONTAINS",
            "search-0-string": offers[1].name,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        rows = sorted(rows, key=itemgetter("ID"))  # ensures deterministic order
        assert rows[0]["ID"] == str(offers[1].id)
        assert rows[0]["Nom de l'offre"] == offers[1].name
        assert rows[0]["Catégorie"] == offers[1].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[1].subcategory.pro_label
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today()).strftime("%d/%m/%Y")
        assert rows[0]["Dernière validation"] == "22/02/2022"
        assert rows[0]["Dép."] == offers[1].venue.departementCode
        assert rows[0]["Structure"] == offers[1].venue.managingOfferer.name
        assert rows[0]["Lieu"] == offers[1].venue.name
        assert rows[1]["ID"] == str(offers[2].id)
        assert rows[1]["Nom de l'offre"] == offers[2].name

    @pytest.mark.parametrize("ean", ["9781234567890", " 978-1234567890", "978 1234567890\t"])
    def test_list_offers_by_ean(self, authenticated_client, offers, ean):
        query_args = {
            "search-0-search_field": "EAN",
            "search-0-operator": "EQUALS",
            "search-0-string": ean,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == offers[2].id

    @pytest.mark.parametrize("visa", ["2023123456", " 2023 123456 ", "2023-123456\t"])
    def test_list_offers_by_visa(self, authenticated_client, offers, visa):
        query_args = {
            "search-0-search_field": "VISA",
            "search-0-operator": "EQUALS",
            "search-0-string": visa,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == offers[1].id

    def test_list_offers_by_creation_date(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "CREATION_DATE",
            "search-0-operator": "DATE_TO",
            "search-0-date": (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            "search-2-search_field": "CREATION_DATE",
            "search-2-operator": "DATE_FROM",
            "search-2-date": (datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}

    def test_list_offers_by_status_and_event_date(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "STATUS",
            "search-0-operator": "IN",
            "search-0-status": offers_models.OfferStatus.ACTIVE.value,
            "search-2-search_field": "EVENT_DATE",
            "search-2-operator": "DATE_TO",
            "search-2-date": (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_without_sort_should_not_have_created_date_sort_link(self, authenticated_client, offers):
        query_args = self._get_query_args_by_id(offers[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        assert "sort=dateCreated&amp;order=desc" not in str(response.data)

    def test_list_offers_with_sort_should_have_created_date_sort_link(self, authenticated_client, offers):
        query_args = self._get_query_args_by_id(offers[0].id) | {"sort": "dateCreated", "order": "asc", "q": "e"}

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        assert "sort=dateCreated&amp;order=desc" in str(response.data)

    def test_list_offers_with_and_sort_should_have_created_date_sort_link(self, authenticated_client, offers):
        query_args = {
            "sort": "dateCreated",
            "order": "asc",
            "search-0-search_field": "NAME",
            "search-0-operator": "NAME_EQUALS",
            "search-0-string": "A Very Specific Name",
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        expected_url = (
            "/pro/offer?sort=dateCreated&amp;order=desc&amp;search-0-search_field=NAME&amp;"
            "search-0-operator=NAME_EQUALS&amp;search-0-boolean=true&amp;search-0-string=A+Very+Specific+Name"
        )
        assert expected_url in str(response.data)

    @pytest.mark.parametrize(
        "operator,valid_date,not_valid_date",
        [
            (
                "DATE_FROM",
                datetime.datetime.utcnow() + datetime.timedelta(days=1),
                datetime.datetime.utcnow() - datetime.timedelta(days=1),
            ),
            (
                "DATE_TO",
                datetime.datetime.utcnow() - datetime.timedelta(days=1),
                datetime.datetime.utcnow() + datetime.timedelta(days=1),
            ),
        ],
    )
    def test_list_offers_with_booking_limit_date_filter(
        self, authenticated_client, operator, valid_date, not_valid_date
    ):
        should_be_displayed_offer = offers_factories.OfferFactory(
            stocks=[offers_factories.StockFactory(bookingLimitDatetime=valid_date)]
        )
        offers_factories.OfferFactory(stocks=[offers_factories.StockFactory()])
        offers_factories.OfferFactory(stocks=[offers_factories.StockFactory(bookingLimitDatetime=not_valid_date)])

        query_args = {
            "order": "asc",
            "search-0-search_field": "BOOKING_LIMIT_DATE",
            "search-0-operator": operator,
            "search-0-date": datetime.date.today(),
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(should_be_displayed_offer.id)

    def test_list_offers_by_event_date(self, authenticated_client, offers):
        offers_factories.EventStockFactory(beginningDatetime=datetime.date.today() + datetime.timedelta(days=1))
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime.date.today())
        offers_factories.EventStockFactory(beginningDatetime=datetime.date.today() - datetime.timedelta(days=1))

        query_args = {
            "search-0-search_field": "EVENT_DATE",
            "search-0-operator": "DATE_EQUALS",
            "search-0-date": datetime.date.today().isoformat(),
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {stock.offer.id}

    def test_list_offers_by_event_date_gte_only(self, authenticated_client, offers):
        # Query investigated for performance issue in PC-23801
        query_args = {
            "limit": "100",
            "search-0-search_field": "EVENT_DATE",
            "search-0-operator": "DATE_FROM",
            "search-0-status": offers_models.OfferStatus.ACTIVE.value,
            "search-0-integer": "",
            "search-0-string": "",
            "search-0-date": (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    @pytest.mark.parametrize(
        "operator,criteria_indexes,expected_offer_indexes",
        [
            ("IN", [0], [0, 2]),
            ("NOT_IN", [0], [1, 3]),
            ("NOT_IN", [1], [0, 1, 3]),
            ("NOT_IN", [2], [0, 1, 2, 3]),
            ("NOT_IN", [0, 1], [1, 3]),
            ("NOT_EXIST", [], [1]),
        ],
    )
    def test_list_offers_by_criterion(
        self, authenticated_client, criteria, offers, operator, criteria_indexes, expected_offer_indexes
    ):
        query_args = {
            "search-3-search_field": "TAG",
            "search-3-operator": operator,
            "search-3-criteria": [criteria[criterion_index].id for criterion_index in criteria_indexes],
        }
        with assert_num_queries(
            self.expected_num_queries + int(bool(criteria_indexes))
        ):  # +1 because of reloading selected criterion in the form when criteria arg is set
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[index].id for index in expected_offer_indexes}

    def test_list_offers_by_in_and_not_in_criteria(self, authenticated_client, criteria, offers):
        query_args = {
            "search-0-search_field": "TAG",
            "search-0-operator": "IN",
            "search-0-criteria": criteria[0].id,
            "search-2-search_field": "TAG",
            "search-2-operator": "NOT_IN",
            "search-2-criteria": criteria[1].id,
        }
        with assert_num_queries(
            self.expected_num_queries + 2
        ):  # +2 because of reloading selected criterion in the form, in both filters
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[0].id}

    def test_list_offers_by_category(self, authenticated_client, offers):
        query_args = {
            "search-3-search_field": "CATEGORY",
            "search-3-operator": "IN",
            "search-3-category": categories.LIVRE.id,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id, offers[2].id}

    def test_list_offers_by_subcategory(self, authenticated_client, offers):
        query_args = {
            "search-3-search_field": "SUBCATEGORY",
            "search-3-operator": "IN",
            "search-3-subcategory": subcategories.LIVRE_PAPIER.id,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}

    def test_list_offers_by_price(self, authenticated_client, offers):

        query_args = {
            "search-3-search_field": "PRICE",
            "search-3-operator": "GREATER_THAN_OR_EQUAL_TO",
            "search-3-price": 12.20,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(offers[0].id)

    def test_list_offers_by_price_multiple_stocks(self, authenticated_client):

        offer_with_multiple_stocks_valid_and_not_valid = offers_factories.OfferFactory()

        offers_factories.StockFactory(
            price=15,
            offer=offer_with_multiple_stocks_valid_and_not_valid,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )

        offers_factories.StockFactory(
            price=16,
            offer=offer_with_multiple_stocks_valid_and_not_valid,
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=2),
            bookingLimitDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        )

        query_args = {
            "search-3-search_field": "PRICE",
            "search-3-operator": "EQUALS",
            "search-3-price": 16,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(offer_with_multiple_stocks_valid_and_not_valid.id)

    def test_list_offers_by_price_no_offer_is_valid(self, authenticated_client, offers):

        query_args = {
            "search-3-search_field": "PRICE",
            "search-3-operator": "GREATER_THAN_OR_EQUAL_TO",
            "search-3-price": 120000.20,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 0

    def test_list_offers_by_department(self, authenticated_client, offers):
        query_args = {
            "search-3-search_field": "DEPARTMENT",
            "search-3-operator": "IN",
            "search-3-department": ["74", "47", "971"],
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[0].id, offers[2].id}

    def test_list_offers_by_region(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "REGION",
            "search-0-operator": "IN",
            "search-0-region": ["La Réunion", "Auvergne-Rhône-Alpes"],
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {int(row["ID"]) for row in rows} == {offers[1].id, offers[2].id}

    def test_list_offers_by_music_type(self, authenticated_client, offers):
        query_args = {
            "search-3-search_field": "MUSIC_TYPE",
            "search-3-operator": "IN",
            "search-3-music_type": ["501", "520", "800"],
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)
        assert int(row[0]["ID"]) == offers[0].id

    def test_list_offers_by_music_sub_type(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "MUSIC_SUB_TYPE",
            "search-0-operator": "IN",
            "search-0-music_sub_type": ["510", "511", "512"],
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)
        assert int(row[0]["ID"]) == offers[0].id

    def test_list_offers_by_show_type(self, authenticated_client, offers):
        query_args = {
            "search-3-search_field": "SHOW_TYPE",
            "search-3-operator": "IN",
            "search-3-show_type": ["200", "100", "300"],
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)
        assert int(row[0]["ID"]) == offers[1].id

    def test_list_offers_by_show_sub_type(self, authenticated_client, offers):
        query_args = {
            "search-3-search_field": "SHOW_SUB_TYPE",
            "search-3-operator": "IN",
            "search-3-show_sub_type": ["104", "105", "106"],
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)
        assert int(row[0]["ID"]) == offers[1].id

    def test_list_offers_by_venue(self, authenticated_client, offers):
        venue_id = offers[1].venueId
        query_args = {
            "search-3-search_field": "VENUE",
            "search-3-operator": "IN",
            "search-3-venue": venue_id,
        }
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue in the form
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_by_address(self, authenticated_client, offers):
        for offer in offers[:3]:
            offer.offererAddress = offerers_factories.OffererAddressFactory(offerer=offer.venue.managingOfferer)
            db.session.add(offer)
        db.session.flush()

        address_id = offers[2].offererAddress.addressId
        query_args = {
            "search-0-search_field": "ADDRESS",
            "search-0-operator": "IN",
            "search-0-address": address_id,
        }
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected address in the form
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}

    def test_list_offers_by_status(self, authenticated_client, offers):
        offer = offers_factories.OfferFactory(isActive=False)

        query_args = {
            "search-0-search_field": "STATUS",
            "search-0-operator": "IN",
            "search-0-status": "INACTIVE",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offer.id}

    def test_list_offers_by_offerer(self, authenticated_client, offers):
        offerer_id = offers[1].venue.managingOffererId
        query_args = {
            "search-3-search_field": "OFFERER",
            "search-3-operator": "IN",
            "search-3-offerer": offerer_id,
        }
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected offerer in the form
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_by_validation(self, authenticated_client, offers):
        status = offers[2].validation
        query_args = {
            "search-3-search_field": "VALIDATION",
            "search-3-operator": "IN",
            "search-3-validation": status.value,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}
        assert rows[0]["État"] == "Rejetée"

    def test_list_offers_by_four_filters(self, authenticated_client, criteria, offers):
        criterion_id = criteria[1].id
        venue_id = offers[2].venueId

        query_args = {
            "search-0-search_field": "TAG",
            "search-0-operator": "IN",
            "search-0-criteria": criterion_id,
            "search-1-search_field": "CATEGORY",
            "search-1-operator": "IN",
            "search-1-category": categories.LIVRE.id,
            "search-2-search_field": "DEPARTMENT",
            "search-2-operator": "IN",
            "search-2-department": "74",
            "search-3-search_field": "VENUE",
            "search-3-operator": "IN",
            "search-3-venue": venue_id,
        }
        with assert_num_queries(self.expected_num_queries + 2):  # +2 because of reloading selected criterion and venue
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}

    @pytest.mark.parametrize(
        "order,expected_list",
        [
            ("", ["Offre 4", "Offre 3", "Offre 2", "Offre 1"]),
            ("asc", ["Offre 4", "Offre 3", "Offre 2", "Offre 1"]),
            ("desc", ["Offre 1", "Offre 2", "Offre 3", "Offre 4"]),
        ],
    )
    def test_list_offers_pending_from_validated_offerers_sorted_by_date(
        self, authenticated_client, order, expected_list
    ):
        # test results when clicking on pending offers link (home page)
        offers_factories.OfferFactory(
            validation=offers_models.OfferValidationStatus.PENDING,
            venue__managingOfferer=offerers_factories.NotValidatedOffererFactory(),
        )

        validated_venue = offerers_factories.VenueFactory()
        for days_ago in (2, 4, 1, 3):
            offers_factories.OfferFactory(
                name=f"Offre {days_ago}",
                dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=days_ago),
                validation=offers_models.OfferValidationStatus.PENDING,
                venue=validated_venue,
            )

        query_args = {
            "only_validated_offerers": "on",
            "sort": "dateCreated",
            "order": order,
            "search-3-search_field": "VALIDATION",
            "search-3-operator": "IN",
            "search-3-validation": offers_models.OfferValidationStatus.PENDING.value,
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    **query_args,
                )
            )
            assert response.status_code == 200

        # must be sorted, older first
        rows = html_parser.extract_table_rows(response.data)
        assert [row["Nom de l'offre"] for row in rows] == expected_list

    def test_list_offers_with_flagging_rules(self, authenticated_client):
        rule_1 = offers_factories.OfferValidationRuleFactory(name="Règle magique")
        rule_2 = offers_factories.OfferValidationRuleFactory(name="Règle moldue")
        offers_factories.OfferFactory(
            validation=offers_models.OfferValidationStatus.PENDING,
            flaggingValidationRules=[rule_1, rule_2],
            extraData={
                "complianceScore": 50,
                "complianceReasons": ["stock_price", "offer_subcategoryid", "offer_description"],
            },
        )

        query_args = {
            "search-0-search_field": "VALIDATION",
            "search-0-operator": "IN",
            "search-0-validation": offers_models.OfferValidationStatus.PENDING.value,
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    **query_args,
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Règles de conformité"] == ", ".join([rule_1.name, rule_2.name])
        assert rows[0]["Score data"] == "50"

        # Check tooltip associated with "Score data"
        tooltip = html_parser.get_soup(response.data).find(
            "i", class_="bi-info-circle", attrs={"data-bs-toggle": "tooltip", "data-bs-html": "true"}
        )
        tooltip_html_content = tooltip.attrs.get("data-bs-title")
        assert (
            html_parser.content_as_text(tooltip_html_content, from_encoding=None)
            == "Raison de score faible : Prix Sous-catégorie Description de l'offre"
        )

    def test_list_offers_by_no_tags(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "TAG",
            "search-0-operator": "NOT_EXIST",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_by_no_tags_and_validation(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "TAG",
            "search-0-operator": "NOT_EXIST",
            "search-2-search_field": "VALIDATION",
            "search-2-operator": "IN",
            "search-2-validation": offers_models.OfferValidationStatus.APPROVED.value,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_by_no_tags_and_other_validation(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "TAG",
            "search-0-operator": "NOT_EXIST",
            "search-2-search_field": "VALIDATION",
            "search-2-operator": "IN",
            "search-2-validation": offers_models.OfferValidationStatus.PENDING.value,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 0

    def test_list_offers_has_provider(self, authenticated_client):
        provider = providers_factories.ProviderFactory()
        offers_factories.OfferFactory(name="good", idAtProvider="pouet", lastProvider=provider)
        offers_factories.OfferFactory(name="bad")
        query_args = {
            "search-0-search_field": "SYNCHRONIZED",
            "search-0-operator": "NULLABLE",
            "search-0-boolean": "true",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom de l'offre"] == "good"

    def test_list_offers_has_no_provider(self, authenticated_client):
        provider = providers_factories.ProviderFactory()
        offers_factories.OfferFactory(name="bad", idAtProvider="pouet", lastProvider=provider)
        offers_factories.OfferFactory(name="good")
        query_args = {
            "search-0-search_field": "SYNCHRONIZED",
            "search-0-operator": "NULLABLE",
            "search-0-boolean": "false",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom de l'offre"] == "good"

    def test_list_offers_by_provider(self, authenticated_client):
        provider = providers_factories.ProviderFactory()
        provider2 = providers_factories.ProviderFactory()
        offers_factories.OfferFactory(name="good", idAtProvider="pouet", lastProvider=provider)
        offers_factories.OfferFactory(
            idAtProvider="pouet2",
            lastProvider=provider2,
        )
        offers_factories.OfferFactory()
        query_args = {
            "search-0-search_field": "PROVIDER",
            "search-0-operator": "IN",
            "search-0-provider": str(provider.id),
        }
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected providers
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom de l'offre"] == "good"

    def test_list_offers_by_not_provider(self, authenticated_client):
        provider = providers_factories.ProviderFactory()
        provider2 = providers_factories.ProviderFactory()
        offers_factories.OfferFactory(name="good", idAtProvider="pouet", lastProvider=provider)
        offers_factories.OfferFactory(
            idAtProvider="pouet2",
            lastProvider=provider2,
        )
        offers_factories.OfferFactory()
        query_args = {
            "search-0-search_field": "PROVIDER",
            "search-0-operator": "NOT_IN",
            "search-0-provider": str(provider2.id),
        }
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected providers
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom de l'offre"] == "good"

    # === Error cases ===

    def test_list_offers_by_invalid_field(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "CATEGRY",
            "search-0-operator": "IN",
            "search-0-category": categories.LIVRE.id,
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert html_parser.extract_alert(response.data) == "Le filtre CATEGRY est invalide."

    def test_list_offers_by_category_and_missing_date(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "CATEGORY",
            "search-0-operator": "IN",
            "search-0-category": categories.LIVRE.id,
            "search-2-search_field": "CREATION_DATE",
            "search-2-operator": "DATE_FROM",
            "search-4-search_field": "BOOKING_LIMIT_DATE",
            "search-4-operator": "DATE_TO",
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert (
            html_parser.extract_alert(response.data)
            == "Le filtre « Date de création » est vide. Le filtre « Date limite de réservation » est vide."
        )

    def test_list_offers_by_invalid_criteria(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "TAG",
            "search-0-operator": "IN",
            "search-0-criteria": "A",
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert html_parser.extract_alert(response.data) == "Le filtre « Tag » est vide."

    def test_list_offers_using_invalid_operator(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "CATEGORY",
            "search-0-operator": "OUT",
            "search-0-category": "13",
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert "Not a valid choice." in html_parser.extract_warnings(response.data)[0]

    @pytest.mark.parametrize(
        "search_field,value",
        [
            ("ID", "12, 34, A"),
            ("EAN", "123"),
            ("EAN", "1234567890ABC"),
            ("VISA", "1234567890123"),
            ("VISA", "1234567ABC"),
        ],
    )
    def test_list_offers_by_invalid_format(self, authenticated_client, search_field, value):
        query_args = {
            "search-0-search_field": search_field,
            "search-0-operator": "EQUALS",
            "search-0-string": value,
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

    # === Result content ===

    @pytest.mark.parametrize("first_quantity,second_quantity,expected_remaining", [(10, 7, 12), (5, 7, 7)])
    def test_list_offers_check_stock_limited(
        self, client, support_pro_n2_admin, first_quantity, second_quantity, expected_remaining
    ):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=first_quantity, dnBookedQuantity=5)
        offers_factories.StockFactory(offer=offer, quantity=second_quantity, dnBookedQuantity=0)

        query_args = self._get_query_args_by_id(offer.id)
        client = client.with_bo_session_auth(support_pro_n2_admin)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "5"
        assert row["Stock restant"] == str(expected_remaining)

    @pytest.mark.parametrize("first_quantity,second_quantity", [(None, None), (None, 10), (5, None)])
    def test_list_offers_check_stock_unlimited(self, client, support_pro_n2_admin, first_quantity, second_quantity):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=first_quantity, dnBookedQuantity=5)
        offers_factories.StockFactory(offer=offer, quantity=second_quantity, dnBookedQuantity=0)

        query_args = self._get_query_args_by_id(offer.id)
        client = client.with_bo_session_auth(support_pro_n2_admin)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "5"
        assert row["Stock restant"] == "Illimité"

    def test_list_offers_check_stock_sold_out(self, client, support_pro_n2_admin):
        offer = offers_factories.EventOfferFactory()
        offers_factories.EventStockFactory(offer=offer, quantity=5, dnBookedQuantity=5)
        offers_factories.EventStockFactory(offer=offer, quantity=7, dnBookedQuantity=7)

        query_args = self._get_query_args_by_id(offer.id)
        client = client.with_bo_session_auth(support_pro_n2_admin)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "12"
        assert row["Stock restant"] == "0"

    def test_list_offers_check_stock_expired(self, client, support_pro_n2_admin):
        offer = offers_factories.EventOfferFactory()
        offers_factories.EventStockFactory(
            offer=offer,
            quantity=7,
            dnBookedQuantity=2,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        offers_factories.EventStockFactory(
            offer=offer,
            quantity=9,
            dnBookedQuantity=3,
            bookingLimitDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        offers_factories.EventStockFactory(
            offer=offer,
            quantity=None,  # unlimited
            dnBookedQuantity=7,
            bookingLimitDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        query_args = self._get_query_args_by_id(offer.id)
        client = client.with_bo_session_auth(support_pro_n2_admin)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "12"
        assert row["Stock restant"] == "0"

    def test_list_offers_check_stock_not_active(self, client, support_pro_n2_admin):
        for status in offers_models.OfferValidationStatus:
            if status != offers_models.OfferValidationStatus.APPROVED:
                offers_factories.StockFactory(offer__validation=status)
        offers_factories.StockFactory(offer__venue__managingOfferer=offerers_factories.NotValidatedOffererFactory())
        offers_factories.StockFactory(offer__venue__managingOfferer__isActive=False)

        query_args = {
            "search-0-search_field": "CATEGORY",
            "search-0-operator": "IN",
            "search-0-category": categories.FILM.id,
        }

        client = client.with_bo_session_auth(support_pro_n2_admin)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == len(offers_models.OfferValidationStatus) - 1 + 2
        for row in rows:
            assert row["Stock réservé"] == "0"
            assert row["Stock restant"] == "-"

    def test_list_offers_price_with_different_stocks(self, client, pro_fraud_admin):
        offer = offers_factories.OfferFactory()

        client = client.with_bo_session_auth(pro_fraud_admin)
        query_args = self._get_query_args_by_id(offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Tarif"] == "-"

        offers_factories.StockFactory(offer=offer, price=10)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Tarif"] == "10,00 €"

        offers_factories.StockFactory(offer=offer, price=15)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Tarif"] == "10,00 € - 15,00 €"

    def test_list_offers_with_offerer_confidence_rule(self, client, pro_fraud_admin):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer__name="Offerer")
        offer = offers_factories.OfferFactory(venue__managingOfferer=rule.offerer, venue__name="Venue")

        client = client.with_bo_session_auth(pro_fraud_admin)
        query_args = self._get_query_args_by_id(offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Structure"] == "Offerer Revue manuelle"
        assert rows[0]["Lieu"] == "Venue"

    def test_list_offers_with_venue_confidence_rule(self, client, pro_fraud_admin):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory(
            venue__name="Venue", venue__managingOfferer__name="Offerer"
        )
        offer = offers_factories.OfferFactory(venue=rule.venue)

        client = client.with_bo_session_auth(pro_fraud_admin)
        query_args = self._get_query_args_by_id(offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Structure"] == "Offerer"
        assert rows[0]["Lieu"] == "Venue Revue manuelle"


class EditOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.edit_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    @patch("pcapi.core.search.reindex_offer_ids")
    def test_update_offer_tags(self, mock_reindex_offer_ids, legit_user, authenticated_client, criteria):
        offer_to_edit = offers_factories.OfferFactory(
            name="A Very Specific Name That Is Longer",
            criteria=[criteria[0]],
            venue__postalCode="74000",
            venue__departementCode="74",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        chosen_ranking_weight = 22
        base_form = {"criteria": [criteria[0].id, criteria[1].id], "rankingWeight": chosen_ranking_weight}

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        db.session.refresh(offer_to_edit)
        assert offer_to_edit.rankingWeight == chosen_ranking_weight
        assert set(offer_to_edit.criteria) == {criteria[0], criteria[1]}

        # offer should be reindexed
        mock_reindex_offer_ids.assert_called_once_with([offer_to_edit.id])
        mock_reindex_offer_ids.reset_mock()

        # New Update without rankingWeight
        base_form = {"criteria": [criteria[2].id, criteria[1].id], "rankingWeight": ""}
        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_edit.id, form=base_form)
        assert response.status_code == 303

        db.session.refresh(offer_to_edit)
        assert offer_to_edit.rankingWeight is None
        assert set(offer_to_edit.criteria) == {criteria[1], criteria[2]}

        # offer should be reindexed
        mock_reindex_offer_ids.assert_called_once_with([offer_to_edit.id])


class GetEditOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_edit_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(3):  # session + current user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class GetBatchEditOfferFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.get_batch_edit_offer_form"
    endpoint_kwargs = {"offer_ids": "1,2"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_get_empty_edit_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint, _external=True)

        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

    def test_get_edit_form_with_values_test(self, legit_user, authenticated_client, criteria):
        offers = offers_factories.OfferFactory.create_batch(
            3, subcategoryId=subcategories.LIVRE_PAPIER.id, criteria=[criteria[2]], rankingWeight=22
        )
        selected_offers = offers[:-1]  # select all but the last offer

        offer_ids = ",".join(str(offer.id) for offer in selected_offers)
        base_form = {
            "object_ids": offer_ids,
            "criteria": [criteria[2].id],
            "rankingWeight": "0",
        }  # as it is already get in the modal form

        response = self._update_offers_form(authenticated_client, base_form)
        assert response.status_code == 200

        # Edit N°1 - The two first offers
        base_form["criteria"].extend([criteria[0].id, criteria[1].id])
        response = self._update_offers(authenticated_client, base_form)
        assert response.status_code == 303
        for offer in offers[:-1]:
            assert set(offer.criteria) == set(criteria[:3])
            assert offer.rankingWeight is None

        # Edit N°2 - Only the last offer
        choosen_ranking_weight = 12
        base_form = {
            "criteria": [criteria[2].id, criteria[3].id],
            "rankingWeight": choosen_ranking_weight,
        }  # new set of criteria
        response = self._update_offer(authenticated_client, offers[-1], base_form)
        assert response.status_code == 303

        assert offers[0].rankingWeight is None
        assert offers[1].rankingWeight is None
        assert offers[2].rankingWeight == choosen_ranking_weight

        assert set(offers[0].criteria) == set(criteria[:3])
        assert set(offers[1].criteria) == set(criteria[:3])
        assert set(offers[2].criteria) == set(criteria[2:])

    def _update_offers_form(self, authenticated_client, form):
        edit_url = url_for("backoffice_web.offer.list_offers")
        authenticated_client.get(edit_url)

        url = url_for(self.endpoint)
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)

    def _update_offers(self, authenticated_client, form):
        url = url_for("backoffice_web.offer.batch_edit_offer")
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)

    def _update_offer(self, authenticated_client, offer, form):
        url = url_for("backoffice_web.offer.edit_offer", offer_id=offer.id)
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)


class BatchEditOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.batch_edit_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_batch_edit_offer(self, mock_async_index, legit_user, authenticated_client, criteria):
        offers = offers_factories.OfferFactory.create_batch(3)
        parameter_ids = ",".join(str(offer.id) for offer in offers)
        chosen_ranking_weight = 2
        base_form = {
            "criteria": [criteria[0].id, criteria[1].id],
            "rankingWeight": chosen_ranking_weight,
            "object_ids": parameter_ids,
        }

        # Expected queries:
        # 1 x user_session
        # 1 x user
        # 1 x all offers
        # 1 x all criteria
        # 1 x update offers (for 3 offers)
        # 1 x insert into offer_criterion (for 3 insertions)
        response = self.post_to_endpoint(authenticated_client, form=base_form, expected_num_queries=6)
        assert response.status_code == 303

        for offer in offers:
            assert offer.rankingWeight == chosen_ranking_weight
            assert len(offer.criteria) == 2
            assert criteria[0] in offer.criteria
            assert criteria[2] not in offer.criteria

        mock_async_index.assert_called_once_with(
            [offer.id for offer in offers],
            reason=search.IndexationReason.OFFER_BATCH_UPDATE,
        )


class ValidateOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.validate_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_validate_offer_with_stocks(self, legit_user, authenticated_client):
        offer_to_validate = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.REJECTED)
        offers_factories.StockFactory(offer=offer_to_validate, price=10.1)
        offers_factories.StockFactory(offer=offer_to_validate, price=1.01)

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_validate.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        db.session.refresh(offer_to_validate)
        assert offer_to_validate.isActive is True
        assert offer_to_validate.validation == offers_models.OfferValidationStatus.APPROVED
        assert offer_to_validate.lastValidationType == OfferValidationType.MANUAL
        assert offer_to_validate.lastValidationDate.date() == datetime.date.today()
        assert offer_to_validate.lastValidationPrice == decimal.Decimal("10.1")

    def test_validate_offer_without_stocks(self, legit_user, authenticated_client):
        offer_to_validate = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.REJECTED)

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_validate.id)
        assert response.status_code == 303

        assert offer_to_validate.isActive is True
        assert offer_to_validate.lastValidationType == OfferValidationType.MANUAL
        assert offer_to_validate.lastValidationPrice is None
        assert offer_to_validate.validation == offers_models.OfferValidationStatus.APPROVED


class GetValidateOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_validate_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_validate_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(3):  # session + current user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class RejectOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.reject_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_reject_offer(self, legit_user, authenticated_client):
        offer_to_reject = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.APPROVED)
        confirmed_booking = bookings_factories.BookingFactory(
            user=users_factories.BeneficiaryGrant18Factory(),
            stock__offer=offer_to_reject,
            status=BookingStatus.CONFIRMED,
        )

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_reject.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        assert offer_to_reject.isActive is False
        assert offer_to_reject.validation == offers_models.OfferValidationStatus.REJECTED
        assert offer_to_reject.lastValidationType == OfferValidationType.MANUAL
        assert offer_to_reject.lastValidationDate.date() == datetime.date.today()
        assert offer_to_reject.lastValidationPrice is None

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["To"] == confirmed_booking.user.email
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[0]["params"]["REJECTED"] is True
        assert mails_testing.outbox[1]["To"] == offer_to_reject.venue.bookingEmail
        assert mails_testing.outbox[1]["template"] == dataclasses.asdict(
            TransactionalEmail.OFFER_VALIDATED_TO_REJECTED_TO_PRO.value
        )


class GetRejectOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_reject_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id, _external=True)

        with assert_num_queries(3):  # session + current user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class BatchOfferValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.batch_validate_offers"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_batch_validate_offers(self, legit_user, authenticated_client):
        offers = offers_factories.OfferFactory.create_batch(3, validation=offers_models.OfferValidationStatus.DRAFT)
        for offer in offers:
            offers_factories.StockFactory(offer=offer, price=10.1)
        parameter_ids = ",".join(str(offer.id) for offer in offers)

        # user_session, user, select offer (3 in 1 query), update offer (3 in 1 query)
        response = self.post_to_endpoint(
            authenticated_client, form={"object_ids": parameter_ids}, expected_num_queries=4
        )

        assert response.status_code == 303
        for offer in offers:
            db.session.refresh(offer)
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
            assert offer.isActive is True
            assert offer.lastValidationType is OfferValidationType.MANUAL
            assert offer.validation is offers_models.OfferValidationStatus.APPROVED
            assert offer.lastValidationAuthor == legit_user
            assert offer.lastValidationPrice == decimal.Decimal("10.1")


class BatchOfferRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.batch_reject_offers"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_batch_reject_offers(self, legit_user, authenticated_client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        draft_offer = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.DRAFT)
        pending_offer = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.PENDING)
        confirmed_offer = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.APPROVED)
        confirmed_booking = bookings_factories.BookingFactory(
            user=beneficiary, stock__offer=confirmed_offer, status=BookingStatus.CONFIRMED
        )
        parameter_ids = ",".join(str(offer.id) for offer in [draft_offer, pending_offer, confirmed_offer])

        assert confirmed_booking.status == BookingStatus.CONFIRMED

        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert confirmed_booking.status == BookingStatus.CANCELLED
        assert response.status_code == 303
        for offer in [draft_offer, pending_offer, confirmed_offer]:
            db.session.refresh(offer)
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
            assert offer.isActive is False
            assert offer.lastValidationType is OfferValidationType.MANUAL
            assert offer.validation is offers_models.OfferValidationStatus.REJECTED
            assert offer.lastValidationAuthor == legit_user

        assert len(mails_testing.outbox) == 4
        emails_dict = {email_data["To"]: email_data for email_data in mails_testing.outbox}
        assert confirmed_booking.user.email in emails_dict
        assert emails_dict[confirmed_booking.user.email]["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value
        )
        assert emails_dict[confirmed_booking.user.email]["params"]["REJECTED"] is True
        assert draft_offer.venue.bookingEmail in emails_dict
        assert emails_dict[draft_offer.venue.bookingEmail]["template"] == dataclasses.asdict(
            TransactionalEmail.OFFER_REJECTION_TO_PRO.value
        )
        assert pending_offer.venue.bookingEmail in emails_dict
        assert emails_dict[pending_offer.venue.bookingEmail]["template"] == dataclasses.asdict(
            TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value
        )
        assert confirmed_offer.venue.bookingEmail in emails_dict
        assert emails_dict[confirmed_offer.venue.bookingEmail]["template"] == dataclasses.asdict(
            TransactionalEmail.OFFER_VALIDATED_TO_REJECTED_TO_PRO.value
        )


class GetOfferDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_offer_details"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + user + offer with joined data
    expected_num_queries = 3

    def test_get_detail_offer(self, authenticated_client):
        offer = offers_factories.OfferFactory(
            withdrawalDetails="Demander à la caisse",
            extraData={
                "ean": "1234567891234",
                "complianceScore": 55,
                "author": "Author",
                "editeur": "Editor",
                "complianceReasons": ["stock_price", "offer_subcategoryid", "offer_description"],
            },
        )
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Offer ID : {offer.id}" in card_text
        assert "Catégorie : Films, vidéos" in card_text
        assert "Sous-catégorie : Support physique (DVD, Blu-ray...)" in card_text
        assert "Statut : Épuisée" in card_text
        assert "État : Validée" in card_text
        assert "Score data : 55 " in card_text
        assert "Raison de score faible : Prix Sous-catégorie Description de l'offre " in card_text
        assert "Structure : Le Petit Rintintin Management" in card_text
        assert "Lieu : Le Petit Rintintin" in card_text
        assert "Utilisateur de la dernière validation" not in card_text
        assert "Date de dernière validation" not in card_text
        assert "Resynchroniser l'offre dans Algolia" in card_text
        assert "Modifier le lieu" not in card_text
        assert "Demander à la caisse" in card_text
        assert b"Auteur :</span> Author" in response.data
        assert b"EAN :</span> 1234567891234" in response.data
        assert "Éditeur :</span> Editor".encode() in response.data

        assert html_parser.count_table_rows(response.data) == 0

    def test_get_detail_event_offer(self, authenticated_client):
        offer = offers_factories.OfferFactory(
            name="good movie",
            offererAddress=None,
            subcategoryId=subcategories.SEANCE_CINE.id,
            durationMinutes=133,
            description="description",
            idAtProvider="pouet provider",
            isActive=True,
            isDuo=False,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=False,
            extraData={
                "cast": [
                    "first actor",
                    "second actor",
                    "third actor",
                ],
                "type": "FEATURE_FILM",
                "visa": "123456",
                "genres": [
                    "ADVENTURE",
                    "ANIMATION",
                    "DRAMA",
                ],
                "theater": {
                    "allocine_room_id": "W1234",
                    "allocine_movie_id": 654321,
                },
                "companies": [
                    {
                        "company": {
                            "name": "Company1 Name",
                        },
                        "activity": "InternationalDistributionExports",
                    },
                    {
                        "company": {
                            "name": "Company2 Name",
                        },
                        "activity": "Distribution",
                    },
                    {
                        "company": {
                            "name": "Company3 Name",
                        },
                        "activity": "Production",
                    },
                    {
                        "company": {"name": "Company4 Name"},
                        "activity": "Production",
                    },
                    {
                        "company": {"name": "Company5 Name"},
                        "activity": "PrAgency",
                    },
                ],
                "countries": [
                    "Never Land",
                ],
                "releaseDate": "2023-04-12",
                "stageDirector": "Georges Méliès",
                "diffusionVersion": "VO",
                "performer": "John Doe",
            },
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)

        response = authenticated_client.get(url)
        assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Offer ID : {offer.id}" in card_text
        assert "Catégorie : Cinéma" in card_text
        assert "Sous-catégorie : Séance de cinéma " in card_text
        assert "Genres : ADVENTURE, ANIMATION, DRAMA " in card_text
        assert "Statut : Épuisée" in card_text
        assert "État : Validée" in card_text
        assert "Structure : Le Petit Rintintin Management" in card_text
        assert "Lieu : Le Petit Rintintin" in card_text
        assert "Adresse :" not in card_text  # no offererAddress
        assert "Utilisateur de la dernière validation" not in card_text
        assert "Date de dernière validation" not in card_text
        assert "Resynchroniser l'offre dans Algolia" in card_text
        assert "Modifier le lieu" not in card_text
        assert b"Identifiant chez le fournisseur :</span> pouet provider" in response.data
        assert b"Langue :</span> VO" in response.data
        assert "Durée :</span> 133 minutes".encode() in response.data
        assert b"Accessible aux handicaps auditifs :</span> Oui" in response.data
        assert b"Accessible aux handicaps mentaux :</span> Non" in response.data
        assert "Accessible aux handicaps moteurs :</span> Non renseigné".encode() in response.data
        assert b"Accessible aux handicaps visuels :</span> Non" in response.data
        assert b"Description :</span> description" in response.data
        assert "Interprète :</span> John Doe".encode() in response.data

        assert html_parser.count_table_rows(response.data) == 0

    def test_get_detail_validated_offer(self, legit_user, authenticated_client):
        validation_date = datetime.datetime.utcnow()
        offer = offers_factories.OfferFactory(
            lastValidationDate=validation_date,
            validation=offers_models.OfferValidationStatus.APPROVED,
            lastValidationAuthor=legit_user,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in card_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in card_text

    def test_get_detail_offer_without_show_subtype(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(
            withdrawalDetails="Demander à la caisse",
            extraData={"showType": 1510},
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_get_detail_offer_without_music_subtype(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(
            withdrawalDetails="Demander à la caisse",
            extraData={"musicType": 1510},
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_get_detail_offer_display_modify_offer_button(self, client):
        offer = offers_factories.OfferFactory()
        manage_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.MANAGE_OFFERS.name).one()
        read_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.READ_OFFERS.name).one()
        role = perm_factories.RoleFactory(permissions=[read_offers, manage_offers])
        user = users_factories.UserFactory()
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        authenticated_client = client.with_bo_session_auth(user)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]

        assert "Modifier l'offre" in card_text
        assert "Valider l'offre" not in card_text
        assert "Rejeter l'offre" not in card_text

    def test_get_detail_offer_display_validation_buttons_fraud(self, client):
        offer = offers_factories.OfferFactory()
        pro_fraud_actions = perm_models.Permission.query.filter_by(
            name=perm_models.Permissions.PRO_FRAUD_ACTIONS.name
        ).one()
        read_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.READ_OFFERS.name).one()
        role = perm_factories.RoleFactory(permissions=[read_offers, pro_fraud_actions])
        user = users_factories.UserFactory()
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        authenticated_client = client.with_bo_session_auth(user)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]

        assert "Modifier l'offre" not in card_text
        assert "Valider l'offre" in card_text
        assert "Rejeter l'offre" in card_text

    def test_get_detail_rejected_offer(self, legit_user, authenticated_client):
        validation_date = datetime.datetime.utcnow()
        offer = offers_factories.OfferFactory(
            lastValidationDate=validation_date,
            validation=offers_models.OfferValidationStatus.REJECTED,
            lastValidationAuthor=legit_user,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in card_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in card_text

    def test_get_offer_details_with_one_expired_stock(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        expired_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=1), price=6.66
        )

        query_count = self.expected_num_queries
        query_count += 1  # _get_editable_stock
        query_count += 1  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["Stock ID"] == str(expired_stock.id)
        assert stocks_rows[0]["Stock réservé"] == "0"
        assert stocks_rows[0]["Stock restant"] == "0"
        assert stocks_rows[0]["Prix"] == "6,66 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(expired_stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    def test_get_offer_details_with_two_expired_stocks(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        expired_stock_1 = offers_factories.EventStockFactory(
            offer=offer,
            quantity=100,
            dnBookedQuantity=70,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
        )
        expired_stock_2 = offers_factories.EventStockFactory(
            offer=offer,
            quantity=None,
            dnBookedQuantity=25,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        )

        query_count = self.expected_num_queries
        query_count += 1  # _get_editable_stock
        query_count += 1  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 2
        assert stocks_rows[0]["Stock ID"] == str(expired_stock_1.id)
        assert stocks_rows[0]["Stock réservé"] == "70"
        assert stocks_rows[0]["Stock restant"] == "0"
        assert stocks_rows[0]["Prix"] == "10,10 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(expired_stock_1.beginningDatetime, "%d/%m/%Y à %Hh%M")

        assert stocks_rows[1]["Stock ID"] == str(expired_stock_2.id)
        assert stocks_rows[1]["Stock réservé"] == "25"
        assert stocks_rows[1]["Stock restant"] == "0"
        assert stocks_rows[1]["Prix"] == "10,10 €"
        assert stocks_rows[1]["Date / Heure"] == format_date(expired_stock_2.beginningDatetime, "%d/%m/%Y à %Hh%M")

    @pytest.mark.parametrize(
        "quantity,booked_quantity,expected_remaining",
        [
            (1000, 0, "1000"),
            (1000, 50, "950"),
            (1000, 1000, "0"),
            (None, 0, "Illimité"),
            (None, 50, "Illimité"),
        ],
    )
    def test_get_offer_details_with_one_bookable_stock(
        self, legit_user, authenticated_client, quantity, booked_quantity, expected_remaining
    ):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        stock = offers_factories.EventStockFactory(offer=offer, quantity=quantity, dnBookedQuantity=booked_quantity)

        query_count = self.expected_num_queries
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["Stock ID"] == str(stock.id)
        assert stocks_rows[0]["Stock réservé"] == str(booked_quantity)
        assert stocks_rows[0]["Stock restant"] == expected_remaining
        assert stocks_rows[0]["Prix"] == "10,10 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    def test_get_event_offer(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=venue.managingOfferer, pricing_point=venue)
        offer = offers_factories.EventOfferFactory(venue=venue)

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        # Additional queries to check if "Modifier le lieu" should be displayed or not":
        # - _get_editable_stock
        # - count stocks with beginningDatetime in the past
        # - count reimbursed bookings
        # - fetch destination venue candidates
        with assert_num_queries(self.expected_num_queries + 4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert "Modifier le lieu" in cards_text[0]

    def test_get_offer_details_with_offerer_address(self, authenticated_client):
        address = geography_factories.AddressFactory(
            street="1v Place Jacques Rueff",
            postalCode="75007",
            city="Paris",
            latitude=48.85605,
            longitude=2.298,
            inseeCode="75107",
            banId="75107_4803_00001_v",
        )
        offerer_adress = offerers_factories.OffererAddressFactory(label="Champ de Mars", address=address)
        offer = offers_factories.OfferFactory(
            offererAddressId=offerer_adress.id, venue__managingOfferer=offerer_adress.offerer
        )

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Adresse : Champ de Mars 1v Place Jacques Rueff 75007 Paris 48.85605, 2.29800" in text


class IndexOfferButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT
    button_label = "Resynchroniser l'offre dans Algolia"

    @property
    def path(self):
        offer = offers_factories.OfferFactory()
        return url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id)


class MoveOfferVenueButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT
    button_label = "Modifier le lieu"

    @property
    def path(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, pricing_point=venue)
        offer = offers_factories.EventOfferFactory(venue=venue)
        return url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id)


class IndexOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.reindex"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_index_offer(self, mocked_async_index_offer_ids, authenticated_client):
        offer = offers_factories.OfferFactory()

        response = self.post_to_endpoint(authenticated_client, offer_id=offer.id)
        assert response.status_code == 303

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "La resynchronisation de l'offre a été demandée." in html_parser.extract_alert(redirected_response.data)

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == {offer.id}


@pytest.fixture(scope="function", name="venues_in_same_offerer")
def venues_in_same_offerer_fixture() -> tuple[offerers_models.Venue]:
    offerer = offerers_factories.OffererFactory()
    source_venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    venue_with_same_pricing_point = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point=source_venue)
    venue_with_own_pricing_point = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    venue_without_pricing_point = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point=None)
    return source_venue, venue_with_same_pricing_point, venue_with_own_pricing_point, venue_without_pricing_point


class EditOfferVenueTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.edit_offer_venue"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def _test_move_event(
        self,
        mocked_async_index_offer_ids,
        authenticated_client,
        source_venue: offerers_models.Venue,
        destination_venue: offerers_models.Venue,
        notify_beneficiary: bool,
        with_pricings: bool = True,
        expected_error: str | None = None,
    ):
        offer = offers_factories.EventOfferFactory(venue=source_venue)

        stock1 = offers_factories.EventStockFactory(offer=offer)
        booking1_1 = bookings_factories.BookingFactory(stock=stock1)
        booking1_2 = bookings_factories.UsedBookingFactory(stock=stock1)
        finance_event1_2 = finance_factories.UsedBookingFinanceEventFactory(booking=booking1_2)
        if with_pricings:
            finance_factories.PricingFactory(event=finance_event1_2, booking=booking1_2)

        stock2 = offers_factories.EventStockFactory(offer=offer)
        booking2_1 = bookings_factories.UsedBookingFactory(stock=stock2)
        finance_event2_1 = finance_factories.UsedBookingFinanceEventFactory(booking=booking2_1)
        if with_pricings:
            finance_factories.PricingFactory(event=finance_event2_1, booking=booking2_1)
        booking2_2 = bookings_factories.CancelledBookingFactory(stock=stock2)

        # other objects to validate queries filters
        offers_factories.EventStockFactory(beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=7))
        bookings_factories.ReimbursedBookingFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            offer_id=offer.id,
            form={"venue": destination_venue.id, "notify_beneficiary": "on" if notify_beneficiary else ""},
        )
        assert response.status_code == 303

        if not expected_error:
            assert (
                html_parser.extract_alert(authenticated_client.get(response.location).data)
                == f"L'offre a été déplacée vers le lieu {destination_venue.name}"
            )

            mocked_async_index_offer_ids.assert_called_once_with(
                {offer.id}, reason=search.IndexationReason.OFFER_UPDATE, log_extra={"changes": {"venueId"}}
            )

            # Mail is sent only for in-going booking
            assert len(mails_testing.outbox) == (1 if notify_beneficiary else 0)

            expected_venue = destination_venue
        else:
            assert html_parser.extract_alert(authenticated_client.get(response.location).data) == expected_error

            mocked_async_index_offer_ids.assert_not_called()
            assert len(mails_testing.outbox) == 0

            expected_venue = source_venue

        assert offer.venueId == expected_venue.id
        assert booking1_1.venueId == expected_venue.id
        assert booking1_2.venueId == expected_venue.id
        assert booking2_1.venueId == expected_venue.id
        assert booking2_2.venueId == expected_venue.id
        assert finance_event1_2.venueId == expected_venue.id
        assert finance_event1_2.pricingPointId == expected_venue.current_pricing_point.id
        assert finance_event2_1.venueId == expected_venue.id
        assert finance_event2_1.pricingPointId == expected_venue.current_pricing_point.id

    @pytest.mark.parametrize("notify_beneficiary", [False, True])
    @patch("pcapi.core.search.async_index_offer_ids")
    def test_move_event_offer_when_venue_has_same_pricing_point(
        self, mocked_async_index_offer_ids, authenticated_client, venues_in_same_offerer, notify_beneficiary
    ):
        source_venue, venue_with_same_pricing_point, _, _ = venues_in_same_offerer
        self._test_move_event(
            mocked_async_index_offer_ids,
            authenticated_client,
            source_venue,
            venue_with_same_pricing_point,
            notify_beneficiary,
        )

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_move_event_offer_without_pricing_when_venue_has_different_pricing_point(
        self, mocked_async_index_offer_ids, authenticated_client, venues_in_same_offerer
    ):
        source_venue, _, venue_with_own_pricing_point, _ = venues_in_same_offerer
        self._test_move_event(
            mocked_async_index_offer_ids,
            authenticated_client,
            source_venue,
            venue_with_own_pricing_point,
            True,
            with_pricings=False,
        )

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_move_event_offer_with_pricings_when_venue_has_different_pricing_point(
        self, mocked_async_index_offer_ids, authenticated_client, venues_in_same_offerer
    ):
        source_venue, _, venue_with_own_pricing_point, _ = venues_in_same_offerer
        self._test_move_event(
            mocked_async_index_offer_ids,
            authenticated_client,
            source_venue,
            venue_with_own_pricing_point,
            True,
            expected_error="Le lieu de cette offre ne peut pas être modifié : "
            "Il existe des réservations valorisées sur un autre point de valorisation que celui du nouveau lieu",
        )

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_cant_move_when_destination_venue_has_no_pricing_point(
        self, mocked_async_index_offer_ids, authenticated_client, venues_in_same_offerer
    ):
        # This case should not happen if the user only selects from venues dropdown list
        source_venue, _, _, venue_without_pricing_point = venues_in_same_offerer
        self._test_move_event(
            mocked_async_index_offer_ids,
            authenticated_client,
            source_venue,
            venue_without_pricing_point,
            True,
            with_pricings=False,
            expected_error="Le lieu de cette offre ne peut pas être modifié : Ce lieu n'est pas éligible au transfert de l'offre",
        )

    def test_cant_move_when_offer_is_not_an_event(self, authenticated_client, venues_in_same_offerer):
        source_venue, destination_venue, _, _ = venues_in_same_offerer
        offer = offers_factories.ThingStockFactory(offer__venue=source_venue).offer

        response = self.post_to_endpoint(authenticated_client, offer_id=offer.id, form={"venue": destination_venue.id})

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le lieu de cette offre ne peut pas être modifié : L'offre n'est pas un évènement"
        )

    def test_cant_move_when_event_is_in_the_past(self, authenticated_client, venues_in_same_offerer):
        source_venue, destination_venue, _, _ = venues_in_same_offerer
        offer = offers_factories.EventOfferFactory(venue=source_venue)
        offers_factories.EventStockFactory.create_batch(
            2, offer=offer, beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )

        response = self.post_to_endpoint(authenticated_client, offer_id=offer.id, form={"venue": destination_venue.id})

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le lieu de cette offre ne peut pas être modifié : L'évènement a déjà eu lieu pour 2 stocks"
        )

    def test_cant_move_when_reimbursed_bookings(self, authenticated_client, venues_in_same_offerer):
        source_venue, destination_venue, _, _ = venues_in_same_offerer
        stock = offers_factories.EventStockFactory(offer__venue=source_venue)
        bookings_factories.ReimbursedBookingFactory(stock=stock)

        response = self.post_to_endpoint(
            authenticated_client, offer_id=stock.offer.id, form={"venue": destination_venue.id}
        )

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le lieu de cette offre ne peut pas être modifié : 1 réservation est déjà remboursée sur cette offre"
        )

    @patch("pcapi.core.search.async_index_offer_ids")
    def test_move_event_offer_with_price_category(
        self, mocked_async_index_offer_ids, authenticated_client, venues_in_same_offerer
    ):
        source_venue, destination_venue, _, _ = venues_in_same_offerer

        offer = offers_factories.EventOfferFactory(venue=source_venue)
        gold_label = offers_factories.PriceCategoryLabelFactory(label="Gold", venue=offer.venue)
        gold_stock = offers_factories.EventStockFactory(
            offer=offer,
            priceCategory=offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=gold_label),
        )
        silver_label = offers_factories.PriceCategoryLabelFactory(label="Silver", venue=offer.venue)
        silver_stock = offers_factories.EventStockFactory(
            offer=offer,
            priceCategory=offers_factories.PriceCategoryFactory(offer=offer, priceCategoryLabel=silver_label),
        )
        destination_silver_label = offers_factories.PriceCategoryLabelFactory(label="Silver", venue=destination_venue)

        response = self.post_to_endpoint(
            authenticated_client,
            offer_id=offer.id,
            form={"venue": destination_venue.id, "notify_beneficiary": ""},
        )
        assert response.status_code == 303

        assert offer.venueId == destination_venue.id
        assert gold_stock.priceCategory.priceCategoryLabel.venue == destination_venue
        assert gold_stock.priceCategory.priceCategoryLabel != gold_label
        assert gold_label.venue == source_venue
        assert silver_stock.priceCategory.priceCategoryLabel.venue == destination_venue
        assert silver_stock.priceCategory.priceCategoryLabel == destination_silver_label
        assert offers_models.PriceCategoryLabel.query.count() == 4


class GetOfferStockEditFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_offer_stock_edit_form"
    endpoint_kwargs = {"offer_id": 1, "stock_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    # session + current user + tested_query
    expected_num_queries = 3

    def test_get_stock_edit_form(self, authenticated_client):
        booking = bookings_factories.UsedBookingFactory(stock__offer__subcategoryId=subcategories.CONFERENCE.id)

        form_url = url_for(self.endpoint, offer_id=booking.stock.offer.id, stock_id=booking.stock.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

    def test_get_stock_edit_form_non_event_offer(self, authenticated_client):
        stock = offers_factories.StockFactory()

        form_url = url_for(self.endpoint, offer_id=stock.offer.id, stock_id=stock.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

        assert b"Ce stock n&#39;est pas \xc3\xa9ditable." in response.data

    def test_get_stock_edit_form_no_eligible_bookings(self, authenticated_client, app):
        booking = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories.CONFERENCE.id, status=BookingStatus.CANCELLED
        )

        form_url = url_for(self.endpoint, offer_id=booking.stock.offer.id, stock_id=booking.stock.id)

        try:
            response = authenticated_client.get(form_url)
        finally:
            app.redis_client.delete(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK)

        assert response.status_code == 200
        assert b"Ce stock n&#39;est pas \xc3\xa9ditable." in response.data

    def test_get_stock_edit_form_running_cashflow_script_test(self, authenticated_client, app):
        booking = bookings_factories.UsedBookingFactory(stock__offer__subcategoryId=subcategories.CONFERENCE.id)

        form_url = url_for(self.endpoint, offer_id=booking.stock.offer.id, stock_id=booking.stock.id)
        app.redis_client.set(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK, "1", 600)

        try:
            response = authenticated_client.get(form_url)
        finally:
            app.redis_client.delete(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK)

        assert response.status_code == 200
        assert (
            "Le script de génération des cashflows est en cours, veuillez réessayer plus tard.".encode("utf-8")
            in response.data
        )


class EditOfferStockTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.edit_offer_stock"
    endpoint_kwargs = {"offer_id": 1, "stock_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_offer_stock_edit_used_booking(self, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONFERENCE.id)
        venue = offer.venue
        stock_to_edit = offers_factories.StockFactory(
            offer=offer,
            price=decimal.Decimal("123.45"),
        )
        booking_to_edit = bookings_factories.UsedBookingFactory(
            stock=stock_to_edit,
            amount=decimal.Decimal("123.45"),
        )
        stock_untouched = offers_factories.StockFactory(
            offer=offer,
            price=decimal.Decimal("123.45"),
        )
        booking_untouched = bookings_factories.UsedBookingFactory(
            stock=stock_untouched,
            amount=decimal.Decimal("123.45"),
        )
        cancelled_event = finance_factories.FinanceEventFactory(
            booking=booking_to_edit, venue=venue, pricingPoint=venue
        )
        cancelled_pricing = finance_factories.PricingFactory(
            event=cancelled_event,
            pricingPoint=venue,
        )
        later_booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue=venue,
            stock__offer__subcategoryId=subcategories.CONFERENCE.id,
            stock__beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        )
        later_event = finance_factories.FinanceEventFactory(
            booking=later_booking,
            venue=venue,
            pricingPoint=venue,
            pricingOrderingDate=later_booking.stock.beginningDatetime,
        )
        later_pricing = finance_factories.PricingFactory(
            event=later_event,
            pricingPoint=venue,
        )
        later_pricing_id = later_pricing.id

        response = self.post_to_endpoint(
            authenticated_client, offer_id=offer.id, stock_id=stock_to_edit.id, form={"price": 50.1}
        )

        db.session.refresh(booking_to_edit)
        db.session.refresh(booking_untouched)
        db.session.refresh(stock_to_edit)
        db.session.refresh(stock_untouched)
        db.session.refresh(cancelled_event)
        db.session.refresh(later_event)

        assert response.status_code == 303
        assert stock_untouched.price == decimal.Decimal("123.45")
        assert booking_untouched.amount == decimal.Decimal("123.45")
        assert cancelled_event.status == finance_models.FinanceEventStatus.READY
        assert cancelled_pricing.status == finance_models.PricingStatus.CANCELLED

        assert stock_to_edit.price == decimal.Decimal("50.1")
        assert booking_to_edit.amount == decimal.Decimal("50.1")
        assert later_event.status == finance_models.FinanceEventStatus.READY
        assert finance_models.Pricing.query.filter_by(id=later_pricing_id).count() == 0

    def test_offer_stock_edit_with_french_decimal(self, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONFERENCE.id)
        stock_to_edit = offers_factories.StockFactory(
            offer=offer,
            price=decimal.Decimal("123.45"),
        )
        booking_to_edit = bookings_factories.UsedBookingFactory(
            stock=stock_to_edit,
            amount=decimal.Decimal("123.45"),
        )

        response = self.post_to_endpoint(
            authenticated_client, offer_id=offer.id, stock_id=stock_to_edit.id, form={"price": "50,1"}
        )

        db.session.refresh(booking_to_edit)
        db.session.refresh(stock_to_edit)

        assert response.status_code == 303

        assert stock_to_edit.price == decimal.Decimal("50.1")
        assert booking_to_edit.amount == decimal.Decimal("50.1")

    def test_offer_stock_edit_confirmed_booking(self, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONFERENCE.id)
        stock_to_edit = offers_factories.StockFactory(
            offer=offer,
            price=decimal.Decimal("123.45"),
        )
        booking_to_edit = bookings_factories.BookingFactory(
            status=BookingStatus.CONFIRMED,
            stock=stock_to_edit,
            amount=decimal.Decimal("123.45"),
        )

        response = self.post_to_endpoint(
            authenticated_client, offer_id=offer.id, stock_id=stock_to_edit.id, form={"price": 50.1}
        )

        db.session.refresh(booking_to_edit)
        db.session.refresh(stock_to_edit)

        assert response.status_code == 303
        assert stock_to_edit.price == decimal.Decimal("50.1")
        assert booking_to_edit.amount == decimal.Decimal("50.1")

    def test_offer_stock_edit_cashfow_script_running(self, authenticated_client, app):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONFERENCE.id)
        venue = offer.venue
        event = finance_factories.FinanceEventFactory(
            booking__amount=decimal.Decimal("123.45"),
            booking__stock__offer=offer,
            booking__stock__price=decimal.Decimal("123.45"),
            venue=venue,
            pricingPoint=venue,
        )
        finance_factories.PricingFactory(
            event=event,
            pricingPoint=venue,
        )
        app.redis_client.set(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK, "1", 600)

        try:
            response = self.post_to_endpoint(
                authenticated_client,
                offer_id=offer.id,
                stock_id=event.booking.stock.id,
                form={"price": 50.1},
            )
        finally:
            app.redis_client.delete(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK)

        db.session.refresh(event.booking)

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id, _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id))
        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data)
            == "Le script de génération des cashflows est en cours, veuillez réessayer plus tard."
        )

        assert event.booking.stock.price == decimal.Decimal("123.45")

    def test_offer_stock_edit_offer_not_an_event(self, authenticated_client, app):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        venue = offer.venue
        event = finance_factories.FinanceEventFactory(
            booking__amount=decimal.Decimal("123.45"),
            booking__stock__offer=offer,
            booking__stock__price=decimal.Decimal("123.45"),
            venue=venue,
            pricingPoint=venue,
        )
        finance_factories.PricingFactory(
            event=event,
            pricingPoint=venue,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            offer_id=offer.id,
            stock_id=event.booking.stock.id,
            form={"price": 50.1},
        )

        db.session.refresh(event.booking)

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id, _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id))
        assert response.status_code == 200
        assert html_parser.extract_alert(response.data) == "Ce stock n'est pas éditable."

        assert event.booking.stock.price == decimal.Decimal("123.45")

    def test_offer_stock_edit_no_used_or_confirmed_bookings(self, authenticated_client, app):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONFERENCE.id)
        stock = offers_factories.StockFactory(
            offer=offer,
            price=decimal.Decimal("123.45"),
        )
        bookings_factories.BookingFactory(
            status=BookingStatus.CANCELLED,
            stock=stock,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            offer_id=offer.id,
            stock_id=stock.id,
            form={"price": 50.1},
        )
        db.session.refresh(stock)

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id, _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id))
        assert response.status_code == 200
        assert html_parser.extract_alert(response.data) == "Ce stock n'est pas éditable."

        assert stock.price == decimal.Decimal("123.45")

    def test_offer_stock_edit_raising_price(self, authenticated_client, app):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CONFERENCE.id)
        venue = offer.venue
        event = finance_factories.FinanceEventFactory(
            booking__amount=decimal.Decimal("123.45"),
            booking__stock__offer=offer,
            booking__stock__price=decimal.Decimal("123.45"),
            venue=venue,
            pricingPoint=venue,
        )
        finance_factories.PricingFactory(
            event=event,
            pricingPoint=venue,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            offer_id=offer.id,
            stock_id=event.booking.stock.id,
            form={"price": 200.0},
        )

        db.session.refresh(event.booking)

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id, _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id))
        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data) == "Le prix ne doit pas être supérieur au prix original du stock."
        )

        assert event.booking.stock.price == decimal.Decimal("123.45")


class DownloadBookingsCSVTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.download_bookings_csv"
    endpoint_kwargs = {"offer_id": 1, "stock_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + current user + bookings
    expected_num_queries = 3

    def test_download_bookings_csv(self, legit_user, authenticated_client):
        offerer = offerers_factories.UserOffererFactory().offerer  # because of join on UserOfferers
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=offerer)
        bookings_factories.UsedBookingFactory(stock__offer=offer)
        bookings_factories.ReimbursedBookingFactory(stock__offer=offer)
        bookings_factories.BookingFactory(stock__offer=offer)
        bookings_factories.BookingFactory()  # other offer

        url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert len(response.data.split(b"\n")) == 1 + 3 + 1


class DownloadBookingsXLSXTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.download_bookings_xlsx"
    endpoint_kwargs = {"offer_id": 1, "stock_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + current user + bookings
    expected_num_queries = 3

    def reader_from_response(self, response):
        wb = openpyxl.load_workbook(BytesIO(response.data))
        return wb.active

    def test_download_bookings_xlsx(self, authenticated_client):
        offerer = offerers_factories.UserOffererFactory().offerer  # because of join on UserOfferers
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=offerer)
        booking1 = bookings_factories.UsedBookingFactory(stock__offer=offer)
        booking2 = bookings_factories.ReimbursedBookingFactory(stock__offer=offer)
        bookings_factories.BookingFactory()  # other offer

        url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        sheet = self.reader_from_response(response)
        assert sheet.cell(row=1, column=1).value == "Lieu"
        assert sheet.cell(row=2, column=1).value == booking1.venue.name
        assert sheet.cell(row=3, column=1).value == booking2.venue.name
        assert sheet.cell(row=4, column=1).value == None
