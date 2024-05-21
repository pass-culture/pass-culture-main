from dataclasses import asdict
import datetime

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.categories.subcategories_v2 import EacFormat
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as user_factory
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(scope="function", name="collective_offer_templates")
def collective_offer_templates_fixture() -> tuple:
    collective_offer_template_1 = educational_factories.CollectiveOfferTemplateFactory(
        author=user_factory.ProFactory(),
        formats=[subcategories.EacFormat.ATELIER_DE_PRATIQUE],
    )
    collective_offer_template_2 = educational_factories.CollectiveOfferTemplateFactory(
        name="A Very Specific Name",
        formats=[subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
    )
    collective_offer_template_3 = educational_factories.CollectiveOfferTemplateFactory(
        name="A Very Specific Name That Is Longer",
        dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        validation=offers_models.OfferValidationStatus.REJECTED,
        formats=[subcategories.EacFormat.FESTIVAL_SALON_CONGRES, subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
    )
    return collective_offer_template_1, collective_offer_template_2, collective_offer_template_3


class ListCollectiveOfferTemplatesTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.list_collective_offer_templates"
    needed_permission = perm_models.Permissions.READ_OFFERS

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    expected_num_queries_when_no_query = 2
    # - fetch collective offer templates with joinedload including extra data (1 query)
    expected_num_queries = expected_num_queries_when_no_query + 1

    def test_list_collective_offer_templates_without_filter(self, authenticated_client, collective_offer_templates):
        with assert_num_queries(self.expected_num_queries_when_no_query):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    def test_list_collective_offer_templates_by_id(self, authenticated_client, collective_offer_templates):
        searched_id = str(collective_offer_templates[0].id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == searched_id
        assert rows[0]["Nom de l'offre"] == collective_offer_templates[0].name
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today() - datetime.timedelta(days=5)).strftime("%d/%m/%Y")
        assert rows[0]["Formats"] == ", ".join([fmt.value for fmt in collective_offer_templates[0].formats])
        assert rows[0]["Structure"] == collective_offer_templates[0].venue.managingOfferer.name
        assert rows[0]["Lieu"] == collective_offer_templates[0].venue.name
        assert rows[0]["Créateur de l'offre"] == collective_offer_templates[0].author.full_name

    def test_list_collective_offer_templates_by_name(self, authenticated_client, collective_offer_templates):
        searched_name = collective_offer_templates[1].name
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_name, sort="id", order="asc"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert rows[0]["ID"] == str(collective_offer_templates[1].id)
        assert rows[0]["Nom de l'offre"] == collective_offer_templates[1].name
        assert rows[0]["État"] == "Validée"
        assert rows[0]["Date de création"] == (datetime.date.today() - datetime.timedelta(days=5)).strftime("%d/%m/%Y")
        assert rows[0]["Structure"] == collective_offer_templates[1].venue.managingOfferer.name
        assert rows[0]["Lieu"] == collective_offer_templates[1].venue.name

    def test_list_offers_by_date(self, authenticated_client, collective_offer_templates):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_date=(datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
                    to_date=(datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[2].id}

    def test_list_collective_offer_templates_by_venue(self, authenticated_client, collective_offer_templates):
        venue_id = collective_offer_templates[1].venueId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue in the form
            response = authenticated_client.get(url_for(self.endpoint, venue=[venue_id]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[1].id}

    def test_list_collective_offer_templates_by_offerer(self, authenticated_client, collective_offer_templates):
        offerer_id = collective_offer_templates[1].venue.managingOffererId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected offerer in the form
            response = authenticated_client.get(url_for(self.endpoint, offerer=[offerer_id]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[1].id}

    def test_list_collective_offer_templates_by_status(self, authenticated_client, collective_offer_templates):
        status = collective_offer_templates[2].validation
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=[status.value]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID"]) for row in rows) == {collective_offer_templates[2].id}
        assert rows[0]["État"] == "Rejetée"

    def test_list_offers_by_all_filters(self, authenticated_client, collective_offer_templates):
        template = collective_offer_templates[2]
        venue_id = template.venueId
        with assert_num_queries(self.expected_num_queries + 1):  # +1 because of reloading selected venue
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="specific name",
                    formats=str(template.formats[0].name),
                    venue=[venue_id],
                )
            )
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

        # must be sorted, older first
        rows = html_parser.extract_table_rows(response.data)
        assert [row["Nom de l'offre"] for row in rows] == expected_list

    def test_list_collective_offer_templates_with_flagging_rules(self, authenticated_client):
        rule_1 = offers_factories.OfferValidationRuleFactory(name="Règle magique")
        rule_2 = offers_factories.OfferValidationRuleFactory(name="Règle moldue")
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
            flaggingValidationRules=[rule_1, rule_2]
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=str(collective_offer_template.id)))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Règles de conformité"] == ", ".join([rule_1.name, rule_2.name])

    def test_list_collective_offer_templates_by_format(self, authenticated_client):
        target_format = subcategories.EacFormat.CONCERT

        target_offer = educational_factories.CollectiveOfferTemplateFactory(formats=[target_format])
        educational_factories.CollectiveOfferTemplateFactory(formats=[subcategories.EacFormat.ATELIER_DE_PRATIQUE])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, formats=str(target_format.name)))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1

        assert rows[0]["ID"] == str(target_offer.id)

    def test_list_collective_offer_templates_with_offerer_confidence_rule(self, client, pro_fraud_admin):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer__name="Offerer")
        collective_offer_template_id = educational_factories.CollectiveOfferTemplateFactory(
            venue__managingOfferer=rule.offerer, venue__name="Venue"
        ).id

        client = client.with_bo_session_auth(pro_fraud_admin)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, q=collective_offer_template_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Structure"] == "Offerer Revue manuelle"
        assert rows[0]["Lieu"] == "Venue"

    def test_list_collective_offer_templates_with_venue_confidence_rule(self, client, pro_fraud_admin):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory(
            venue__name="Venue", venue__managingOfferer__name="Offerer"
        )
        collective_offer_template_id = educational_factories.CollectiveOfferTemplateFactory(venue=rule.venue).id

        client = client.with_bo_session_auth(pro_fraud_admin)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, q=collective_offer_template_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["Structure"] == "Offerer"
        assert rows[0]["Lieu"] == "Venue Revue manuelle"


class GetCollectiveOfferTemplateDetailTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.get_collective_offer_template_details"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch CollectiveOfferTemplate including joinedload of venue and offerer
    expected_num_queries = 3

    def test_nominal(self, authenticated_client):
        collectiveOfferTemplate = educational_factories.CollectiveOfferTemplateFactory(
            formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
        )
        url = url_for(self.endpoint, collective_offer_template_id=collectiveOfferTemplate.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content_as_text = html_parser.content_as_text(response.data)
        assert f"Date de création : {collectiveOfferTemplate.dateCreated.strftime('%d/%m/%Y')}" in content_as_text
        assert f"Description : {collectiveOfferTemplate.description}" in content_as_text
        assert f"Structure : {collectiveOfferTemplate.venue.managingOfferer.name}" in content_as_text
        assert f"Lieu : {collectiveOfferTemplate.venue.name}" in content_as_text
        assert f"Formats : {EacFormat.PROJECTION_AUDIOVISUELLE.value}" in content_as_text

    def test_collective_offer_template_not_found(self, authenticated_client):
        url = url_for(self.endpoint, collective_offer_template_id=1)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 404


class ValidateCollectiveOfferTemplateFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Valider l'offre"
    endpoint = "backoffice_web.collective_offer_template.get_collective_offer_template_details"

    @property
    def path(self):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        return url_for(self.endpoint, collective_offer_template_id=offer.id)


class RejectCollectiveOfferTemplateFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Rejeter l'offre"
    endpoint = "backoffice_web.collective_offer_template.get_collective_offer_template_details"

    @property
    def path(self):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        return url_for(self.endpoint, collective_offer_template_id=offer.id)


class ValidateCollectiveOfferTemplateTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.validate_collective_offer_template"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_validate_collective_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_validate = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_template_to_validate.id
        )
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_template_list_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates",
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

    def test_cant_validate_non_pending_offer(self, legit_user, authenticated_client):
        collective_offer_to_validate = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.REJECTED
        )

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_to_validate.id
        )
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_list_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates",
            q=collective_offer_to_validate.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_list_url)

        assert response.status_code == 200
        assert "Seules les offres collectives vitrine en attente peuvent être validées" in response.data.decode("utf-8")
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Rejetée"


class ValidateCollectiveOfferTemplateFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.get_validate_collective_offer_template_form"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_validate_form_test(self, legit_user, authenticated_client):
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()

        url = url_for(self.endpoint, collective_offer_template_id=collective_offer_template.id)

        with assert_num_queries(3):  # session + current user + collective offer
            response = authenticated_client.get(url)
            assert response.status_code == 200


class RejectCollectiveOfferTemplateTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.reject_collective_offer_template"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_reject_collective_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_reject = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.PENDING
        )

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_template_to_reject.id
        )
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_template_list_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates",
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

    def test_cant_reject_non_pending_offer_template(self, legit_user, authenticated_client):
        collective_offer_template_to_reject = educational_factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.APPROVED
        )

        response = self.post_to_endpoint(
            authenticated_client, collective_offer_template_id=collective_offer_template_to_reject.id
        )
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates", _external=True
        )
        assert response.location == expected_url

        collective_offer_template_list_url = url_for(
            "backoffice_web.collective_offer_template.list_collective_offer_templates",
            q=collective_offer_template_to_reject.id,
            _external=True,
        )
        response = authenticated_client.get(collective_offer_template_list_url)

        assert response.status_code == 200
        assert "Seules les offres collectives vitrine en attente peuvent être rejetées" in response.data.decode("utf-8")
        row = html_parser.extract_table_rows(response.data)
        assert len(row) == 1
        assert row[0]["État"] == "Validée"


class RejectCollectiveOfferTemplateFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.get_reject_collective_offer_template_form"
    endpoint_kwargs = {"collective_offer_template_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_reject_form_test(self, legit_user, authenticated_client):
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()

        form_url = url_for(self.endpoint, collective_offer_template_id=collective_offer_template.id)

        with assert_num_queries(3):  # session + current user + collective offer
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class BatchCollectiveOfferTemplatesValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.batch_validate_collective_offer_templates"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

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
            "backoffice_web.collective_offer_template.list_collective_offer_templates", _external=True
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
            assert collective_offer_template.lastValidationAuthor == legit_user

        received_dict = {email["To"]: email["template"] for email in mails_testing.outbox}
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
        collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(
            id=collective_offer_template.id
        ).one()
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        non_existing_collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.id.in_(fake_offer_ids)
        ).all()
        assert len(non_existing_collective_offer_template) == 0


class BatchCollectiveOfferTemplatesRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.batch_reject_collective_offer_templates"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

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
            "backoffice_web.collective_offer_template.list_collective_offer_templates", _external=True
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

        received_dict = {email["To"]: email["template"] for email in mails_testing.outbox}
        expected_dict = {
            collective_offer_templates[0].venue.bookingEmail: asdict(
                TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value
            ),
            collective_offer_templates[1].venue.bookingEmail: asdict(
                TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value
            ),
            collective_offer_templates[2].venue.bookingEmail: asdict(
                TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value
            ),
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
        collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(
            id=collective_offer_template.id
        ).one()
        assert collective_offer_template.validation == OfferValidationStatus.PENDING
        non_existing_collective_offer_templates = educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.id.in_(fake_offer_ids)
        ).all()
        assert len(non_existing_collective_offer_templates) == 0


class GetBatchCollectiveOfferTemplatesApproveFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.get_batch_validate_collective_offer_templates_form"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_batch_collective_offer_templates_approve_form(self, legit_user, authenticated_client):
        url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url)
            assert response.status_code == 200


class GetBatchCollectiveOfferTemplatesRejectFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer_template.get_batch_reject_collective_offer_templates_form"
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_get_batch_collective_offer_templates_reject_form(self, legit_user, authenticated_client):
        url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url)
            assert response.status_code == 200
