import datetime
from decimal import Decimal

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import date as date_utils

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class ListCustomReimbursementRulesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.reimbursement_rules.list_custom_reimbursement_rules"
    needed_permission = perm_models.Permissions.READ_REIMBURSEMENT_RULES

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch custom reimbursement rules with extra data (1 query)
    expected_num_queries = 3

    def test_list_custom_reimbursement_rules(self, authenticated_client):
        start = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        end = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        offer_rule = finance_factories.CustomReimbursementRuleFactory(amount=27, timespan=(start, None))
        offerer = offerers_factories.OffererFactory()
        offerer_rule = finance_factories.CustomReimbursementRuleFactory(
            offerer=offerer, rate=0.5, subcategories=["FESTIVAL_LIVRE"]
        )

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        rows = sorted(rows, key=lambda row: int(row["ID règle"]))

        assert rows[0]["ID règle"] == str(offer_rule.id)
        assert rows[0]["Structure"] == offer_rule.offer.venue.managingOfferer.name
        assert rows[0]["SIREN"] == offer_rule.offer.venue.managingOfferer.siren
        assert rows[0]["Lieu"] == offer_rule.offer.venue.name
        assert rows[0]["Offre"] == offer_rule.offer.name
        assert rows[0]["Taux de remboursement"] == ""
        assert rows[0]["Montant remboursé"] == "27,00 €"
        assert rows[0]["Sous-catégories"] == ""
        assert rows[0]["Date d'application"] == start.strftime("%d/%m/%Y") + " → ∞"

        assert rows[1]["ID règle"] == str(offerer_rule.id)
        assert rows[1]["Structure"] == offerer_rule.offerer.name
        assert rows[1]["SIREN"] == offerer_rule.offerer.siren
        assert rows[1]["Lieu"] == ""
        assert rows[1]["Offre"] == ""
        assert rows[1]["Taux de remboursement"] == "50,00 %"
        assert rows[1]["Montant remboursé"] == ""
        assert rows[1]["Sous-catégories"] == subcategories_v2.FESTIVAL_LIVRE.pro_label
        assert rows[1]["Date d'application"] == start.strftime("%d/%m/%Y") + " → " + end.strftime("%d/%m/%Y")

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_offer_id(self, authenticated_client):
        offer_rule = finance_factories.CustomReimbursementRuleFactory()
        searched_id = str(offer_rule.offerId)
        finance_factories.CustomReimbursementRuleFactory.create_batch(2)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule.id)

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_offer_name(self, authenticated_client):
        offer = offers_factories.OfferFactory(name="Comment obtenir un tarif dérogatoire au pass")
        offer_rule = finance_factories.CustomReimbursementRuleFactory(offer=offer)
        finance_factories.CustomReimbursementRuleFactory.create_batch(2)
        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Comment obtenir un tarif dérogatoire au pass")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule.id)

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_id_not_found(self, authenticated_client):
        rules = finance_factories.CustomReimbursementRuleFactory.create_batch(5)
        # when
        search_query = str(rules[-1].id * 1000)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 0

    def test_list_rules_by_offerer(self, authenticated_client):
        offerer_1 = offerers_factories.OffererFactory()
        offerer_rule_1 = finance_factories.CustomReimbursementRuleFactory(offerer=offerer_1)
        offerer_2 = offerers_factories.OffererFactory()
        offerer_rule_2 = finance_factories.CustomReimbursementRuleFactory(offerer=offerer_2)
        other_offerer = offerers_factories.OffererFactory()
        finance_factories.CustomReimbursementRuleFactory(offerer=other_offerer)
        offer = offers_factories.OfferFactory(venue__managingOfferer=offerer_1)
        offerer_rule_3 = finance_factories.CustomReimbursementRuleFactory(offer=offer)

        # when
        offerer_ids = [offerer_1.id, offerer_2.id]
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_ids))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID règle"]) for row in rows) == {offerer_rule_1.id, offerer_rule_2.id, offerer_rule_3.id}

    def test_list_rules_more_than_max(self, authenticated_client):
        # given
        finance_factories.CustomReimbursementRuleFactory.create_batch(30)

        # when
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, limit=25))

        # then
        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data) == 25  # extra data in second row for each booking
        assert "Il y a plus de 25 résultats dans la base de données" in html_parser.extract_alert(response.data)


class GetCreateCustomReimbursementRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.reimbursement_rules.get_create_custom_reimbursement_rule_form"
    needed_permission = perm_models.Permissions.CREATE_REIMBURSEMENT_RULES

    def test_get_create_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class CreateCustomReimbursementRuleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.reimbursement_rules.create_custom_reimbursement_rule"
    needed_permission = perm_models.Permissions.CREATE_REIMBURSEMENT_RULES
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    next_year = datetime.date.today() + datetime.timedelta(days=365)

    def test_create_custom_reimbursement_rule(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "subcategories": ["ABO_CONCERT", "ABO_JEU_VIDEO"],
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Tarif dérogatoire créé"

        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.offererId == offerer.id
        assert rule.rate == Decimal("0.1234")
        assert rule.timespan.lower == date_utils.get_day_start(
            self.tomorrow, finance_utils.ACCOUNTING_TIMEZONE
        ).astimezone(tz=None).replace(tzinfo=None)
        assert rule.timespan.upper == date_utils.get_day_start(
            self.next_year + datetime.timedelta(days=1), finance_utils.ACCOUNTING_TIMEZONE
        ).astimezone(tz=None).replace(tzinfo=None)
        assert set(rule.subcategories) == {"ABO_CONCERT", "ABO_JEU_VIDEO"}

    def test_create_with_invalid_offerer(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": 0,
                "rate": "12,34",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert "Tarif dérogatoire non créé" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert finance_models.CustomReimbursementRule.query.count() == 0

    def test_create_with_no_end_date(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": "",
            },
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Tarif dérogatoire créé"

        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.timespan.lower == date_utils.get_day_start(
            self.tomorrow, finance_utils.ACCOUNTING_TIMEZONE
        ).astimezone(tz=None).replace(tzinfo=None)
        assert rule.timespan.upper is None

    def test_create_with_start_date_too_early(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "12,34",
                "start_date": "1970-01-01",
            },
        )
        assert response.status_code == 303
        assert "Ne peut pas commencer avant demain" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert finance_models.CustomReimbursementRule.query.count() == 0

    def test_create_with_end_date_before_start_date(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "12,34",
                "start_date": self.next_year,
                "end_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert "Ne peut pas être postérieure à la date de fin" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert finance_models.CustomReimbursementRule.query.count() == 0

    def test_create_with_invalid_rate(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "pouet",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert finance_models.CustomReimbursementRule.query.count() == 0

    def test_create_with_rate_100(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "100",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Tarif dérogatoire créé"

        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.rate == Decimal(1)

    def test_create_with_rate_0(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "0",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Tarif dérogatoire créé"

        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.rate == Decimal(0)

    def test_create_with_negative_rate(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "-10",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert "Doit contenir un nombre positif" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert finance_models.CustomReimbursementRule.query.count() == 0

    def test_create_with_greater_rate(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "1203",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert "Doit contenir un nombre inférieur ou égal à 100" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert finance_models.CustomReimbursementRule.query.count() == 0

    def test_create_with_no_subcategory(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Tarif dérogatoire créé"

        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.offererId == offerer.id
        assert rule.subcategories == []

    def test_create_with_invalid_subcategory(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "subcategories": ["POUET"],
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert finance_models.CustomReimbursementRule.query.count() == 0


class GetEditCustomReimbursementRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.reimbursement_rules.get_edit_custom_reimbursement_rule_form"
    endpoint_kwargs = {"reimbursement_rule_id": 1}
    needed_permission = perm_models.Permissions.CREATE_REIMBURSEMENT_RULES

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        custom_reimbursement_rule = finance_factories.CustomReimbursementRuleFactory()
        form_url = url_for(self.endpoint, reimbursement_rule_id=custom_reimbursement_rule.id)
        db.session.expire(custom_reimbursement_rule)

        with assert_num_queries(3):  # session + user + rule
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class EditCustomReimbursementRuleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.reimbursement_rules.edit_custom_reimbursement_rule"
    endpoint_kwargs = {"reimbursement_rule_id": 1}
    needed_permission = perm_models.Permissions.CREATE_REIMBURSEMENT_RULES

    def test_update_custom_reimbursement_rule(self, authenticated_client):
        original_timespan = (datetime.datetime.today() - datetime.timedelta(days=10), None)
        rule = finance_factories.CustomReimbursementRuleFactory(timespan=original_timespan)
        new_end_date = datetime.date.today() + datetime.timedelta(days=5)

        response = self.post_to_endpoint(
            authenticated_client, reimbursement_rule_id=rule.id, form={"end_date": new_end_date}
        )

        assert response.status_code == 303
        assert "Tarif dérogatoire modifié" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        db.session.refresh(rule)
        assert rule.timespan.lower == original_timespan[0]
        assert rule.timespan.upper == date_utils.get_day_start(
            new_end_date + datetime.timedelta(days=1), finance_utils.ACCOUNTING_TIMEZONE
        ).astimezone(tz=None).replace(tzinfo=None)

    def test_update_with_no_end_date(self, authenticated_client):
        original_timespan = (
            datetime.datetime.today() - datetime.timedelta(days=10),
            datetime.datetime.today() + datetime.timedelta(days=5),
        )
        rule = finance_factories.CustomReimbursementRuleFactory(timespan=original_timespan)

        response = self.post_to_endpoint(authenticated_client, reimbursement_rule_id=rule.id, form={"end_date": ""})

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "Tarif dérogatoire modifié"
        )

        db.session.refresh(rule)
        assert rule.timespan.lower == original_timespan[0]
        assert rule.timespan.upper is None

    def test_update_with_end_date_before_start_date(self, authenticated_client):
        original_timespan = (datetime.datetime.today() + datetime.timedelta(days=10), None)
        rule = finance_factories.CustomReimbursementRuleFactory(timespan=original_timespan)
        new_end_date = datetime.date.today() + datetime.timedelta(days=5)

        response = self.post_to_endpoint(
            authenticated_client, reimbursement_rule_id=rule.id, form={"end_date": new_end_date}
        )

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La date de fin ne peut être avant la date de début"
        )

        db.session.refresh(rule)
        assert rule.timespan.lower, rule.timespan.upper == original_timespan

    def test_update_with_conflicting_end_date(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        original_timespan = (
            datetime.datetime.today() - datetime.timedelta(days=10),
            datetime.datetime.today() + datetime.timedelta(days=5),
        )
        rule = finance_factories.CustomReimbursementRuleFactory(offerer=offerer, timespan=original_timespan)

        conflicting_rule = finance_factories.CustomReimbursementRuleFactory(
            offerer=offerer,
            timespan=(
                datetime.datetime.today() + datetime.timedelta(days=10),
                datetime.datetime.today() + datetime.timedelta(days=15),
            ),
        )

        response = self.post_to_endpoint(
            authenticated_client,
            reimbursement_rule_id=rule.id,
            form={"end_date": datetime.date.today() + datetime.timedelta(days=20)},
        )

        assert response.status_code == 303
        assert html_parser.extract_alert(
            authenticated_client.get(response.location).data
        ) == "Ce tarif dérogatoire est en conflit avec les tarifs dérogatoires {'%s'}" % (conflicting_rule.id,)

        db.session.refresh(rule)
        assert rule.timespan.lower, rule.timespan.upper == original_timespan
