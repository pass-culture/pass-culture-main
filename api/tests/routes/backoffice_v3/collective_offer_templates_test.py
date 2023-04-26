import datetime

from flask import g
from flask import url_for
import pytest

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="collective_offer_templates")
def collective_offer_templates_fixture() -> tuple:
    collective_offer_template_1 = educational_factories.CollectiveOfferTemplateFactory(
        subcategoryId=subcategories.ATELIER_PRATIQUE_ART.id,
    )
    collective_offer_template_2 = educational_factories.CollectiveOfferTemplateFactory(
        name="A Very Specific Name",
        subcategoryId=subcategories.EVENEMENT_CINE.id,
    )
    collective_offer_template_3 = educational_factories.CollectiveOfferTemplateFactory(
        name="A Very Specific Name That Is Longer",
        dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        validation=offers_models.OfferValidationStatus.REJECTED,
        subcategoryId=subcategories.FESTIVAL_CINE.id,
    )
    return collective_offer_template_1, collective_offer_template_2, collective_offer_template_3


class ListCollectiveOfferTemplatesTest:
    endpoint = "backoffice_v3_web.collective_offer_template.list_collective_offer_templates"

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch collective offer templates with joinedload including extra data (1 query)
    expected_num_queries = 3

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.collective_offer_template.list_collective_offer_templates"
        needed_permission = perm_models.Permissions.READ_OFFERS

    def test_list_collective_offer_templates_without_filter(self, authenticated_client, collective_offer_templates):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_collective_offer_templates_by_id(self, authenticated_client, collective_offer_templates):
        # when
        searched_id = str(collective_offer_templates[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == searched_id
        assert rows[0]["Nom de l'offre"] == collective_offer_templates[0].name
        assert rows[0]["Catégorie"] == collective_offer_templates[0].subcategory.category.pro_label
        assert rows[0]["Sous-catégorie"] == collective_offer_templates[0].subcategory.pro_label
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today() - datetime.timedelta(days=5)).strftime("%d/%m/%Y")
        assert rows[0]["Structure"] == collective_offer_templates[0].venue.managingOfferer.name
        assert rows[0]["Lieu"] == collective_offer_templates[0].venue.name

    def test_list_collective_offer_templates_by_name(self, authenticated_client, collective_offer_templates):
        # when
        searched_name = collective_offer_templates[1].name
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_name, sort="id", order="asc"))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["ID"] == str(collective_offer_templates[1].id)
        assert rows[0]["Nom de l'offre"] == collective_offer_templates[1].name
        assert rows[0]["Catégorie"] == collective_offer_templates[1].subcategory.category.pro_label
        assert rows[0]["Sous-catégorie"] == collective_offer_templates[1].subcategory.pro_label
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today() - datetime.timedelta(days=5)).strftime("%d/%m/%Y")
        assert rows[0]["Structure"] == collective_offer_templates[1].venue.managingOfferer.name
        assert rows[0]["Lieu"] == collective_offer_templates[1].venue.name

    def test_list_offers_by_date(self, authenticated_client, collective_offer_templates):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_date=(datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
                    to_date=(datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[2].id}

    def test_list_collective_offer_templates_by_category(self, authenticated_client, collective_offer_templates):
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, category=[categories.CINEMA.id]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {
            collective_offer_templates[1].id,
            collective_offer_templates[2].id,
        }

    def test_list_collective_offer_templates_by_venue(self, authenticated_client, collective_offer_templates):
        # when
        venue_id = collective_offer_templates[1].venueId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue in the form
            response = authenticated_client.get(url_for(self.endpoint, venue=[venue_id]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[1].id}

    def test_list_collective_offer_templates_by_offerer(self, authenticated_client, collective_offer_templates):
        # when
        offerer_id = collective_offer_templates[1].venue.managingOffererId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected offerer in the form
            response = authenticated_client.get(url_for(self.endpoint, offerer=[offerer_id]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[1].id}

    def test_list_collective_offer_templates_by_status(self, authenticated_client, collective_offer_templates):
        # when
        status = collective_offer_templates[2].validation
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=[status.value]))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[2].id}
        assert rows[0]["État"] == "Rejetée"

    def test_list_offers_by_all_filters(self, authenticated_client, collective_offer_templates):
        # when
        venue_id = collective_offer_templates[2].venueId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="specific name",
                    category=[categories.CINEMA.id],
                    venue=[venue_id],
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[2].id}

    def test_list_offers_pending_from_validated_offerers_sorted_by_date(self, authenticated_client):
        # test results when clicking on pending collective offers link (home page)
        # given
        educational_factories.CollectiveOfferTemplateFactory(
            validation=offers_models.OfferValidationStatus.PENDING,
            venue__managingOfferer=offerers_factories.NotValidatedOffererFactory(),
        )

        validated_venue = offerers_factories.VenueFactory()
        for days_ago in (2, 4, 1, 3):
            educational_factories.CollectiveOfferTemplateFactory(
                name=f"Offre {days_ago}",
                dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=days_ago),
                validation=offers_models.OfferValidationStatus.PENDING,
                venue=validated_venue,
            )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    status=[offers_models.OfferValidationStatus.PENDING.value],
                    only_validated_offerers="on",
                    sort="dateCreated",
                )
            )
            assert response.status_code == 200

        # then: must be sorted, older first
        rows = html_parser.extract_table_rows(response.data)
        assert [row["Nom de l'offre"] for row in rows] == ["Offre 4", "Offre 3", "Offre 2", "Offre 1"]


class ValidateCollectiveOfferTemplateTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.collective_offer_template.validate_collective_offer_template"
        endpoint_kwargs = {"collective_offer_template_id": 1}
        needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_validate_collective_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_validate = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )
        base_form = {}

        response = self._validate_collective_offer(
            authenticated_client, collective_offer_template_to_validate, base_form
        )
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_template_list_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates",
            q=collective_offer_template_to_validate.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_template_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Validée"

        assert collective_offer_template_to_validate.isActive is True
        assert collective_offer_template_to_validate.lastValidationType == OfferValidationType.MANUAL

    # TODO (vroullier) 2023-03-24 : remove when we allow validation of rejected collective offer templates
    def test_cant_validate_non_pending_offer(self, legit_user, authenticated_client):
        collective_offer_to_validate = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.REJECTED
        )
        base_form = {}

        response = self._validate_collective_offer(authenticated_client, collective_offer_to_validate, base_form)
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_list_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates",
            q=collective_offer_to_validate.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_list_url)

        assert response.status_code == 200
        assert "Seules les offres collectives vitrines en attente peuvent être validées" in response.data.decode(
            "utf-8"
        )
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Rejetée"

    def _validate_collective_offer(self, authenticated_client, collective_offer_template, form):
        edit_url = url_for("backoffice_v3_web.collective_offer_template.list_collective_offer_templates")
        authenticated_client.get(edit_url)

        url = url_for(
            "backoffice_v3_web.collective_offer_template.validate_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        )
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)


class ValidateCollectiveOfferTemplateFormTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.collective_offer_template.get_validate_collective_offer_template_form"
        endpoint_kwargs = {"collective_offer_template_id": 1}
        needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_validate_form_test(self, legit_user, authenticated_client):
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()

        form_url = url_for(
            "backoffice_v3_web.collective_offer_template.get_validate_collective_offer_template_form",
            collective_offer_template_id=collective_offer_template.id,
            _external=True,
        )

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class RejectCollectiveOfferTemplateTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.collective_offer_template.reject_collective_offer_template"
        endpoint_kwargs = {"collective_offer_template_id": 1}
        needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_reject_collective_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_reject = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )
        base_form = {}

        response = self._reject_collective_offer_template(
            authenticated_client, collective_offer_template_to_reject, base_form
        )
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_template_list_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates",
            q=collective_offer_template_to_reject.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_template_list_url)

        assert response.status_code == 200
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Rejetée"

        assert collective_offer_template_to_reject.isActive is False
        assert collective_offer_template_to_reject.lastValidationType == OfferValidationType.MANUAL

    # TODO (vroullier) 2023-03-24 : remove when we allow validation of validated collective offer templates
    def test_cant_reject_non_pending_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_reject = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.APPROVED
        )
        base_form = {}

        response = self._reject_collective_offer_template(
            authenticated_client, collective_offer_template_to_reject, base_form
        )
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_template_list_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates",
            q=collective_offer_template_to_reject.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_template_list_url)

        assert response.status_code == 200
        assert "Seules les offres collectives vitrines en attente peuvent être rejetées" in response.data.decode(
            "utf-8"
        )
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Validée"

    def _reject_collective_offer_template(self, authenticated_client, collective_offer_template, form):
        edit_url = url_for("backoffice_v3_web.collective_offer_template.list_collective_offer_templates")
        authenticated_client.get(edit_url)

        url = url_for(
            "backoffice_v3_web.collective_offer_template.reject_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        )
        form["csrf_token"] = g.get("csrf_token", "")

        return authenticated_client.post(url, form=form)


class RejectCollectiveOfferTemplateFormTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.collective_offer_template.get_reject_collective_offer_template_form"
        endpoint_kwargs = {"collective_offer_template_id": 1}
        needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_reject_form_test(self, legit_user, authenticated_client):
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()

        form_url = url_for(
            "backoffice_v3_web.collective_offer_template.get_reject_collective_offer_template_form",
            collective_offer_template_id=collective_offer_template.id,
            _external=True,
        )

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200
