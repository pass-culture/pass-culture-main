import datetime
from operator import itemgetter
from unittest import mock
from unittest.mock import patch

from flask import g
from flask import url_for
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
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
        product__subcategoryId=subcategories.MATERIEL_ART_CREATIF.id,
    )
    offer_with_limited_stock = offers_factories.EventOfferFactory(
        name="A Very Specific Name",
        lastValidationDate=datetime.date(2022, 2, 22),
        venue__postalCode="97400",
        venue__departementCode="974",
        product__subcategoryId=subcategories.FESTIVAL_LIVRE.id,
        validation=offers_models.OfferValidationStatus.APPROVED,
        extraData={"visa": "2023123456"},
    )
    offer_with_two_criteria = offers_factories.OfferFactory(
        name="A Very Specific Name That Is Longer",
        criteria=[criteria[0], criteria[1]],
        dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        validation=offers_models.OfferValidationStatus.REJECTED,
        venue__postalCode="74000",
        venue__departementCode="74",
        product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"ean": "9781234567890"},
    )
    offers_factories.StockFactory(quantity=None, offer=offer_with_unlimited_stock)
    offers_factories.StockFactory(offer=offer_with_unlimited_stock)
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
    return offer_with_unlimited_stock, offer_with_limited_stock, offer_with_two_criteria


class ListOffersTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.list_offers"
    needed_permission = perm_models.Permissions.READ_OFFERS

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

    # === Basic search ===

    def test_list_offers_by_id(self, authenticated_client, offers):
        searched_id = str(offers[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == searched_id
        assert rows[0]["Nom de l'offre"] == offers[0].name
        assert rows[0]["Catégorie"] == offers[0].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[0].subcategory.pro_label
        assert rows[0]["Stock réservé"] == "0"
        assert rows[0]["Stock restant"] == "Illimité"
        assert rows[0]["Tag"] == offers[0].criteria[0].name
        assert rows[0]["Pond."] == ""
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today()).strftime("%d/%m/%Y")
        assert rows[0]["Dernière validation"] == ""
        assert rows[0]["Dép."] == offers[0].venue.departementCode
        assert rows[0]["Structure"] == offers[0].venue.managingOfferer.name
        assert rows[0]["Lieu"] == offers[0].venue.name

    def test_list_offers_by_ids_list(self, authenticated_client, offers):
        searched_ids = f"{offers[0].id}, {offers[2].id}\n"
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_ids))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert set(int(row["ID"]) for row in rows) == {offers[0].id, offers[2].id}

    def test_list_offers_by_name(self, authenticated_client, offers):
        searched_name = offers[1].name
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_name))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        rows = sorted(rows, key=itemgetter("ID"))  # ensures deterministic order
        assert rows[0]["ID"] == str(offers[1].id)
        assert rows[0]["Nom de l'offre"] == offers[1].name
        assert rows[0]["Catégorie"] == offers[1].category.pro_label
        assert rows[0]["Sous-catégorie"] == offers[1].subcategory.pro_label
        assert rows[0]["Stock réservé"] == "5"
        assert rows[0]["Stock restant"] == "15"
        assert rows[0]["Tag"] == ""
        assert rows[0]["Pond."] == ""
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
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=ean))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == offers[2].id

    @pytest.mark.parametrize("visa", ["2023123456", " 2023 123456 ", "2023-123456\t"])
    def test_list_offers_by_visa(self, authenticated_client, offers, visa):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=visa))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert int(rows[0]["ID"]) == offers[1].id

    def test_list_offers_by_category(self, authenticated_client, offers):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category=[categories.LIVRE.id]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id, offers[2].id}

    def test_list_offers_by_offerer(self, authenticated_client, offers):
        offerer_id = offers[1].venue.managingOffererId
        # +1 because of reloading selected offerer in the form
        # +1 because of reloading selected offerer in the form for display
        with assert_num_queries(self.expected_num_queries + 2):
            response = authenticated_client.get(url_for(self.endpoint, offerer=[offerer_id]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    # === Advanced search ===

    def test_list_offers_advanced_search_by_date(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "CREATION_DATE",
            "search-0-operator": "LESS_THAN",
            "search-0-date": (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            "search-2-search_field": "CREATION_DATE",
            "search-2-operator": "GREATER_THAN_OR_EQUAL_TO",
            "search-2-date": (datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[2].id}

    def test_list_offers_advanced_search_by_status_and_event_date(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "STATUS",
            "search-0-operator": "IN",
            "search-0-status": offers_models.OfferStatus.ACTIVE.value,
            "search-2-search_field": "EVENT_DATE",
            "search-2-operator": "LESS_THAN",
            "search-2-date": (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_without_sort_should_not_have_created_date_sort_link(self, authenticated_client, offers):
        searched_id = str(offers[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        expected_url = "/pro/offer?sort=dateCreated&amp;order=desc"
        assert expected_url not in str(response.data)

    def test_list_offers_with_sort_should_have_created_date_sort_link(self, authenticated_client, offers):
        query_args = {"sort": "dateCreated", "order": "asc", "q": "e"}

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        expected_url = "/pro/offer?q=e&amp;sort=dateCreated&amp;order=desc"
        assert expected_url in str(response.data)

    def test_list_offers_with_advanced_search_and_sort_should_have_created_date_sort_link(
        self, authenticated_client, offers
    ):
        query_args = {
            "sort": "dateCreated",
            "order": "asc",
            "search-0-search_field": "NAME",
            "search-0-operator": "STR_EQUALS",
            "search-0-string": "A Very Specific Name",
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        expected_url = (
            "/pro/offer?sort=dateCreated&amp;order=desc&amp;search-0-search_field=NAME&amp;"
            "search-0-operator=STR_EQUALS&amp;search-0-string=A+Very+Specific+Name"
        )
        assert expected_url in str(response.data)

    @pytest.mark.parametrize(
        "operator,valid_date,not_valid_date",
        [
            (
                "GREATER_THAN_OR_EQUAL_TO",
                datetime.datetime.utcnow() + datetime.timedelta(days=1),
                datetime.datetime.utcnow() - datetime.timedelta(days=1),
            ),
            (
                "LESS_THAN",
                datetime.datetime.utcnow() - datetime.timedelta(days=1),
                datetime.datetime.utcnow() + datetime.timedelta(days=1),
            ),
        ],
    )
    def test_list_offers_advanced_search_with_booking_limit_date_filter(
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

    def test_list_offers_advanced_search_by_event_date(self, authenticated_client, offers):
        offers_factories.EventStockFactory(beginningDatetime=datetime.date.today() + datetime.timedelta(days=1))
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime.date.today())
        offers_factories.EventStockFactory(beginningDatetime=datetime.date.today() - datetime.timedelta(days=1))

        query_args = {
            "search-0-search_field": "EVENT_DATE",
            "search-0-operator": "LESS_THAN",
            "search-0-date": (datetime.date.today() + datetime.timedelta(days=1)).isoformat(),
            "search-2-search_field": "EVENT_DATE",
            "search-2-operator": "GREATER_THAN_OR_EQUAL_TO",
            "search-2-date": datetime.date.today().isoformat(),
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {stock.offer.id}

    def test_list_offers_advanced_search_by_event_date_gte_only(self, authenticated_client, offers):
        # Query investigated for performance issue in PC-23801
        query_args = {
            "limit": "100",
            "search-0-search_field": "EVENT_DATE",
            "search-0-operator": "GREATER_THAN_OR_EQUAL_TO",
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

    def test_list_offers_advanced_search_by_criteria(self, authenticated_client, criteria, offers):
        criterion_id = criteria[0].id
        query_args = {
            "search-3-search_field": "TAG",
            "search-3-operator": "IN",
            "search-3-criteria": criterion_id,
        }
        with assert_num_queries(
            self.expected_num_queries + 1
        ):  # +1 because of reloading selected criterion in the form
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[0].id, offers[2].id}

    def test_list_offers_advanced_search_by_category(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_subcategory(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_department(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_venue(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_status(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_offerer(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_validation(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_all_filters(self, authenticated_client, criteria, offers):
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
    def test_list_offers_advanced_search_pending_from_validated_offerers_sorted_by_date(
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

    def test_list_offers_advanced_search_with_flagging_rules(self, authenticated_client):
        rule_1 = offers_factories.OfferValidationRuleFactory(name="Règle magique")
        rule_2 = offers_factories.OfferValidationRuleFactory(name="Règle moldue")
        offers_factories.OfferFactory(
            validation=offers_models.OfferValidationStatus.PENDING,
            flaggingValidationRules=[rule_1, rule_2],
            extraData={"complianceScore": 50},
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

    def test_list_offers_advanced_search_by_no_tags(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "TAG",
            "search-0-operator": "NOT_EXIST",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {offers[1].id}

    def test_list_offers_advanced_search_by_no_tags_and_validation(self, authenticated_client, offers):
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

    def test_list_offers_advanced_search_by_no_tags_and_other_validation(self, authenticated_client, offers):
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

    # === Advanced search: error cases ===

    def test_list_offers_advanced_search_by_invalid_field(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "CATEGRY",
            "search-0-operator": "IN",
            "search-0-category": categories.LIVRE.id,
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert html_parser.extract_alert(response.data) == "Le filtre CATEGRY est invalide."

    def test_list_offers_advanced_search_by_category_and_missing_date(self, authenticated_client, offers):
        query_args = {
            "search-0-search_field": "CATEGORY",
            "search-0-operator": "IN",
            "search-0-category": categories.LIVRE.id,
            "search-2-search_field": "CREATION_DATE",
            "search-2-operator": "GREATER_THAN_OR_EQUAL_TO",
            "search-4-search_field": "BOOKING_LIMIT_DATE",
            "search-4-operator": "LESS_THAN",
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert (
            html_parser.extract_alert(response.data)
            == "Le filtre « Date de création » est vide. Le filtre « Date limite de réservation » est vide."
        )

    # === Result content ===

    @pytest.mark.parametrize("first_quantity,second_quantity,expected_remaining", [(10, 7, 12), (5, 7, 7)])
    def test_list_offers_check_stock_limited(
        self, authenticated_client, first_quantity, second_quantity, expected_remaining
    ):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=first_quantity, dnBookedQuantity=5)
        offers_factories.StockFactory(offer=offer, quantity=second_quantity, dnBookedQuantity=0)

        searched_id = str(offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "5"
        assert row["Stock restant"] == str(expected_remaining)

    @pytest.mark.parametrize("first_quantity,second_quantity", [(None, None), (None, 10), (5, None)])
    def test_list_offers_check_stock_unlimited(self, authenticated_client, first_quantity, second_quantity):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=first_quantity, dnBookedQuantity=5)
        offers_factories.StockFactory(offer=offer, quantity=second_quantity, dnBookedQuantity=0)

        searched_id = str(offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "5"
        assert row["Stock restant"] == "Illimité"

    def test_list_offers_check_stock_sold_out(self, authenticated_client):
        offer = offers_factories.EventOfferFactory()
        offers_factories.EventStockFactory(offer=offer, quantity=5, dnBookedQuantity=5)
        offers_factories.EventStockFactory(offer=offer, quantity=7, dnBookedQuantity=7)

        searched_id = str(offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "12"
        assert row["Stock restant"] == "0"

    def test_list_offers_check_stock_expired(self, authenticated_client):
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
        searched_id = str(offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        row = html_parser.extract_table_rows(response.data)[0]
        assert row["Stock réservé"] == "12"
        assert row["Stock restant"] == "0"

    def test_list_offers_check_stock_not_active(self, authenticated_client):
        for status in offers_models.OfferValidationStatus:
            if status != offers_models.OfferValidationStatus.APPROVED:
                offers_factories.StockFactory(offer__validation=status)
        offers_factories.StockFactory(offer__venue__managingOfferer=offerers_factories.NotValidatedOffererFactory())
        offers_factories.StockFactory(offer__venue__managingOfferer__isActive=False)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category=[categories.FILM.id]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == len(offers_models.OfferValidationStatus) - 1 + 2
        for row in rows:
            assert row["Stock réservé"] == "0"
            assert row["Stock restant"] == "-"


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
            product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        choosen_ranking_weight = 22
        base_form = {"criteria": [criteria[0].id, criteria[1].id], "rankingWeight": choosen_ranking_weight}

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        offer_list_url = url_for("backoffice_web.offer.list_offers", q=offer_to_edit.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["Pond."] == str(choosen_ranking_weight)
        assert criteria[0].name in row[0]["Tag"]
        assert criteria[1].name in row[0]["Tag"]
        assert criteria[2].name not in row[0]["Tag"]

        # offer should be reindexed
        mock_reindex_offer_ids.assert_called_once_with([offer_to_edit.id])
        mock_reindex_offer_ids.reset_mock()

        # New Update without rankingWeight
        base_form = {"criteria": [criteria[2].id, criteria[1].id], "rankingWeight": ""}
        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_edit.id, form=base_form)
        assert response.status_code == 303

        offer_list_url = url_for("backoffice_web.offer.list_offers", q=offer_to_edit.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["Pond."] == ""
        assert criteria[2].name in row[0]["Tag"]
        assert criteria[1].name in row[0]["Tag"]
        assert criteria[0].name not in row[0]["Tag"]
        assert criteria[3].name not in row[0]["Tag"]

        # offer should be reindexed
        mock_reindex_offer_ids.assert_called_once_with([offer_to_edit.id])


class GetEditOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_edit_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(3):  # session + user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class GetBatchEditOfferFormTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.get_batch_edit_offer_form"
    endpoint_kwargs = {"offer_ids": "1,2"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_get_empty_edit_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint, _external=True)

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

    def test_get_edit_form_with_values_test(self, legit_user, authenticated_client, criteria):
        offers = offers_factories.OfferFactory.create_batch(
            3, product__subcategoryId=subcategories.LIVRE_PAPIER.id, criteria=[criteria[2]], rankingWeight=22
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

        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303

        for offer in offers:
            assert offer.rankingWeight == chosen_ranking_weight
            assert len(offer.criteria) == 2
            assert criteria[0] in offer.criteria
            assert criteria[2] not in offer.criteria

        mock_async_index.assert_called_once_with([offer.id for offer in offers])


class ValidateOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.validate_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_validate_offer(self, legit_user, authenticated_client):
        offer_to_validate = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.REJECTED)

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_validate.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        offer_list_url = url_for("backoffice_web.offer.list_offers", q=offer_to_validate.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Validée"
        assert row[0]["Dernière validation"] == (datetime.date.today()).strftime("%d/%m/%Y")

        assert offer_to_validate.isActive is True
        assert offer_to_validate.lastValidationType == OfferValidationType.MANUAL


class GetValidateOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_validate_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_validate_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id)

        with assert_num_queries(3):  # session + user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class RejectOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.reject_offer"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_reject_offer(self, legit_user, authenticated_client):
        offer_to_reject = offers_factories.OfferFactory(validation=offers_models.OfferValidationStatus.APPROVED)

        response = self.post_to_endpoint(authenticated_client, offer_id=offer_to_reject.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offer.list_offers", _external=True)
        assert response.location == expected_url

        offer_list_url = url_for("backoffice_web.offer.list_offers", q=offer_to_reject.id, _external=True)
        response = authenticated_client.get(offer_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Rejetée"
        assert row[0]["Dernière validation"] == (datetime.date.today()).strftime("%d/%m/%Y")

        assert offer_to_reject.isActive is False
        assert offer_to_reject.lastValidationType == OfferValidationType.MANUAL


class GetRejectOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_reject_offer_form"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

        form_url = url_for(self.endpoint, offer_id=offer.id, _external=True)

        with assert_num_queries(3):  # session + user + tested_query
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class BatchOfferValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.batch_validate_offers"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_batch_validate_offers(self, legit_user, authenticated_client):
        offers = offers_factories.OfferFactory.create_batch(3, validation=offers_models.OfferValidationStatus.DRAFT)
        parameter_ids = ",".join(str(offer.id) for offer in offers)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303
        for offer in offers:
            db.session.refresh(offer)
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
            assert offer.isActive is True
            assert offer.lastValidationType is OfferValidationType.MANUAL
            assert offer.validation is offers_models.OfferValidationStatus.APPROVED
            assert offer.lastValidationAuthor == legit_user


class BatchOfferRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.batch_reject_offers"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_batch_reject_offers(self, legit_user, authenticated_client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offers = offers_factories.OfferFactory.create_batch(3, validation=offers_models.OfferValidationStatus.DRAFT)
        confirmed_booking = bookings_factories.BookingFactory(
            user=beneficiary, stock__offer=offers[0], status=BookingStatus.CONFIRMED
        )
        parameter_ids = ",".join(str(offer.id) for offer in offers)

        assert confirmed_booking.status == BookingStatus.CONFIRMED

        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert confirmed_booking.status == BookingStatus.CANCELLED
        assert response.status_code == 303
        for offer in offers:
            db.session.refresh(offer)
            assert offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
            assert offer.isActive is False
            assert offer.lastValidationType is OfferValidationType.MANUAL
            assert offer.validation is offers_models.OfferValidationStatus.REJECTED
            assert offer.lastValidationAuthor == legit_user


class GetOfferDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_offer_details"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + user + offer with joined data
    expected_num_queries = 3

    def test_get_detail_offer(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory()

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
        assert "Structure : Le Petit Rintintin Management" in card_text
        assert "Lieu : Le Petit Rintintin" in card_text
        assert "Utilisateur de la dernière validation" not in card_text
        assert "Date de dernière validation" not in card_text
        assert "Resynchroniser l'offre dans Algolia" in card_text

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
        offer = offers_factories.OfferFactory()

        expired_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=1), price=6.66
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
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
        offer = offers_factories.OfferFactory()

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

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
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
        offer = offers_factories.OfferFactory()

        stock = offers_factories.EventStockFactory(offer=offer, quantity=quantity, dnBookedQuantity=booked_quantity)

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["Stock ID"] == str(stock.id)
        assert stocks_rows[0]["Stock réservé"] == str(booked_quantity)
        assert stocks_rows[0]["Stock restant"] == expected_remaining
        assert stocks_rows[0]["Prix"] == "10,10 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    class IndexOfferButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT
        button_label = "Resynchroniser l'offre dans Algolia"

        @property
        def path(self):
            offer = offers_factories.OfferFactory()
            return url_for("backoffice_web.offer.get_offer_details", offer_id=offer.id)


class IndexOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.offer.reindex"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_index_offer(self, mocked_async_index_offer_ids, authenticated_client):
        offer = offers_factories.OfferFactory()

        response = self.post_to_endpoint(authenticated_client, offer_id=offer.id)
        assert response.status_code == 302

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "La resynchronisation de l'offre a été demandée." in html_parser.extract_alert(redirected_response.data)

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == {offer.id}
