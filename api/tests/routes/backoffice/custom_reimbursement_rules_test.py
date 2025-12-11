import datetime
from decimal import Decimal

import pytest
from flask import url_for

from pcapi.core.categories import subcategories
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
    pytest.mark.backoffice,
]


class ListCustomReimbursementRulesTest(GetEndpointHelper):
    endpoint = "backoffice_web.reimbursement_rules.list_custom_reimbursement_rules"
    needed_permission = perm_models.Permissions.READ_REIMBURSEMENT_RULES

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session + user (1 query)
    # - fetch custom reimbursement rules with extra data (1 query)
    expected_num_queries = 2

    def test_list_custom_reimbursement_rules(self, authenticated_client):
        start = date_utils.get_naive_utc_now() - datetime.timedelta(days=365)
        end = date_utils.get_naive_utc_now() + datetime.timedelta(days=365)
        offer_rule = finance_factories.CustomReimbursementRuleFactory(amount=2700, timespan=(start, None))
        venue = offerers_factories.VenueFactory()
        venue_rule = finance_factories.CustomReimbursementRuleFactory(venue=venue, rate=0.98, timespan=(start, None))
        offerer = offerers_factories.OffererFactory()
        offerer_rule = finance_factories.CustomReimbursementRuleFactory(
            offerer=offerer, rate=0.5, subcategories=["FESTIVAL_LIVRE"]
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3

        rows = sorted(rows, key=lambda row: int(row["ID règle"]))

        assert rows[0]["ID règle"] == str(offer_rule.id)
        assert rows[0]["Entité juridique"] == offer_rule.offer.venue.managingOfferer.name
        assert rows[0]["SIREN"] == offer_rule.offer.venue.managingOfferer.siren
        assert rows[0]["Partenaire culturel"] == offer_rule.offer.venue.name
        assert rows[0]["Offre"] == offer_rule.offer.name
        assert rows[0]["Taux de remboursement"] == ""
        assert rows[0]["Montant remboursé"] == "27,00 €"
        assert rows[0]["Sous-catégories"] == ""
        assert rows[0]["Date d'application"] == start.strftime("%d/%m/%Y") + " → ∞"

        assert rows[1]["ID règle"] == str(venue_rule.id)
        assert rows[1]["Entité juridique"] == venue_rule.venue.managingOfferer.name
        assert rows[1]["SIREN"] == venue_rule.venue.managingOfferer.siren
        assert rows[1]["Partenaire culturel"] == venue_rule.venue.name
        assert rows[1]["Offre"] == ""
        assert rows[1]["Taux de remboursement"] == "98,00 %"
        assert rows[1]["Montant remboursé"] == ""
        assert rows[1]["Sous-catégories"] == ""
        assert rows[1]["Date d'application"] == start.strftime("%d/%m/%Y") + " → ∞"

        assert rows[2]["ID règle"] == str(offerer_rule.id)
        assert rows[2]["Entité juridique"] == offerer_rule.offerer.name
        assert rows[2]["SIREN"] == offerer_rule.offerer.siren
        assert rows[2]["Partenaire culturel"] == ""
        assert rows[2]["Offre"] == ""
        assert rows[2]["Taux de remboursement"] == "50,00 %"
        assert rows[2]["Montant remboursé"] == ""
        assert rows[2]["Sous-catégories"] == subcategories.FESTIVAL_LIVRE.pro_label
        assert rows[2]["Date d'application"] == start.strftime("%d/%m/%Y") + " → " + end.strftime("%d/%m/%Y")

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_offer_id(self, authenticated_client):
        offer_rule = finance_factories.CustomReimbursementRuleFactory()
        searched_id = str(offer_rule.offerId)
        finance_factories.CustomReimbursementRuleFactory.create_batch(2)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=searched_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule.id)

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_offer_name(self, authenticated_client):
        offer = offers_factories.OfferFactory(name="Comment obtenir un tarif dérogatoire au pass")
        offer_rule = finance_factories.CustomReimbursementRuleFactory(offer=offer)
        finance_factories.CustomReimbursementRuleFactory.create_batch(2)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="Comment obtenir un tarif dérogatoire au pass")
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule.id)

        assert html_parser.extract_pagination_info(response.data) == (1, 1, len(rows))

    def test_list_rules_by_category(self, authenticated_client):
        offer_rule_music = finance_factories.CustomReimbursementRuleFactory(subcategories=["FESTIVAL_MUSIQUE"])
        finance_factories.CustomReimbursementRuleFactory(subcategories=["CARTE_MUSEE"])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, categories=["MUSIQUE_LIVE"]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule_music.id)

    def test_list_rules_by_subcategory(self, authenticated_client):
        offer_rule_music = finance_factories.CustomReimbursementRuleFactory(subcategories=["FESTIVAL_MUSIQUE"])
        finance_factories.CustomReimbursementRuleFactory(subcategories=["CARTE_MUSEE"])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, subcategories=["FESTIVAL_MUSIQUE"]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID règle"] == str(offer_rule_music.id)

    def test_list_rules_by_id_not_found(self, authenticated_client):
        rules = finance_factories.CustomReimbursementRuleFactory.create_batch(5)
        search_query = str(rules[-1].id * 1000)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=search_query))
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
        venue_rule = finance_factories.CustomReimbursementRuleFactory(
            venue=offerers_factories.VenueFactory(managingOfferer=offerer_1)
        )

        offerer_ids = [offerer_1.id, offerer_2.id]
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_ids))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert set(int(row["ID règle"]) for row in rows) == {
            offerer_rule_1.id,
            offerer_rule_2.id,
            offerer_rule_3.id,
            venue_rule.id,
        }

    def test_list_rules_more_than_max(self, authenticated_client):
        finance_factories.CustomReimbursementRuleFactory.create_batch(30)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, limit=25))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 25  # extra data in second row for each booking
        assert "Il y a plus de 25 résultats dans la base de données" in html_parser.extract_alert(response.data)

    def test_display_list_even_if_rule_on_venue_without_siret(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        finance_factories.CustomReimbursementRuleFactory(venue=venue)
        venue.comment = "comment"
        venue.siret = None
        db.session.flush()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, limit=25))
            assert response.status_code == 200


class GetCreateCustomReimbursementRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.reimbursement_rules.get_create_custom_reimbursement_rule_form"
    needed_permission = perm_models.Permissions.CREATE_REIMBURSEMENT_RULES

    def test_get_create_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint)

        with assert_num_queries(1):  # session
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class CreateCustomReimbursementRuleTest(PostEndpointHelper):
    endpoint = "backoffice_web.reimbursement_rules.create_custom_reimbursement_rule"
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
                "venue": "",
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le nouveau tarif dérogatoire a été créé"
        )

        rule = db.session.query(finance_models.CustomReimbursementRule).one()
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
                "venue": "",
                "rate": "12,34",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Must provide offer, venue, or offerer (only one)"
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_invalid_venue(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": "",
                "venue": 0,
                "rate": "12,34",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Must provide offer, venue, or offerer (only one)"
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_not_a_pricing_point(self, authenticated_client):
        venue = offerers_factories.VenueWithoutSiretFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": "",
                "venue": venue.id,
                "rate": "12,34",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"Le lieu {venue.id} - {venue.name} doit être un point de valorisation."
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_venue_and_offerer(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": 1,
                "venue": 1,
                "rate": "12,34",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Un tarif dérogatoire ne peut pas concerner un partenaire culturel et une entité juridique en même temps"
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_no_end_date(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": "",
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le nouveau tarif dérogatoire a été créé"
        )

        rule = db.session.query(finance_models.CustomReimbursementRule).one()
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
                "venue": "",
                "rate": "12,34",
                "start_date": "1970-01-01",
            },
        )
        assert response.status_code == 303
        assert "Ne peut pas commencer avant demain" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_end_date_before_start_date(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "12,34",
                "start_date": self.next_year,
                "end_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert "Ne peut pas être postérieure à la date de fin" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_invalid_rate(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "pouet",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_rate_100(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "100",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le nouveau tarif dérogatoire a été créé"
        )

        rule = db.session.query(finance_models.CustomReimbursementRule).one()
        assert rule.rate == Decimal(1)

    def test_create_with_rate_0(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "0",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Must provide rate or amount (but not both)"
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_negative_rate(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "-10",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert "Doit contenir un nombre positif" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_greater_rate(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "1203",
                "start_date": self.tomorrow,
            },
        )
        assert response.status_code == 303
        assert "Doit contenir un nombre inférieur ou égal à 100" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0

    def test_create_with_no_subcategory(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "venue": "",
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Le nouveau tarif dérogatoire a été créé"
        )

        rule = db.session.query(finance_models.CustomReimbursementRule).one()
        assert rule.offererId == offerer.id
        assert rule.subcategories == []

    def test_create_with_invalid_subcategory(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "offerer": offerer.id,
                "subcategories": ["POUET"],
                "venue": "",
                "rate": "12,34",
                "start_date": self.tomorrow,
                "end_date": self.next_year,
            },
        )
        assert response.status_code == 303
        assert db.session.query(finance_models.CustomReimbursementRule).count() == 0


class GetEditCustomReimbursementRuleFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.reimbursement_rules.get_edit_custom_reimbursement_rule_form"
    endpoint_kwargs = {"reimbursement_rule_id": 1}
    needed_permission = perm_models.Permissions.CREATE_REIMBURSEMENT_RULES

    def test_get_edit_form_test(self, legit_user, authenticated_client):
        custom_reimbursement_rule = finance_factories.CustomReimbursementRuleFactory()
        form_url = url_for(self.endpoint, reimbursement_rule_id=custom_reimbursement_rule.id)
        db.session.expire(custom_reimbursement_rule)

        with assert_num_queries(2):  # session + rule
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class EditCustomReimbursementRuleTest(PostEndpointHelper):
    endpoint = "backoffice_web.reimbursement_rules.edit_custom_reimbursement_rule"
    endpoint_kwargs = {"reimbursement_rule_id": 1}
    needed_permission = perm_models.Permissions.CREATE_REIMBURSEMENT_RULES

    @pytest.mark.parametrize("start_day_gap", (1, -1))
    def test_update_custom_reimbursement_rule(self, authenticated_client, start_day_gap):
        original_timespan = (datetime.datetime.today() + datetime.timedelta(days=start_day_gap), None)
        rule = finance_factories.CustomReimbursementRuleFactory(timespan=original_timespan)
        new_end_date = datetime.date.today() + datetime.timedelta(days=5)

        response = self.post_to_endpoint(
            authenticated_client, reimbursement_rule_id=rule.id, form={"end_date": new_end_date}
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"custom-reimbursement-rule-row-{rule.id}")
        assert cells[1] == str(rule.id)

        db.session.refresh(rule)
        assert rule.timespan.lower == original_timespan[0]
        assert rule.timespan.upper == date_utils.get_day_start(
            new_end_date + datetime.timedelta(days=1), finance_utils.ACCOUNTING_TIMEZONE
        ).astimezone(tz=None).replace(tzinfo=None)

    def test_update_with_anterior_end_date(self, authenticated_client):
        original_timespan = (
            datetime.datetime.today() - datetime.timedelta(days=5),
            None,
        )
        rule = finance_factories.CustomReimbursementRuleFactory(timespan=original_timespan)
        new_end_date = datetime.date.today() - datetime.timedelta(days=1)

        response = self.post_to_endpoint(
            authenticated_client, reimbursement_rule_id=rule.id, form={"end_date": new_end_date}
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"custom-reimbursement-rule-row-{rule.id}")
        assert cells[1] == str(rule.id)

        db.session.refresh(rule)
        assert rule.timespan.lower, rule.timespan.upper == original_timespan

    def test_update_when_end_date_already_defined(self, authenticated_client):
        original_timespan = (
            datetime.datetime.today() + datetime.timedelta(days=5),
            datetime.datetime.today() + datetime.timedelta(days=10),
        )
        rule = finance_factories.CustomReimbursementRuleFactory(timespan=original_timespan)
        new_end_date = datetime.date.today() + datetime.timedelta(days=15)

        response = self.post_to_endpoint(
            authenticated_client, reimbursement_rule_id=rule.id, form={"end_date": new_end_date}
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"custom-reimbursement-rule-row-{rule.id}")
        assert cells[1] == str(rule.id)

        db.session.refresh(rule)
        assert rule.timespan.lower, rule.timespan.upper == original_timespan

    def test_update_with_end_date_before_start_date(self, authenticated_client):
        original_timespan = (datetime.datetime.today() + datetime.timedelta(days=10), None)
        rule = finance_factories.CustomReimbursementRuleFactory(timespan=original_timespan)
        new_end_date = datetime.date.today() + datetime.timedelta(days=5)

        response = self.post_to_endpoint(
            authenticated_client, reimbursement_rule_id=rule.id, form={"end_date": new_end_date}
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"custom-reimbursement-rule-row-{rule.id}")
        assert cells[1] == str(rule.id)

        db.session.refresh(rule)
        assert rule.timespan.lower, rule.timespan.upper == original_timespan


class GetReimburementStatsTest(GetEndpointHelper):
    endpoint = "backoffice_web.reimbursement_rules.get_stats"
    needed_permission = perm_models.Permissions.READ_REIMBURSEMENT_RULES

    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session + user (1 query)
    # - fetch custom reimbursement rules statistics (1 query)
    expected_num_queries = 2

    def test_get_data(self, authenticated_client):
        finance_factories.CustomReimbursementRuleFactory.create_batch(4, offerer=offerers_factories.OffererFactory())
        finance_factories.CustomReimbursementRuleFactory.create_batch(5, venue=offerers_factories.VenueFactory())
        finance_factories.CustomReimbursementRuleFactory.create_batch(3, offer=offers_factories.OfferFactory())

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rules_count_by_offerer, rules_count_by_venue, rules_count_by_offer = html_parser.extract_cards_titles(
            response.data
        )

        assert rules_count_by_offerer == "4"
        assert rules_count_by_venue == "5"
        assert rules_count_by_offer == "3"
