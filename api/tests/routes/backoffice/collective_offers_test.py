from dataclasses import asdict
import datetime
from decimal import Decimal

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
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


@pytest.fixture(scope="function", name="collective_offers")
def collective_offers_fixture() -> tuple:
    collective_offer_1 = educational_factories.CollectiveStockFactory(
        startDatetime=datetime.date.today() + datetime.timedelta(days=1),
        endDatetime=datetime.date.today() + datetime.timedelta(days=1),
        collectiveOffer__author=users_factories.UserFactory(),
        collectiveOffer__institution=educational_factories.EducationalInstitutionFactory(),
        collectiveOffer__formats=[subcategories.EacFormat.ATELIER_DE_PRATIQUE],
        collectiveOffer__venue__postalCode="47000",
        collectiveOffer__venue__departementCode="47",
        price=10.1,
    ).collectiveOffer
    collective_offer_2 = educational_factories.CollectiveStockFactory(
        startDatetime=datetime.date.today() + datetime.timedelta(days=3),
        endDatetime=datetime.date.today() + datetime.timedelta(days=3),
        collectiveOffer__institution=collective_offer_1.institution,
        collectiveOffer__name="A Very Specific Name",
        collectiveOffer__formats=[subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
        collectiveOffer__venue__postalCode="97400",
        collectiveOffer__venue__departementCode="974",
        price=11,
    ).collectiveOffer
    collective_offer_3 = educational_factories.CollectiveStockFactory(
        startDatetime=datetime.date.today(),
        endDatetime=datetime.date.today(),
        collectiveOffer__dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        collectiveOffer__institution=educational_factories.EducationalInstitutionFactory(),
        collectiveOffer__name="A Very Specific Name That Is Longer",
        collectiveOffer__formats=[
            subcategories.EacFormat.FESTIVAL_SALON_CONGRES,
            subcategories.EacFormat.PROJECTION_AUDIOVISUELLE,
        ],
        collectiveOffer__validation=offers_models.OfferValidationStatus.REJECTED,
        collectiveOffer__venue__postalCode="74000",
        collectiveOffer__venue__departementCode="74",
        price=20,
    ).collectiveOffer
    return collective_offer_1, collective_offer_2, collective_offer_3


class ListCollectiveOffersTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.list_collective_offers"
    needed_permission = perm_models.Permissions.READ_OFFERS

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch collective offers with joinedload including extra data (1 query)
    expected_num_queries = 3

    def _get_query_args_by_id(self, id_: int) -> dict[str, str]:
        return {
            "search-0-search_field": "ID",
            "search-0-operator": "IN",
            "search-0-string": str(id_),
        }

    def test_list_collective_offers_without_filter(self, authenticated_client, collective_offers):
        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    def test_list_collective_offers_by_id(self, authenticated_client, collective_offers):
        query_args = self._get_query_args_by_id(collective_offers[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(collective_offers[0].id)
        assert rows[0]["Nom de l'offre"] == collective_offers[0].name
        assert rows[0]["Créateur de l'offre"] == collective_offers[0].author.full_name
        assert rows[0]["Formats"] == ", ".join([fmt.value for fmt in collective_offers[0].formats])
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today() - datetime.timedelta(days=5)).strftime("%d/%m/%Y")
        assert rows[0]["Date de l'évènement"] == (datetime.date.today() + datetime.timedelta(days=1)).strftime(
            "%d/%m/%Y"
        )
        assert rows[0]["Tarif"] == "10,10 €"
        assert rows[0]["Formats"] == ", ".join([fmt.value for fmt in collective_offers[0].formats])
        assert rows[0]["Structure"] == collective_offers[0].venue.managingOfferer.name
        assert rows[0]["Lieu"] == collective_offers[0].venue.name

    def test_list_collective_offers_without_fraud_permission(
        self,
        client,
        read_only_bo_user,
        collective_offers,
    ):
        user = offerers_factories.UserOffererFactory().user

        response = client.with_bo_session_auth(read_only_bo_user).get(
            url_for(self.endpoint, user_id=user.id, **self._get_query_args_by_id(collective_offers[0].id))
        )
        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert "Tarif" not in rows[0]
        assert "Règles de conformité" not in rows[0]

    def test_list_collective_offers_by_name(self, authenticated_client, collective_offers):
        query_args = {
            "search-0-search_field": "NAME",
            "search-0-operator": "CONTAINS",
            "search-0-string": collective_offers[1].name,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        rows = sorted(rows, key=lambda row: row["Nom de l'offre"])
        assert len(rows) == 2
        assert rows[0]["ID"] == str(collective_offers[1].id)
        assert rows[0]["Nom de l'offre"] == collective_offers[1].name
        assert rows[0]["Formats"] == ", ".join([fmt.value for fmt in collective_offers[1].formats])
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today() - datetime.timedelta(days=5)).strftime("%d/%m/%Y")
        assert rows[0]["Date de l'évènement"] == (datetime.date.today() + datetime.timedelta(days=3)).strftime(
            "%d/%m/%Y"
        )
        assert rows[0]["Tarif"] == "11,00 €"
        assert rows[0]["Structure"] == collective_offers[1].venue.managingOfferer.name
        assert rows[0]["Lieu"] == collective_offers[1].venue.name

    def test_list_collective_offers_by_several_filters(self, authenticated_client, collective_offers):
        collective_offer = collective_offers[2]

        query_args = {
            "search-0-search_field": "NAME",
            "search-0-operator": "CONTAINS",
            "search-0-string": "specific name",
            "search-1-search_field": "FORMATS",
            "search-1-operator": "INTERSECTS",
            "search-1-formats": collective_offer.formats[0].name,
            "search-2-search_field": "VENUE",
            "search-2-operator": "IN",
            "search-2-venue": collective_offer.venueId,
        }

        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[2].id}

    def test_list_collective_offers_by_creation_date(self, authenticated_client, collective_offers):
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
        assert set(int(row["ID"]) for row in rows) == {collective_offers[2].id}

    def test_list_collective_offers_by_status_and_event_date(self, authenticated_client, collective_offers):
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
        assert set(int(row["ID"]) for row in rows) == {collective_offers[0].id}

    def test_list_collective_offers_without_sort_should_not_have_created_date_sort_link(
        self, authenticated_client, collective_offers
    ):
        query_args = self._get_query_args_by_id(collective_offers[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        assert "sort=dateCreated&amp;order=desc" not in str(response.data)

    def test_list_collective_offers_with_sort_should_have_created_date_sort_link(
        self, authenticated_client, collective_offers
    ):
        query_args = self._get_query_args_by_id(collective_offers[0].id) | {
            "sort": "dateCreated",
            "order": "asc",
            "q": "e",
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        assert "sort=dateCreated&amp;order=desc" in str(response.data)

    def test_list_collective_offers_with_and_sort_should_have_created_date_sort_link(
        self, authenticated_client, collective_offers
    ):
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
            "/pro/collective-offer?sort=dateCreated&amp;order=desc&amp;search-0-search_field=NAME&amp;"
            "search-0-operator=NAME_EQUALS&amp;search-0-string=A+Very+Specific+Name"
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
    def test_list_collective_offers_with_booking_limit_date_filter(
        self, authenticated_client, operator, valid_date, not_valid_date
    ):
        should_be_displayed_offer = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=valid_date
        ).collectiveOffer
        educational_factories.CollectiveStockFactory(bookingLimitDatetime=not_valid_date)

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

    def test_list_collective_offers_by_event_date(self, authenticated_client):
        educational_factories.CollectiveStockFactory(
            startDatetime=datetime.date.today() + datetime.timedelta(days=1),
            endDatetime=datetime.date.today() + datetime.timedelta(days=1),
        )
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime.date.today(), endDatetime=datetime.date.today()
        )
        educational_factories.CollectiveStockFactory(
            startDatetime=datetime.date.today() - datetime.timedelta(days=1),
            endDatetime=datetime.date.today() - datetime.timedelta(days=1),
        )

        query_args = {
            "search-2-search_field": "EVENT_DATE",
            "search-2-operator": "DATE_EQUALS",
            "search-2-date": datetime.date.today().isoformat(),
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {stock.collectiveOffer.id}

    def test_list_collective_offers_by_event_date_gte_only(self, authenticated_client, collective_offers):
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
        assert set(int(row["ID"]) for row in rows) == {collective_offers[1].id}

    @pytest.mark.parametrize(
        "operator,formats,expected_offer_indexes",
        [
            ("INTERSECTS", [subcategories.EacFormat.ATELIER_DE_PRATIQUE], [0]),
            (
                "INTERSECTS",
                [subcategories.EacFormat.ATELIER_DE_PRATIQUE, subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
                [0, 1, 2],
            ),
            (
                "INTERSECTS",
                [subcategories.EacFormat.FESTIVAL_SALON_CONGRES, subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
                [1, 2],
            ),
            ("NOT_INTERSECTS", [subcategories.EacFormat.PROJECTION_AUDIOVISUELLE], [0]),
            (
                "NOT_INTERSECTS",
                [subcategories.EacFormat.ATELIER_DE_PRATIQUE, subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
                [],
            ),
        ],
    )
    def test_list_collective_offers_by_formats(
        self, authenticated_client, collective_offers, operator, formats, expected_offer_indexes
    ):
        query_args = {
            "search-3-search_field": "FORMATS",
            "search-3-operator": operator,
            "search-3-formats": [format.name for format in formats],
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[index].id for index in expected_offer_indexes}

    def test_list_collective_offers_by_price(self, authenticated_client, collective_offers):

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
        assert rows[0]["ID"] == str(collective_offers[2].id)

    def test_list_collective_offers_by_price_no_offer_found(self, authenticated_client, collective_offers):

        query_args = {
            "search-3-search_field": "PRICE",
            "search-3-operator": "GREATER_THAN_OR_EQUAL_TO",
            "search-3-price": 21.20,
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 0

    def test_list_offers_by_in_and_not_in_formats(self, authenticated_client, collective_offers):
        query_args = {
            "search-0-search_field": "FORMATS",
            "search-0-operator": "INTERSECTS",
            "search-0-formats": [subcategories.EacFormat.PROJECTION_AUDIOVISUELLE.name],
            "search-2-search_field": "FORMATS",
            "search-2-operator": "NOT_INTERSECTS",
            "search-2-formats": [subcategories.EacFormat.FESTIVAL_SALON_CONGRES.name],
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[1].id}

    def test_list_offers_by_institution(self, authenticated_client, collective_offers):
        institution_id = collective_offers[0].institutionId
        query_args = {
            "search-3-search_field": "INSTITUTION",
            "search-3-operator": "IN",
            "search-3-institution": institution_id,
        }
        with assert_num_queries(
            self.expected_num_queries + 1
        ):  # +1 because of reloading selected institution in the form
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[0].id, collective_offers[1].id}

    def test_list_collective_offers_by_department(self, authenticated_client, collective_offers):
        query_args = {
            "search-3-search_field": "DEPARTMENT",
            "search-3-operator": "IN",
            "search-3-department": ["74", "47", "971"],
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[0].id, collective_offers[2].id}

    def test_list_collective_offers_by_region(self, authenticated_client, collective_offers):
        query_args = {
            "search-0-search_field": "REGION",
            "search-0-operator": "IN",
            "search-0-region": ["La Réunion", "Auvergne-Rhône-Alpes"],
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {int(row["ID"]) for row in rows} == {collective_offers[1].id, collective_offers[2].id}

    def test_list_collective_offers_by_venue(self, authenticated_client, collective_offers):
        venue_id = collective_offers[1].venueId
        query_args = {
            "search-3-search_field": "VENUE",
            "search-3-operator": "IN",
            "search-3-venue": venue_id,
        }
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue in the form
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[1].id}

    def test_list_collective_offers_by_status(self, authenticated_client, collective_offers):
        offer = educational_factories.CollectiveOfferFactory(isActive=False)

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
        assert rows[0]["État"] == "Validée"

    def test_list_collective_offers_by_offerer(self, authenticated_client, collective_offers):
        offerer_id = collective_offers[1].venue.managingOffererId
        query_args = {
            "search-3-search_field": "OFFERER",
            "search-3-operator": "IN",
            "search-3-offerer": offerer_id,
        }
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected offerer in the form
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[1].id}

    def test_list_collective_offers_by_validation(self, authenticated_client, collective_offers):
        status = collective_offers[2].validation
        query_args = {
            "search-3-search_field": "VALIDATION",
            "search-3-operator": "IN",
            "search-3-validation": status.value,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offers[2].id}
        assert rows[0]["État"] == "Rejetée"

    def test_list_collective_offers_by_four_filters(self, authenticated_client, collective_offers):
        venue_id = collective_offers[2].venueId

        query_args = {
            "search-0-search_field": "INSTITUTION",
            "search-0-operator": "NOT_IN",
            "search-0-institution": collective_offers[0].institutionId,
            "search-1-search_field": "FORMATS",
            "search-1-operator": "INTERSECTS",
            "search-1-formats": [subcategories.EacFormat.PROJECTION_AUDIOVISUELLE.name],
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
        assert set(int(row["ID"]) for row in rows) == {collective_offers[2].id}

    @pytest.mark.parametrize(
        "order,expected_list",
        [
            ("", ["Offre collective 4", "Offre collective 3", "Offre collective 2", "Offre collective 1"]),
            ("asc", ["Offre collective 4", "Offre collective 3", "Offre collective 2", "Offre collective 1"]),
            ("desc", ["Offre collective 1", "Offre collective 2", "Offre collective 3", "Offre collective 4"]),
        ],
    )
    def test_list_collective_offers_pending_from_validated_offerers_sorted_by_date(
        self, authenticated_client, order, expected_list
    ):
        # test results when clicking on pending offers link (home page)
        educational_factories.CollectiveOfferFactory(
            validation=offers_models.OfferValidationStatus.PENDING,
            venue__managingOfferer=offerers_factories.NotValidatedOffererFactory(),
        )

        validated_venue = offerers_factories.VenueFactory()
        for days_ago in (2, 4, 1, 3):
            educational_factories.CollectiveOfferFactory(
                name=f"Offre collective {days_ago}",
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
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        # must be sorted, older first
        rows = html_parser.extract_table_rows(response.data)
        assert [row["Nom de l'offre"] for row in rows] == expected_list

    def test_list_collective_offers_with_flagging_rules(self, authenticated_client):
        rule_1 = offers_factories.OfferValidationRuleFactory(name="Règle magique")
        rule_2 = offers_factories.OfferValidationRuleFactory(name="Règle moldue")
        educational_factories.CollectiveOfferFactory(
            validation=offers_models.OfferValidationStatus.PENDING, flaggingValidationRules=[rule_1, rule_2]
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

    # === Error cases ===

    def test_list_offers_by_invalid_field(self, authenticated_client, collective_offers):
        query_args = {
            "search-0-search_field": "FARMOTS",
            "search-0-operator": "INTERSECTS",
            "search-0-formats": [subcategories.EacFormat.PROJECTION_AUDIOVISUELLE.name],
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert html_parser.extract_alert(response.data) == "Le filtre FARMOTS est invalide."

    def test_list_offers_by_formats_and_missing_date(self, authenticated_client, collective_offers):
        query_args = {
            "search-0-search_field": "FORMATS",
            "search-0-operator": "INTERSECTS",
            "search-0-formats": [subcategories.EacFormat.PROJECTION_AUDIOVISUELLE.name],
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

    def test_list_offers_by_invalid_format(self, authenticated_client):
        query_args = {
            "search-0-search_field": "ID",
            "search-0-operator": "EQUALS",
            "search-0-string": "12, 34, A",
        }
        with assert_num_queries(2):  # only session + current user, before form validation
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

    def test_list_offers_with_offerer_confidence_rule(self, client, pro_fraud_admin):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer__name="Offerer")
        collective_offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=rule.offerer, venue__name="Venue"
        )

        client = client.with_bo_session_auth(pro_fraud_admin)
        query_args = self._get_query_args_by_id(collective_offer.id)
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
        collective_offer = educational_factories.CollectiveOfferFactory(venue=rule.venue)

        client = client.with_bo_session_auth(pro_fraud_admin)
        query_args = self._get_query_args_by_id(collective_offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Structure"] == "Offerer"
        assert rows[0]["Lieu"] == "Venue Revue manuelle"


class ValidateCollectiveOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer.validate_collective_offer"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_validate_collective_offer(self, legit_user, authenticated_client):
        collective_offer_to_validate = educational_factories.CollectiveOfferFactory(
            validation=OfferValidationStatus.PENDING
        )

        response = self.post_to_endpoint(authenticated_client, collective_offer_id=collective_offer_to_validate.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.collective_offer.list_collective_offers", _external=True)
        assert response.location == expected_url

        collective_offer_list_url = url_for(
            "backoffice_web.collective_offer.list_collective_offers",
            q=collective_offer_to_validate.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_list_url)
        assert response.status_code == 200

        assert collective_offer_to_validate.isActive is True
        assert collective_offer_to_validate.validation == OfferValidationStatus.APPROVED
        assert collective_offer_to_validate.lastValidationType == OfferValidationType.MANUAL

    def test_cant_validate_non_pending_offer(self, legit_user, authenticated_client):
        collective_offer_to_validate = educational_factories.CollectiveOfferFactory(
            validation=OfferValidationStatus.REJECTED
        )

        response = self.post_to_endpoint(authenticated_client, collective_offer_id=collective_offer_to_validate.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.collective_offer.list_collective_offers", _external=True)
        assert response.location == expected_url

        collective_offer_list_url = url_for(
            "backoffice_web.collective_offer.list_collective_offers",
            q=collective_offer_to_validate.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_list_url)

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data) == "Seules les offres collectives en attente peuvent être validées"
        )
        db.session.refresh(collective_offer_to_validate)
        assert collective_offer_to_validate.validation == OfferValidationStatus.REJECTED


class ValidateCollectiveOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_validate_collective_offer_form"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_validate_form_test(self, legit_user, authenticated_client):
        collective_offer = educational_factories.CollectiveOfferFactory()

        form_url = url_for(self.endpoint, collective_offer_id=collective_offer.id)

        with assert_num_queries(3):  # session + current user + collective offer
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class RejectCollectiveOfferTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer.reject_collective_offer"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_reject_collective_offer(self, legit_user, authenticated_client):
        collective_offer_to_reject = educational_factories.CollectiveOfferFactory(
            validation=OfferValidationStatus.PENDING
        )

        response = self.post_to_endpoint(authenticated_client, collective_offer_id=collective_offer_to_reject.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.collective_offer.list_collective_offers", _external=True)
        assert response.location == expected_url

        collective_offer_list_url = url_for(
            "backoffice_web.collective_offer.list_collective_offers", q=collective_offer_to_reject.id, _external=True
        )
        response = authenticated_client.get(collective_offer_list_url)

        assert response.status_code == 200

        assert collective_offer_to_reject.isActive is False
        assert collective_offer_to_reject.validation == OfferValidationStatus.REJECTED
        assert collective_offer_to_reject.lastValidationType == OfferValidationType.MANUAL

    def test_cant_reject_non_pending_offer(self, legit_user, authenticated_client):
        collective_offer_to_reject = educational_factories.CollectiveOfferFactory(
            validation=OfferValidationStatus.APPROVED
        )

        response = self.post_to_endpoint(authenticated_client, collective_offer_id=collective_offer_to_reject.id)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.collective_offer.list_collective_offers", _external=True)
        assert response.location == expected_url

        collective_offer_list_url = url_for(
            "backoffice_web.collective_offer.list_collective_offers", q=collective_offer_to_reject.id, _external=True
        )
        response = authenticated_client.get(collective_offer_list_url)

        assert response.status_code == 200
        assert (
            html_parser.extract_alert(response.data) == "Seules les offres collectives en attente peuvent être rejetées"
        )
        db.session.refresh(collective_offer_to_reject)
        assert collective_offer_to_reject.validation == OfferValidationStatus.APPROVED


class RejectCollectiveOfferFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_reject_collective_offer_form"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_reject_form_test(self, legit_user, authenticated_client):
        collective_offer = educational_factories.CollectiveOfferFactory()

        form_url = url_for(self.endpoint, collective_offer_id=collective_offer.id)

        with assert_num_queries(3):  # session + current user + collective_offer
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class BatchCollectiveOffersValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer.batch_validate_collective_offers"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_batch_validate_collective_offers(self, legit_user, authenticated_client):
        collective_offers = educational_factories.CollectiveOfferFactory.create_batch(
            3, validation=OfferValidationStatus.PENDING
        )
        parameter_ids = ",".join(str(collective_offer.id) for collective_offer in collective_offers)
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.collective_offer.list_collective_offers", _external=True)
        assert response.location == expected_url

        for collective_offer in collective_offers:
            db.session.refresh(collective_offer)
            assert collective_offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime(
                "%d/%m/%Y"
            )
            assert collective_offer.isActive is True
            assert collective_offer.lastValidationType is OfferValidationType.MANUAL
            assert collective_offer.validation is OfferValidationStatus.APPROVED

        assert len(mails_testing.outbox) == 3

        received_dict = {email["To"]: email["template"] for email in mails_testing.outbox}
        expected_dict = {
            collective_offers[0].venue.bookingEmail: asdict(TransactionalEmail.OFFER_APPROVAL_TO_PRO.value),
            collective_offers[1].venue.bookingEmail: asdict(TransactionalEmail.OFFER_APPROVAL_TO_PRO.value),
            collective_offers[2].venue.bookingEmail: asdict(TransactionalEmail.OFFER_APPROVAL_TO_PRO.value),
        }
        assert received_dict == expected_dict

    def test_batch_validate_collective_offers_wrong_id(self, legit_user, authenticated_client):
        fake_offer_ids = [123, 456]
        collective_offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        parameter_ids = f"{str(fake_offer_ids[0])}, {str(fake_offer_ids[1])}, {collective_offer}"
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303
        assert collective_offer.validation == OfferValidationStatus.PENDING
        collective_offer_template = educational_models.CollectiveOffer.query.filter_by(id=collective_offer.id).one()
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        non_existing_collective_offers = educational_models.CollectiveOffer.query.filter(
            educational_models.CollectiveOffer.id.in_(fake_offer_ids)
        ).all()
        assert len(non_existing_collective_offers) == 0


class BatchCollectiveOffersRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer.batch_reject_collective_offers"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_batch_reject_offers(self, legit_user, authenticated_client):
        collective_offers = educational_factories.CollectiveOfferFactory.create_batch(
            3, validation=OfferValidationStatus.PENDING
        )
        parameter_ids = ",".join(str(collective_offer.id) for collective_offer in collective_offers)

        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.collective_offer.list_collective_offers", _external=True)
        assert response.location == expected_url

        for collective_offer in collective_offers:
            db.session.refresh(collective_offer)
            assert collective_offer.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime(
                "%d/%m/%Y"
            )
            assert collective_offer.isActive is False
            assert collective_offer.lastValidationType is OfferValidationType.MANUAL
            assert collective_offer.validation is OfferValidationStatus.REJECTED
            assert collective_offer.lastValidationAuthor == legit_user

        assert len(mails_testing.outbox) == 3

        received_dict = {email["To"]: email["template"] for email in mails_testing.outbox}
        expected_dict = {
            collective_offers[0].venue.bookingEmail: asdict(TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value),
            collective_offers[1].venue.bookingEmail: asdict(TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value),
            collective_offers[2].venue.bookingEmail: asdict(TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value),
        }
        assert received_dict == expected_dict

    def test_batch_reject_collective_offers_wrong_id(self, legit_user, authenticated_client):
        fake_offer_ids = [123, 456]
        collective_offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        parameter_ids = f"{str(fake_offer_ids[0])}, {str(fake_offer_ids[1])}, {collective_offer}"
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303
        assert collective_offer.validation == OfferValidationStatus.PENDING
        collective_offer_template = educational_models.CollectiveOffer.query.filter_by(id=collective_offer.id).one()
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        non_existing_collective_offers = educational_models.CollectiveOffer.query.filter(
            educational_models.CollectiveOffer.id.in_(fake_offer_ids)
        ).all()
        assert len(non_existing_collective_offers) == 0


class GetBatchCollectiveOffersApproveFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_batch_validate_collective_offers_form"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_batch_collective_offers_approve_form(self, legit_user, authenticated_client):
        url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url)
            assert response.status_code == 200


class GetBatchCollectiveOffersRejectFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_batch_reject_collective_offers_form"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_batch_collective_offers_reject_form(self, legit_user, authenticated_client):
        url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url)
            assert response.status_code == 200


class GetCollectiveOfferDetailTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS
    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch CollectiveOffer
    # - _is_collective_offer_price_editable
    expected_num_queries = 4

    def test_nominal(self, legit_user, authenticated_client):
        event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=event_date,
            collectiveStock__endDatetime=event_date,
            collectiveStock__collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(
                firstName="Pacôme", lastName="De Champignac"
            ),
            collectiveStock__collectiveOffer__institution=educational_factories.EducationalInstitutionFactory(
                name="Ecole de Marcinelle"
            ),
            collectiveStock__collectiveOffer__template=educational_factories.CollectiveOfferTemplateFactory(
                name="offre Vito Cortizone pour lieu que l'on ne peut refuser"
            ),
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content_as_text = html_parser.content_as_text(response.data)
        assert "Ajuster le prix de l'offre" in content_as_text
        assert "Statut : Expirée" in content_as_text
        assert "État : Validée" in content_as_text
        assert "Utilisateur de la dernière validation" not in content_as_text
        assert "Date de dernière validation de l’offre" not in content_as_text
        assert "Enseignant : Pacôme De Champignac" in content_as_text
        assert "Établissement : Ecole de Marcinelle" in content_as_text
        assert "Offre vitrine liée : offre Vito Cortizone pour lieu que l'on ne peut refuser" in content_as_text

    def test_processed_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.PROCESSED,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
            collectiveBooking__collectiveStock__endDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Ajuster le prix de l'offre" not in response.data.decode()

    def test_invoiced_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.INVOICED,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
            collectiveBooking__collectiveStock__endDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Ajuster le prix de l'offre" not in response.data.decode()

    def test_cashflow_pending(self, legit_user, authenticated_client, app):
        pricing = finance_factories.CollectivePricingFactory(
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
            collectiveBooking__collectiveStock__endDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)
        app.redis_client.set(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK, "1", 600)
        try:
            with assert_num_queries(3):
                response = authenticated_client.get(url)
                assert response.status_code == 200
        finally:
            app.redis_client.delete(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK)

        assert "Ajuster le prix de l'offre" not in response.data.decode()

    def test_get_validated_offer(self, legit_user, authenticated_client):
        event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        validation_date = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=event_date,
            collectiveStock__endDatetime=event_date,
            collectiveStock__collectiveOffer__lastValidationDate=validation_date,
            collectiveStock__collectiveOffer__validation=offers_models.OfferValidationStatus.APPROVED,
            collectiveStock__collectiveOffer__lastValidationAuthor=legit_user,
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        content_as_text = html_parser.content_as_text(response.data)
        assert response.status_code == 200
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in content_as_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in content_as_text

    def test_get_rejected_offer(self, legit_user, authenticated_client):
        event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        validation_date = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=event_date,
            collectiveStock__endDatetime=event_date,
            collectiveStock__collectiveOffer__lastValidationDate=validation_date,
            collectiveStock__collectiveOffer__validation=offers_models.OfferValidationStatus.REJECTED,
            collectiveStock__collectiveOffer__lastValidationAuthor=legit_user,
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content_as_text = html_parser.content_as_text(response.data)
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in content_as_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in content_as_text


class ValidateCollectiveOfferFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Valider l'offre"
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"

    @property
    def path(self):
        stock = educational_factories.CollectiveStockFactory()
        return url_for(self.endpoint, collective_offer_id=stock.collectiveOffer.id)


class RejectCollectiveOfferFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Rejeter l'offre"
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"

    @property
    def path(self):
        stock = educational_factories.CollectiveStockFactory()
        return url_for(self.endpoint, collective_offer_id=stock.collectiveOffer.id)


class GetCollectiveOfferPriceFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_collective_offer_price_form"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    # session + current user + offer + stock
    expected_num_queries = 4

    def test_get_collective_offer_price_form(self, legit_user, authenticated_client):
        collective_offer_id = educational_factories.CollectiveStockFactory().collectiveOfferId

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, collective_offer_id=collective_offer_id))
            assert response.status_code == 200


class PostEditCollectiveOfferPriceTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer.edit_collective_offer_price"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.ADVANCED_PRO_SUPPORT

    def test_nominal(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        date_used = datetime.datetime.utcnow() - datetime.timedelta(hours=72)
        collective_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(100.00),
            collectiveStock__numberOfTickets=25,
            collectiveStock__startDatetime=date_used,
            collectiveStock__endDatetime=date_used,
            venue=venue,
            dateUsed=date_used,
        )
        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED,
            booking=collective_booking,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={"numberOfTickets": 5, "price": 1},
            collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id,
        )

        assert response.status_code == 303
        assert collective_booking.collectiveStock.price == 1
        assert collective_booking.collectiveStock.numberOfTickets == 5
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'offre collective a été mise à jour"
        )

    def test_processed_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.PROCESSED,
            collectiveBooking__collectiveStock__price=Decimal(100.00),
            collectiveBooking__collectiveStock__numberOfTickets=25,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
            collectiveBooking__collectiveStock__endDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)
        authenticated_client.get(url)

        response = self.post_to_endpoint(
            authenticated_client,
            form={"numberOfTickets": 5, "price": 1},
            collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id,
        )

        assert response.status_code == 303
        assert pricing.collectiveBooking.collectiveStock.price == 100
        assert pricing.collectiveBooking.collectiveStock.numberOfTickets == 25
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Cette offre n'est pas modifiable"
        )

    def test_invoiced_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.INVOICED,
            collectiveBooking__collectiveStock__price=Decimal(100.00),
            collectiveBooking__collectiveStock__numberOfTickets=25,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
            collectiveBooking__collectiveStock__endDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)
        authenticated_client.get(url)

        response = self.post_to_endpoint(
            authenticated_client,
            form={"numberOfTickets": 5, "price": 1},
            collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id,
        )

        assert response.status_code == 303
        assert pricing.collectiveBooking.collectiveStock.price == 100
        assert pricing.collectiveBooking.collectiveStock.numberOfTickets == 25
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Cette offre n'est pas modifiable"
        )

    @pytest.mark.parametrize(
        "pricing_status",
        [
            finance_models.PricingStatus.CANCELLED,
            finance_models.PricingStatus.VALIDATED,
            finance_models.PricingStatus.PENDING,
            finance_models.PricingStatus.REJECTED,
        ],
    )
    def test_unprocessed_pricing(self, legit_user, authenticated_client, pricing_status):
        # when
        pricing = finance_factories.CollectivePricingFactory(
            status=pricing_status,
            collectiveBooking__collectiveStock__price=Decimal(100.00),
            collectiveBooking__collectiveStock__numberOfTickets=25,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
            collectiveBooking__collectiveStock__endDatetime=datetime.datetime(1970, 1, 1),
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={"numberOfTickets": 5, "price": 1},
            collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id,
        )

        # then
        assert response.status_code == 303
        assert pricing.collectiveBooking.collectiveStock.price == 1
        assert pricing.collectiveBooking.collectiveStock.numberOfTickets == 5
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'offre collective a été mise à jour"
        )

    def test_cashflow_pending(self, legit_user, authenticated_client, app):
        event_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__price=Decimal(100.00),
            collectiveStock__numberOfTickets=25,
            collectiveStock__startDatetime=event_date,
            collectiveStock__endDatetime=event_date,
        )
        app.redis_client.set(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK, "1", 600)
        try:
            response = self.post_to_endpoint(
                authenticated_client,
                form={"numberOfTickets": 5, "price": 1},
                collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id,
            )
        finally:
            app.redis_client.delete(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK)

        assert response.status_code == 303
        assert collective_booking.collectiveStock.price == 100
        assert collective_booking.collectiveStock.numberOfTickets == 25
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Cette offre n'est pas modifiable"
        )

    @pytest.mark.parametrize(
        "booking_status",
        [
            educational_models.CollectiveBookingStatus.CANCELLED,
            educational_models.CollectiveBookingStatus.PENDING,
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.USED,
        ],
    )
    def test_price_higher_than_previously(self, legit_user, authenticated_client, booking_status):
        now = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__price=Decimal(100.00),
            collectiveStock__numberOfTickets=25,
            collectiveStock__startDatetime=now,
            collectiveStock__endDatetime=now,
            status=booking_status,
            dateUsed=now,
            confirmationDate=now,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            form={"numberOfTickets": 5, "price": 200},
            collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id,
        )

        if booking_status in [
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.USED,
        ]:
            assert response.status_code == 303
            assert collective_booking.collectiveStock.price == 100
            assert collective_booking.collectiveStock.numberOfTickets == 25
            assert (
                html_parser.extract_alert(authenticated_client.get(response.location).data)
                == "Impossible d'augmenter le prix d'une offre confirmée"
            )
        else:
            assert response.status_code == 303
            assert collective_booking.collectiveStock.price == 200
            assert collective_booking.collectiveStock.numberOfTickets == 5

    @pytest.mark.parametrize(
        "booking_status",
        [
            educational_models.CollectiveBookingStatus.CANCELLED,
            educational_models.CollectiveBookingStatus.PENDING,
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.USED,
        ],
    )
    def test_number_of_tickets_higher_than_previously(self, legit_user, authenticated_client, booking_status):
        now = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__price=Decimal(100.00),
            collectiveStock__numberOfTickets=25,
            collectiveStock__startDatetime=now,
            collectiveStock__endDatetime=now,
            status=booking_status,
            dateUsed=now,
            confirmationDate=now,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            form={"numberOfTickets": 50, "price": 1},
            collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id,
        )

        if booking_status in [
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.USED,
        ]:
            assert response.status_code == 303
            assert collective_booking.collectiveStock.price == 100
            assert collective_booking.collectiveStock.numberOfTickets == 25
            assert (
                html_parser.extract_alert(authenticated_client.get(response.location).data)
                == "Impossible d'augmenter le nombre de participants d'une offre confirmée"
            )
        else:
            assert response.status_code == 303
            assert collective_booking.collectiveStock.price == 1
            assert collective_booking.collectiveStock.numberOfTickets == 50
