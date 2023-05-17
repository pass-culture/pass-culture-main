from dataclasses import asdict
import datetime

from flask import url_for
import pytest

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


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


class ListCollectiveOfferTemplatesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.list_collective_offer_templates"
    needed_permission = perm_models.Permissions.READ_OFFERS

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch collective offer templates with joinedload including extra data (1 query)
    expected_num_queries = 3

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
                    order=order,
                )
            )
            assert response.status_code == 200

        # then: must be sorted, older first
        rows = html_parser.extract_table_rows(response.data)
        assert [row["Nom de l'offre"] for row in rows] == expected_list


class ValidateCollectiveOfferTemplateTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.validate_collective_offer_template"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_validate_collective_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_validate = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_template_to_validate.id
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

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_to_validate.id
        )
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


class ValidateCollectiveOfferTemplateFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.get_validate_collective_offer_template_form"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_validate_form_test(self, legit_user, authenticated_client):
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()

        url = url_for(self.endpoint, collective_offer_template_id=collective_offer_template.id)

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(url)
            assert response.status_code == 200


class RejectCollectiveOfferTemplateTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.reject_collective_offer_template"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_reject_collective_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_reject = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_template_to_reject.id
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

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_template_to_reject.id
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


class RejectCollectiveOfferTemplateFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.get_reject_collective_offer_template_form"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_reject_form_test(self, legit_user, authenticated_client):
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()

        form_url = url_for(self.endpoint, collective_offer_template_id=collective_offer_template.id)

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class BatchCollectiveOfferTemplatesValidateTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.batch_validate_collective_offer_templates"
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_batch_validate_collective_offer_templates(self, legit_user, authenticated_client):
        collective_offer_templates = educational_factories.CollectiveOfferTemplateFactory.create_batch(
            3, validation=OfferValidationStatus.PENDING
        )
        parameter_ids = ", ".join(
            str(collective_offer_template.id) for collective_offer_template in collective_offer_templates
        )
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        for collective_offer_template in collective_offer_templates:
            db.session.refresh(collective_offer_template)
            assert collective_offer_template.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime(
                "%d/%m/%Y"
            )
            assert collective_offer_template.isActive is True
            assert collective_offer_template.lastValidationType is OfferValidationType.MANUAL
            assert collective_offer_template.validation is OfferValidationStatus.APPROVED

        received_dict = {email.sent_data["To"]: email.sent_data["template"] for email in mails_testing.outbox}
        expected_dict = {
            collective_offer_templates[0].venue.bookingEmail: asdict(TransactionalEmail.OFFER_APPROVAL_TO_PRO.value),
            collective_offer_templates[1].venue.bookingEmail: asdict(TransactionalEmail.OFFER_APPROVAL_TO_PRO.value),
            collective_offer_templates[2].venue.bookingEmail: asdict(TransactionalEmail.OFFER_APPROVAL_TO_PRO.value),
        }
        assert received_dict == expected_dict

    def test_batch_validate_collective_offer_templates_wrong_id(self, legit_user, authenticated_client):
        fake_offer_ids = [123, 456]
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )
        parameter_ids = f"{str(fake_offer_ids[0])}, {str(fake_offer_ids[1])}, {collective_offer_template}"
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})
        assert response.status_code == 303
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        collective_offer_template = educational_models.CollectiveOfferTemplate.query.get(collective_offer_template.id)
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        non_existing_collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.id.in_(fake_offer_ids)
        ).all()
        assert len(non_existing_collective_offer_template) == 0


class BatchCollectiveOfferTemplatesRejectTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.batch_reject_collective_offer_templates"
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_batch_reject_offers(self, legit_user, authenticated_client):
        collective_offer_templates = educational_factories.CollectiveOfferTemplateFactory.create_batch(
            3, validation=OfferValidationStatus.PENDING
        )
        parameter_ids = ", ".join(
            str(collective_offer_template.id) for collective_offer_template in collective_offer_templates
        )

        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_v3_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        for collective_offer_template in collective_offer_templates:
            db.session.refresh(collective_offer_template)
            assert collective_offer_template.lastValidationDate.strftime("%d/%m/%Y") == datetime.date.today().strftime(
                "%d/%m/%Y"
            )
            assert collective_offer_template.isActive is False
            assert collective_offer_template.lastValidationType is OfferValidationType.MANUAL
            assert collective_offer_template.validation is OfferValidationStatus.REJECTED

        assert len(mails_testing.outbox) == 3

        received_dict = {email.sent_data["To"]: email.sent_data["template"] for email in mails_testing.outbox}
        expected_dict = {
            collective_offer_templates[0].venue.bookingEmail: asdict(TransactionalEmail.OFFER_REJECTION_TO_PRO.value),
            collective_offer_templates[1].venue.bookingEmail: asdict(TransactionalEmail.OFFER_REJECTION_TO_PRO.value),
            collective_offer_templates[2].venue.bookingEmail: asdict(TransactionalEmail.OFFER_REJECTION_TO_PRO.value),
        }
        assert received_dict == expected_dict

    def test_batch_reject_collective_offer_templates_wrong_id(self, legit_user, authenticated_client):
        fake_offer_ids = [123, 456]
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )
        parameter_ids = f"{str(fake_offer_ids[0])}, {str(fake_offer_ids[1])}, {collective_offer_template}"
        response = self.post_to_endpoint(authenticated_client, form={"object_ids": parameter_ids})

        assert response.status_code == 303
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        collective_offer_template = educational_models.CollectiveOfferTemplate.query.get(collective_offer_template.id)
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        non_existing_collective_offer_templates = educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.id.in_(fake_offer_ids)
        ).all()
        assert len(non_existing_collective_offer_templates) == 0


class GetBatchCollectiveOfferTemplatesApproveFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.get_batch_validate_collective_offer_templates_form"
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_batch_collective_offer_templates_approve_form(self, legit_user, authenticated_client):
        # when
        url = url_for(self.endpoint)
        response = authenticated_client.get(url)

        # then
        assert response.status_code == 200


class GetBatchCollectiveOfferTemplatesRejectFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.collective_offer_template.get_batch_reject_collective_offer_templates_form"
    needed_permission = perm_models.Permissions.FRAUD_ACTIONS

    def test_get_batch_collective_offer_templates_reject_form(self, legit_user, authenticated_client):
        # when
        url = url_for(self.endpoint)
        response = authenticated_client.get(url)

        # then
        assert response.status_code == 200
