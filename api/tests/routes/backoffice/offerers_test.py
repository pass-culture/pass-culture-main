import datetime
from operator import attrgetter
import re

from flask import url_for
import pytest

from pcapi.connectors.entreprise.backends.testing import TestingBackend
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice.offerers import offerer_blueprint
from pcapi.routes.backoffice.pro.forms import TypeOptions

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetOffererTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + current user (2 queries)
    # - offerer with joined data except tags (1 query)
    # - get offerer tags (1 query)
    # - get all tags for edit form (1 query)
    # - get feature flag: WIP_ENABLE_PRO_SIDE_NAV (1 query)
    expected_num_queries = 5

    def test_keep_search_parameters_on_top(self, authenticated_client, offerer):
        url = url_for(self.endpoint, offerer_id=offerer.id, q=offerer.name, departments=["75", "77"])

        response = authenticated_client.get(url)
        assert response.status_code == 200

        assert html_parser.extract_input_value(response.data, "q") == offerer.name
        selected_type = html_parser.extract_select_options(response.data, "pro_type", selected_only=True)
        assert set(selected_type.keys()) == {TypeOptions.OFFERER.name}
        selected_departments = html_parser.extract_select_options(response.data, "departments", selected_only=True)
        assert set(selected_departments.keys()) == {"75", "77"}

    def test_search_have_departements_preference_parameters_on_top(self, authenticated_client, legit_user, offerer):
        url = url_for(self.endpoint, offerer_id=offerer.id)
        legit_user.backoffice_profile.preferences = {"departments": ["04", "05", "06"]}
        db.session.flush()

        response = authenticated_client.get(url)
        assert response.status_code == 200

        assert html_parser.extract_input_value(response.data, "q") == ""
        selected_type = html_parser.extract_select_options(response.data, "pro_type", selected_only=True)
        assert set(selected_type.keys()) == {TypeOptions.OFFERER.name}
        selected_departments = html_parser.extract_select_options(response.data, "departments", selected_only=True)
        assert set(selected_departments.keys()) == {"04", "05", "06"}

    def test_get_offerer(self, authenticated_client, offerer, offerer_tags):
        offerers_factories.OffererTagMappingFactory(tagId=offerer_tags[0].id, offererId=offerer.id)
        offerers_factories.OffererTagMappingFactory(tagId=offerer_tags[1].id, offererId=offerer.id)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert offerer.name in content
        assert f"Offerer ID : {offerer.id} " in content
        assert f"SIREN : {offerer.siren} " in content
        assert "Région : Occitanie " in content
        assert f"Ville : {offerer.city} " in content
        assert f"Code postal : {offerer.postalCode} " in content
        assert f"Adresse : {offerer.street} " in content
        assert "Peut créer une offre EAC : Oui" in content
        assert "Présence CB dans les lieux : 0 OK / 0 KO " in content
        assert "Tags structure : Collectivité Top acteur " in content
        assert "Validation des offres : Suivre les règles" in content
        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Structure" in badges
        assert "Validée" in badges
        assert "Suspendue" not in badges

    @pytest.mark.parametrize(
        "new_nav_users,old_nav_users",
        [
            (True, True),
            (False, True),
            (True, False),
            (False, False),
        ],
    )
    def test_get_offerer_with_new_nav_badges(self, new_nav_users, old_nav_users, authenticated_client, offerer):
        if new_nav_users:
            user_with_new_nav = users_factories.ProFactory()
            users_factories.UserProNewNavStateFactory(user=user_with_new_nav)
            offerers_factories.UserOffererFactory(user=user_with_new_nav, offerer=offerer)
        if old_nav_users:
            _user_exclude_from_beta_test = users_factories.ProFactory()

            user_with_nav_date_in_the_future = users_factories.ProFactory()
            users_factories.UserProNewNavStateFactory(
                user=user_with_nav_date_in_the_future,
                eligibilityDate=None,
                newNavDate=datetime.datetime.utcnow() + datetime.timedelta(days=5),
            )
            offerers_factories.UserOffererFactory(user=user_with_nav_date_in_the_future, offerer=offerer)

            user_with_old_nav = users_factories.ProFactory()
            users_factories.UserProNewNavStateFactory(user=user_with_old_nav, eligibilityDate=None, newNavDate=None)
            offerers_factories.UserOffererFactory(user=user_with_old_nav, offerer=offerer)

            eligible_user_with_inactivated_new_nav = users_factories.ProFactory()
            users_factories.UserProNewNavStateFactory(
                user=eligible_user_with_inactivated_new_nav, eligibilityDate=datetime.datetime.utcnow(), newNavDate=None
            )
            offerers_factories.UserOffererFactory(user=eligible_user_with_inactivated_new_nav, offerer=offerer)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Structure" in badges
        assert "Validée" in badges
        assert "Suspendue" not in badges

        if new_nav_users:
            assert "Nouvelle interface" in badges
        if old_nav_users:
            assert "Ancienne interface" in badges

    def test_offerer_detail_contains_venue_bank_information_stats(
        self,
        authenticated_client,
        offerer,
    ):
        venue_with_accepted_bank_account = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_accepted_bank_account,
            timespan=[
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                None,
            ],
            bankAccount=finance_factories.BankAccountFactory(label="Nouveau compte", offererId=offerer.id),
        )
        venue_with_two_bank_accounts = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_two_bank_accounts,
            timespan=[
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(days=1),
            ],
            bankAccount=finance_factories.BankAccountFactory(label="Ancien compte", offererId=offerer.id),
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_two_bank_accounts,
            timespan=[datetime.datetime.utcnow() - datetime.timedelta(days=1), None],
            bankAccount=finance_factories.BankAccountFactory(label="Nouveau compte", offererId=offerer.id),
        )

        venue_with_expired_bank_account = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_expired_bank_account,
            timespan=[
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(days=1),
            ],
            bankAccount=finance_factories.BankAccountFactory(label="Ancien compte", offererId=offerer.id),
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Présence CB dans les lieux : 2 OK / 1 KO " in html_parser.content_as_text(response.data)

    def test_offerer_with_adage_venue_has_adage_data(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(allowedOnAdage=True)
        offerers_factories.VenueFactory(managingOfferer=offerer, adageId="1234")
        offerers_factories.VenueFactory(managingOfferer=offerer, adageId=None)
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Peut créer une offre EAC : Oui" in html_parser.content_as_text(response.data)
        # One venue with adageId out of two physical venues
        assert "Lieux cartographiés sur ADAGE : 1/2" in html_parser.content_as_text(response.data)

    def test_offerer_with_no_adage_venue_has_adage_data(self, authenticated_client, offerer):
        offerer = offerers_factories.OffererFactory(allowedOnAdage=True)
        offerers_factories.VenueFactory(managingOfferer=offerer, adageId=None)

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Peut créer une offre EAC : Oui" in html_parser.content_as_text(response.data)
        assert "Lieux cartographiés sur ADAGE : 0/1" in html_parser.content_as_text(response.data)

    def test_offerer_with_no_individual_subscription_tab(self, authenticated_client, offerer):
        offerer_id = offerer.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        assert not html_parser.get_soup(response.data).find(class_="subscription-tab-pane")

    def test_offerer_with_individual_subscription_tab_no_data(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory(name="auto-entrepreneur")
        offerer = offerers_factories.NotValidatedOffererFactory(tags=[tag])
        offerer_id = offerer.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        assert html_parser.get_soup(response.data).find(class_="subscription-tab-pane")

    def test_offerer_with_individual_subscription_data(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory(name="auto-entrepreneur")
        offerer = offerers_factories.NotValidatedOffererFactory(tags=[tag])
        offerers_factories.IndividualOffererSubscription(offerer=offerer)
        offerer_id = offerer.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        assert html_parser.get_soup(response.data).find(class_="subscription-tab-pane")

    @pytest.mark.parametrize(
        "factory, expected_text",
        [
            (offerers_factories.WhitelistedOffererConfidenceRuleFactory, "Validation auto"),
            (offerers_factories.ManualReviewOffererConfidenceRuleFactory, "Revue manuelle"),
        ],
    )
    def test_get_offerer_with_confidence_rule(self, authenticated_client, factory, expected_text):
        rule = factory()
        url = url_for(self.endpoint, offerer_id=rule.offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Validation des offres : {expected_text}" in response_text

    def test_get_offerer_which_does_not_exist(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, offerer_id=12345))
        assert response.status_code == 404


class SuspendOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.suspend_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_suspend_offerer(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"comment": "Test suspension"}
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)
        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == f"La structure {offerer.name} ({offerer.id}) a été suspendue"

        updated_offerer = offerers_models.Offerer.query.filter_by(id=offerer.id).one()
        assert not updated_offerer.isActive

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_SUSPENDED
        assert action.authorUser == legit_user
        assert action.comment == "Test suspension"

    def test_cant_suspend_offerer_with_bookings(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        offers_factories.OfferFactory(venue__managingOfferer=offerer)
        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer)

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)
        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de suspendre une structure juridique pour laquelle il existe des réservations"
        )

        not_updated_offerer = offerers_models.Offerer.query.filter_by(id=offerer.id).one()
        assert not_updated_offerer.isActive

        assert history_models.ActionHistory.query.count() == 0


class UnsuspendOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.unsuspend_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_unsuspend_offerer(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory(isActive=False)

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"comment": "Test réactivation"}
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)
        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == f"La structure {offerer.name} ({offerer.id}) a été réactivée"

        updated_offerer = offerers_models.Offerer.query.filter_by(id=offerer.id).one()
        assert updated_offerer.isActive

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_UNSUSPENDED
        assert action.authorUser == legit_user
        assert action.comment == "Test réactivation"


class DeleteOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.delete_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.DELETE_PRO_ENTITY

    def test_delete_offerer(self, legit_user, authenticated_client):
        offerer_to_delete = offerers_factories.OffererFactory()
        offerer_to_delete_name = offerer_to_delete.name
        offerer_to_delete_id = offerer_to_delete.id

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_delete.id)
        assert response.status_code == 303
        assert offerers_models.Offerer.query.filter(offerers_models.Offerer.id == offerer_to_delete_id).count() == 0

        expected_url = url_for("backoffice_web.pro.search_pro", _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == f"La structure {offerer_to_delete_name} ({offerer_to_delete_id}) a été supprimée"
        )

    def test_cant_delete_offerer_with_bookings(self, legit_user, authenticated_client):
        offerer_to_delete = offerers_factories.OffererFactory()
        offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer_to_delete)
        offerer_to_delete_id = offerer_to_delete.id

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_delete.id)
        assert response.status_code == 303
        assert offerers_models.Offerer.query.filter(offerers_models.Offerer.id == offerer_to_delete_id).count() == 1

        expected_url = url_for("backoffice_web.offerer.get", offerer_id=offerer_to_delete.id, _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de supprimer une structure juridique pour laquelle il existe des réservations"
        )

    def test_no_script_injection_in_offerer_name(self, legit_user, authenticated_client):
        offerer_id = offerers_factories.NotValidatedOffererFactory(name="<script>alert('coucou')</script>").id

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_id)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"La structure <script>alert('coucou')</script> ({offerer_id}) a été supprimée"
        )


class UpdateOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.update_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_update_offerer(self, legit_user, authenticated_client):
        offerer_to_edit = offerers_factories.OffererFactory()

        old_name = offerer_to_edit.name
        new_name = "Librairie bretonne"
        old_city = offerer_to_edit.city
        new_city = "Brest"
        old_postal_code = offerer_to_edit.postalCode
        new_postal_code = "29000"
        expected_new_region = "Bretagne"
        old_street = offerer_to_edit.street
        new_street = "1 Rue de Siam"

        base_form = {
            "name": new_name,
            "city": new_city,
            "postal_code": new_postal_code,
            "street": new_street,
            "tags": [tag.id for tag in offerer_to_edit.tags],
        }

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_edit.id, form=base_form)
        assert response.status_code == 303

        # Test redirection
        expected_url = url_for("backoffice_web.offerer.get", offerer_id=offerer_to_edit.id, _external=True)
        assert response.location == expected_url

        # Test region update
        response = authenticated_client.get(expected_url)
        assert f"Région : {expected_new_region}" in html_parser.content_as_text(response.data)

        # Test history
        history_url = url_for("backoffice_web.offerer.get_history", offerer_id=offerer_to_edit.id)
        history_response = authenticated_client.get(history_url)

        offerer_to_edit = offerers_models.Offerer.query.filter_by(id=offerer_to_edit.id).one()
        assert offerer_to_edit.name == new_name
        assert offerer_to_edit.city == new_city
        assert offerer_to_edit.postalCode == new_postal_code
        assert offerer_to_edit.street == new_street

        assert len(offerer_to_edit.action_history) == 1
        assert offerer_to_edit.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert offerer_to_edit.action_history[0].authorUser == legit_user
        assert set(offerer_to_edit.action_history[0].extraData["modified_info"].keys()) == {
            "name",
            "city",
            "postalCode",
            "street",
        }

        history_rows = html_parser.extract_table_rows(history_response.data)
        assert len(history_rows) == 1
        assert history_rows[0]["Type"] == history_models.ActionType.INFO_MODIFIED.value
        assert f"Nom juridique : {old_name} => {offerer_to_edit.name}" in history_rows[0]["Commentaire"]
        assert f"Ville : {old_city} => {offerer_to_edit.city}" in history_rows[0]["Commentaire"]
        assert f"Code postal : {old_postal_code} => {offerer_to_edit.postalCode}" in history_rows[0]["Commentaire"]
        assert f"Adresse : {old_street} => {offerer_to_edit.street}" in history_rows[0]["Commentaire"]

    def test_update_offerer_tags(self, legit_user, authenticated_client):
        offerer_to_edit = offerers_factories.OffererFactory(
            street="Place de la Liberté", postalCode="29200", city="Brest"
        )
        tag1 = offerers_factories.OffererTagFactory(label="Premier tag")
        tag2 = offerers_factories.OffererTagFactory(label="Deuxième tag")
        tag3 = offerers_factories.OffererTagFactory(label="Troisième tag")
        offerers_factories.OffererTagMappingFactory(tagId=tag1.id, offererId=offerer_to_edit.id)

        base_form = {
            "name": offerer_to_edit.name,
            "city": offerer_to_edit.city,
            "postal_code": offerer_to_edit.postalCode,
            "street": offerer_to_edit.street,
            "tags": [tag2.id, tag3.id],
        }

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_edit.id, form=base_form)
        assert response.status_code == 303

        # Test history
        history_url = url_for("backoffice_web.offerer.get_history", offerer_id=offerer_to_edit.id)
        history_response = authenticated_client.get(history_url)

        updated_offerer = offerers_models.Offerer.query.filter_by(id=offerer_to_edit.id).one()
        assert updated_offerer.city == "Brest"
        assert updated_offerer.postalCode == "29200"
        assert updated_offerer.street == "Place de la Liberté"

        history_rows = html_parser.extract_table_rows(history_response.data)
        assert len(history_rows) == 1
        assert history_rows[0]["Type"] == history_models.ActionType.INFO_MODIFIED.value
        assert history_rows[0]["Auteur"] == legit_user.full_name
        assert "Premier tag => Deuxième tag, Troisième tag" in history_rows[0]["Commentaire"]
        for item in ("Adresse", "Code postal", "Ville"):
            assert item not in history_rows[0]["Commentaire"]

    def test_update_offerer_empty_name(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory(name="Original")

        base_form = {
            "name": "",
            "city": offerer.city,
            "postal_code": offerer.postalCode,
            "street": offerer.street,
            "tags": [],
        }

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=base_form)
        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs" in html_parser.extract_alert(response.data)

        assert offerer.name == "Original"
        assert len(offerer.action_history) == 0


class UpdateForFraudTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.update_for_fraud"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_set_rule(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={
                "confidence_level": offerers_models.OffererConfidenceLevel.WHITELIST.name,
                "comment": "Test",
            },
        )
        assert response.status_code == 303

        assert offerer.confidenceLevel == offerers_models.OffererConfidenceLevel.WHITELIST
        assert len(offerer.action_history) == 1
        action = offerer.action_history[0]
        assert action.actionType == history_models.ActionType.FRAUD_INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.comment == "Test"
        assert action.extraData == {
            "modified_info": {
                "confidenceRule.confidenceLevel": {
                    "old_info": None,
                    "new_info": offerers_models.OffererConfidenceLevel.WHITELIST.name,
                }
            }
        }

    def test_update_rule(self, legit_user, authenticated_client):
        rule = offerers_factories.WhitelistedOffererConfidenceRuleFactory()
        offerer = rule.offerer

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={
                "confidence_level": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                "comment": "Test",
            },
        )
        assert response.status_code == 303

        assert offerer.confidenceLevel == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
        assert len(offerer.action_history) == 1
        action = offerer.action_history[0]
        assert action.actionType == history_models.ActionType.FRAUD_INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.comment == "Test"
        assert action.extraData == {
            "modified_info": {
                "confidenceRule.confidenceLevel": {
                    "old_info": offerers_models.OffererConfidenceLevel.WHITELIST.name,
                    "new_info": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                }
            }
        }

    def test_remove_rule(self, legit_user, authenticated_client):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory()
        offerer = rule.offerer

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={
                "confidence_level": "",
                "comment": "Test",
            },
        )
        assert response.status_code == 303

        assert offerer.confidenceLevel is None
        assert offerers_models.OffererConfidenceRule.query.count() == 0
        assert len(offerer.action_history) == 1
        action = offerer.action_history[0]
        assert action.actionType == history_models.ActionType.FRAUD_INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.comment == "Test"
        assert action.extraData == {
            "modified_info": {
                "confidenceRule.confidenceLevel": {
                    "old_info": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                    "new_info": None,
                }
            }
        }

    def test_update_nothing(self, legit_user, authenticated_client):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory()
        offerer = rule.offerer

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={
                "confidence_level": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                "comment": "",
            },
        )
        assert response.status_code == 303

        assert offerer.confidenceLevel == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
        assert len(offerer.action_history) == 0


class GetOffererStatsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_stats"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_get_stats(self, authenticated_client, offerer):
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(
            venue=venue,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        educational_factories.CollectiveOfferFactory(
            venue=venue,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        booking = bookings_factories.BookingFactory(
            status=bookings_models.BookingStatus.USED,
            quantity=1,
            amount=10,
            stock=offers_factories.StockFactory(offer=offer),
        )
        url = url_for(self.endpoint, offerer_id=offerer.id)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get total revenue (1 query)
        # get offerers offers stats (6 query: 3 to check the quantity and 3 to get the data)
        with assert_num_queries(9):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert f"{str(booking.amount).replace('.', ',')} € de CA" in cards_text[0]
        assert "3 offres actives ( 1 IND / 2 EAC ) 0 offres inactives ( 0 IND / 0 EAC )" in cards_text


class GetOffererStatsDataTest:
    def test_get_data(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
        offerer_active_collective_offer_templates,
        offerer_inactive_collective_offer_templates,
        offerer_expired_offers,
        offerer_expired_collective_offers,
        individual_offerer_bookings,
        collective_offerer_booking,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (6 query)
        # get total revenue (1 query)
        with assert_num_queries(7):
            stats = offerer_blueprint.get_stats_data(offerer_id)
        assert stats["active"]["individual"] == 2
        assert stats["active"]["collective"] == 5
        assert stats["inactive"]["individual"] == 9
        assert stats["inactive"]["collective"] == 15

        total_revenue = stats["total_revenue"]

        assert total_revenue == 1694.0

    def test_individual_offers_only(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        individual_offerer_bookings,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (6 query)
        # get total revenue (1 query)
        with assert_num_queries(7):
            stats = offerer_blueprint.get_stats_data(offerer_id)

        assert stats["active"]["individual"] == 2
        assert stats["active"]["collective"] == 0
        assert stats["inactive"]["individual"] == 5
        assert stats["inactive"]["collective"] == 0

        total_revenue = stats["total_revenue"]

        assert total_revenue == 30.0

    def test_collective_offers_only(
        self,
        offerer,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
        collective_offerer_booking,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (6 query)
        # get total revenue (1 query)
        with assert_num_queries(7):
            stats = offerer_blueprint.get_stats_data(offerer_id)

        assert stats["active"]["individual"] == 0
        assert stats["active"]["collective"] == 4
        assert stats["inactive"]["individual"] == 0
        assert stats["inactive"]["collective"] == 7

        total_revenue = stats["total_revenue"]

        assert total_revenue == 1664.0

    def test_active_offers_only(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_active_collective_offers,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (6 query)
        # get total revenue (1 query)
        with assert_num_queries(7):
            stats = offerer_blueprint.get_stats_data(offerer_id)

        assert stats["active"]["individual"] == 2
        assert stats["active"]["collective"] == 4
        assert stats["inactive"]["individual"] == 0
        assert stats["inactive"]["collective"] == 0

        total_revenue = stats["total_revenue"]

        assert total_revenue == 0.0

    def test_inactive_offers_only(
        self,
        offerer,
        offerer_inactive_individual_offers,
        offerer_inactive_collective_offers,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (6 query)
        # get total revenue (1 query)
        with assert_num_queries(7):
            stats = offerer_blueprint.get_stats_data(offerer_id)

        assert stats["active"]["individual"] == 0
        assert stats["active"]["collective"] == 0
        assert stats["inactive"]["individual"] == 5
        assert stats["inactive"]["collective"] == 7

        total_revenue = stats["total_revenue"]

        assert total_revenue == 0.0

    def test_no_bookings(self, offerer):
        offerer_id = offerer.id

        # get active/inactive stats (6 query)
        # get total revenue (1 query)
        with assert_num_queries(7):
            stats = offerer_blueprint.get_stats_data(offerer_id)

        assert stats["active"]["individual"] == 0
        assert stats["active"]["collective"] == 0
        assert stats["inactive"]["individual"] == 0
        assert stats["inactive"]["collective"] == 0

        total_revenue = stats["total_revenue"]

        assert total_revenue == 0.0


class GetOffererHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_history"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - full history with joined data (1 query)
    expected_num_queries = 3

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            offerer = offerers_factories.UserOffererFactory().offerer
            return url_for("backoffice_web.offerer.get_history", offerer_id=offerer.id)

    def test_get_history(self, authenticated_client, pro_fraud_admin):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        action = history_factories.ActionHistoryFactory(offerer=offerer)
        history_factories.ActionHistoryFactory(
            # displayed because legit_user has fraud permission
            actionType=history_models.ActionType.FRAUD_INFO_MODIFIED,
            actionDate=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            authorUser=pro_fraud_admin,
            offerer=offerer,
            comment=None,
            extraData={
                "modified_info": {
                    "confidenceRule.confidenceLevel": {
                        "old_info": offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.name,
                        "new_info": offerers_models.OffererConfidenceLevel.WHITELIST.name,
                    },
                }
            },
        )
        history_factories.ActionHistoryFactory(offerer=offerers_factories.OffererFactory())  # other offerer

        url = url_for(self.endpoint, offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["Type"] == history_models.ActionType.COMMENT.value
        assert rows[0]["Date/Heure"].startswith(action.actionDate.strftime("Le %d/%m/%Y à "))
        assert rows[0]["Commentaire"] == action.comment
        assert rows[0]["Auteur"] == action.authorUser.full_name

        assert rows[1]["Type"] == "Fraude et Conformité"
        assert (
            rows[1]["Commentaire"]
            == "Informations modifiées : Validation des offres : Revue manuelle => Validation auto"
        )
        assert rows[1]["Auteur"] == pro_fraud_admin.full_name

    def test_get_history_with_missing_authorId(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        action = history_factories.ActionHistoryFactory(
            offerer=offerer, actionType=history_models.ActionType.OFFERER_NEW, authorUser=None
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Type"] == history_models.ActionType.OFFERER_NEW.value
        assert rows[0]["Commentaire"] == action.comment
        assert not rows[0]["Auteur"]

    def test_get_history_without_fraud_permission(self, client, read_only_bo_user):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        history_factories.ActionHistoryFactory(actionType=history_models.ActionType.COMMENT, offerer=offerer)
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.FRAUD_INFO_MODIFIED, offerer=offerer
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        auth_client = client.with_bo_session_auth(read_only_bo_user)
        with assert_num_queries(self.expected_num_queries):
            response = auth_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Type"] == "Commentaire interne"

    def test_no_action(self, authenticated_client, offerer):
        url = url_for(self.endpoint, offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    def test_action_name_depends_on_type(self, authenticated_client, offerer):
        admin_user = users_factories.AdminFactory()
        user_offerer_1 = offerers_factories.UserOffererFactory(
            offerer=offerer, user__firstName="Vincent", user__lastName="Auriol"
        )
        user_offerer_2 = offerers_factories.UserOffererFactory(offerer=offerer)
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 13, 1),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=admin_user,
            user=user_offerer_1.user,
            offerer=offerer,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 5, 13, 1),
            actionType=history_models.ActionType.USER_OFFERER_NEW,
            authorUser=admin_user,
            user=user_offerer_2.user,
            offerer=offerer,
            comment=None,
        )
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        assert user_offerer_1.user.full_name not in content
        assert user_offerer_2.user.full_name in content

    def test_get_full_sorted_history(self, authenticated_client, legit_user):
        admin = users_factories.UserFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 13, 1),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=user_offerer.user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 4, 14, 2),
            actionType=history_models.ActionType.OFFERER_PENDING,
            authorUser=admin,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment="Documents complémentaires demandés",
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 5, 15, 3),
            actionType=history_models.ActionType.COMMENT,
            authorUser=legit_user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment="Documents reçus",
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 6, 16, 4),
            actionType=history_models.ActionType.OFFERER_VALIDATED,
            authorUser=admin,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 6, 17, 5),
            actionType=history_models.ActionType.COMMENT,
            authorUser=admin,
            user=user_offerer.user,
            offerer=offerers_factories.UserOffererFactory(user=user_offerer.user).offerer,
            comment="Commentaire sur une autre structure",
        )

        url = url_for(self.endpoint, offerer_id=user_offerer.offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert rows[0]["Type"] == "Structure validée"
        assert rows[0]["Date/Heure"] == "Le 06/10/2022 à 18h04"  # CET (Paris time)
        assert rows[0]["Commentaire"] == ""
        assert rows[0]["Auteur"] == admin.full_name

        assert rows[1]["Type"] == "Commentaire interne"
        assert rows[1]["Date/Heure"] == "Le 05/10/2022 à 17h03"  # CET (Paris time)
        assert rows[1]["Commentaire"] == "Documents reçus"
        assert rows[1]["Auteur"] == legit_user.full_name

        assert rows[2]["Type"] == "Structure mise en attente"
        assert rows[2]["Date/Heure"] == "Le 04/10/2022 à 16h02"  # CET (Paris time)
        assert rows[2]["Commentaire"] == "Documents complémentaires demandés"
        assert rows[2]["Auteur"] == admin.full_name

        assert rows[3]["Type"] == "Nouvelle structure"
        assert rows[3]["Date/Heure"] == "Le 03/10/2022 à 15h01"  # CET (Paris time)
        assert rows[3]["Commentaire"] == ""
        assert rows[3]["Auteur"] == user_offerer.user.full_name


class GetOffererUsersTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_pro_users"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - users with joined data (1 query)
    # - offerer_invitation data
    # - retrieve Feature Flags
    expected_num_queries = 5

    def test_get_pro_users(self, authenticated_client, offerer):
        uo1 = offerers_factories.UserOffererFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName=None, lastName=None)
        )
        uo2 = offerers_factories.UserOffererFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName="Jean", lastName="Bon")
        )
        uo3 = offerers_factories.NotValidatedUserOffererFactory(offerer=offerer)
        uo4 = offerers_factories.UserOffererFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName="Hang", lastName="Man", isActive=False)
        )

        offerers_factories.UserOffererFactory()

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert rows[0]["ID"] == str(uo1.user.id)
        assert rows[0]["Statut"] == "Validé"
        assert rows[0]["Prénom / Nom"] == uo1.user.full_name
        assert rows[0]["Email"] == uo1.user.email
        assert rows[0]["Invitation"] == ""
        assert "Connect as" not in rows[0]

        assert rows[1]["ID"] == str(uo2.user.id)
        assert rows[1]["Statut"] == "Validé"
        assert rows[1]["Prénom / Nom"] == uo2.user.full_name
        assert rows[1]["Email"] == uo2.user.email
        assert rows[1]["Invitation"] == ""
        assert "Connect as" not in rows[1]

        assert rows[2]["ID"] == str(uo3.user.id)
        assert rows[2]["Statut"] == "Nouveau"
        assert rows[2]["Prénom / Nom"] == uo3.user.full_name
        assert rows[2]["Email"] == uo3.user.email
        assert rows[2]["Invitation"] == ""
        assert "Connect as" not in rows[2]

        assert rows[3]["ID"] == str(uo4.user.id)
        assert rows[3]["Statut"] == "Validé Suspendu"
        assert rows[3]["Prénom / Nom"] == uo4.user.full_name
        assert rows[3]["Email"] == uo4.user.email
        assert rows[3]["Invitation"] == ""
        assert "Connect as" not in rows[3]

    @override_features(WIP_CONNECT_AS=True)
    @pytest.mark.parametrize(
        "roles,active,result",
        [
            ([users_models.UserRole.PRO], False, False),
            ([users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED], True, False),
            ([users_models.UserRole.PRO, users_models.UserRole.ADMIN], True, False),
            ([users_models.UserRole.PRO], True, True),
        ],
    )
    def test_connect_as_available_for_pro(self, authenticated_client, offerer, roles, active, result):
        user = users_factories.ProFactory(roles=roles, isActive=active)
        offerers_factories.UserOffererFactory(
            offerer=offerer,
            user=user,
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert (url_for("backoffice_web.pro_user.connect_as", user_id=user.id).encode() in response.data) == result

    def test_get_pro_users_with_one_offerer_invitation_without_user_account(self, authenticated_client, offerer):
        uo1 = offerers_factories.UserOffererFactory(offerer=offerer)
        guest = offerers_factories.OffererInvitationFactory(offerer=offerer)

        # other invitation on another offerer for test not conflict
        offerers_factories.OffererInvitationFactory()

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["ID"] == str(uo1.user.id)
        assert rows[0]["Statut"] == "Validé"
        assert rows[0]["Prénom / Nom"] == uo1.user.full_name
        assert rows[0]["Email"] == uo1.user.email
        assert rows[0]["Invitation"] == ""

        assert rows[1]["ID"] == ""
        assert rows[1]["Statut"] == "Invité"
        assert rows[1]["Prénom / Nom"] == ""
        assert rows[1]["Email"] == guest.email
        assert rows[1]["Invitation"].startswith("Invité le ")
        assert rows[1]["Invitation"].endswith("par " + guest.user.full_name)

    def test_get_pro_users_with_one_offerer_invitation_with_validated_user_account(self, authenticated_client, offerer):
        uo1 = offerers_factories.UserOffererFactory(offerer=offerer)
        pro = users_factories.ProFactory()
        uo2 = offerers_factories.UserOffererFactory(offerer=offerer, user=pro)
        guest1 = offerers_factories.OffererInvitationFactory(
            user=users_factories.ProFactory(firstName="Pro1", lastName="lastName"), offerer=offerer, email=pro.email
        )
        guest2 = offerers_factories.OffererInvitationFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName="Jean", lastName="SansPeur")
        )

        # other invitation on another offerer for test not conflict
        offerers_factories.OffererInvitationFactory()

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3

        assert rows[0]["ID"] == str(uo1.user.id)
        assert rows[0]["Statut"] == "Validé"
        assert rows[0]["Prénom / Nom"] == uo1.user.full_name
        assert rows[0]["Email"] == uo1.user.email
        assert rows[0]["Invitation"] == ""

        assert rows[1]["ID"] == str(uo2.user.id)
        assert rows[1]["Statut"] == "Validé"
        assert rows[1]["Prénom / Nom"] == uo2.user.full_name
        assert rows[1]["Email"] == uo2.user.email
        assert rows[1]["Invitation"].startswith("Invité le ")
        assert rows[1]["Invitation"].endswith("par " + guest1.user.full_name)

        assert rows[2]["ID"] == ""
        assert rows[2]["Statut"] == "Invité"
        assert rows[2]["Prénom / Nom"] == ""
        assert rows[2]["Email"] == guest2.email
        assert rows[2]["Invitation"].startswith("Invité le ")
        assert rows[2]["Invitation"].endswith("par " + guest2.user.full_name)

    def test_get_pro_users_with_one_offerer_invitation_with_not_validated_user_account(
        self, authenticated_client, offerer
    ):
        pro = users_factories.ProFactory()
        guest2 = offerers_factories.OffererInvitationFactory(offerer=offerer, user=pro, email=pro.email)
        # no UserOfferer when the user has not validated their user account

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1

        assert rows[0]["ID"] == ""
        assert rows[0]["Statut"] == "Invité"
        assert rows[0]["Prénom / Nom"] == ""
        assert rows[0]["Email"] == guest2.email
        assert rows[0]["Invitation"].startswith("Invité le ")
        assert rows[0]["Invitation"].endswith("par " + guest2.user.full_name)

    def test_add_pro_user_choices(self, authenticated_client, legit_user, offerer):
        user1 = offerers_factories.UserOffererFactory(offerer=offerer)
        user2 = users_factories.UserFactory(firstName="Raymond", lastName="Poincaré")
        user3 = users_factories.ProFactory(firstName="Paul", lastName="Deschanel")
        users_factories.UserFactory(firstName="Alexandre", lastName="Millerand")
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_PENDING,
            authorUser=legit_user,
            user=user1.user,
            offerer=offerer,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED,
            authorUser=legit_user,
            user=user2,
            offerer=offerer,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED,
            authorUser=legit_user,
            user=user3,
            offerer=offerer,
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        select = parsed_html.find("select", attrs={"name": "pro_user_id"})
        options = select.find_all("option")
        assert [option["value"] for option in options] == ["", str(user3.id), str(user2.id)]

    def test_user_offerer_details_tab_with_new_nav_tags(self, authenticated_client, offerer):
        user_with_new_nav = users_factories.ProFactory()
        users_factories.UserProNewNavStateFactory(user=user_with_new_nav)
        offerers_factories.UserOffererFactory(user=user_with_new_nav, offerer=offerer)

        user_with_old_nav = users_factories.ProFactory()
        users_factories.UserProNewNavStateFactory(user=user_with_old_nav, eligibilityDate=None, newNavDate=None)
        offerers_factories.UserOffererFactory(user=user_with_old_nav, offerer=offerer)

        eligible_user_with_inactivated_new_nav = users_factories.ProFactory()
        users_factories.UserProNewNavStateFactory(
            user=eligible_user_with_inactivated_new_nav, eligibilityDate=datetime.datetime.utcnow(), newNavDate=None
        )
        offerers_factories.UserOffererFactory(user=eligible_user_with_inactivated_new_nav, offerer=offerer)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert len(rows) == 3

        assert rows[0]["ID"] == str(user_with_new_nav.id)
        assert rows[0]["Statut"] == "Validé"
        assert rows[0]["Interface"] == "Nouvelle interface"
        assert rows[0]["Prénom / Nom"] == user_with_new_nav.full_name
        assert rows[0]["Email"] == user_with_new_nav.email

        assert rows[1]["ID"] == str(user_with_old_nav.id)
        assert rows[1]["Statut"] == "Validé"
        assert rows[1]["Interface"] == "Ancienne interface"
        assert rows[1]["Prénom / Nom"] == user_with_old_nav.full_name
        assert rows[1]["Email"] == user_with_old_nav.email

        assert rows[2]["ID"] == str(eligible_user_with_inactivated_new_nav.id)
        assert rows[2]["Statut"] == "Validé"
        assert rows[2]["Interface"] == "Ancienne interface"
        assert rows[2]["Prénom / Nom"] == eligible_user_with_inactivated_new_nav.full_name
        assert rows[2]["Email"] == eligible_user_with_inactivated_new_nav.email


class GetDeleteOffererAttachmentFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_delete_user_offerer_form"
    endpoint_kwargs = {"offerer_id": 1, "user_offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_get_delete_offerer_attachment_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        url = url_for(self.endpoint, offerer_id=user_offerer.offerer.id, user_offerer_id=user_offerer.id)
        with assert_num_queries(3):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class DeleteOffererAttachmentTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.delete_user_offerer"
    endpoint_kwargs = {"offerer_id": 1, "user_offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_delete_offerer_attachment(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=user_offerer.offerer.id, user_offerer_id=user_offerer.id
        )

        assert response.status_code == 303

        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 1
        assert users_offerers[0].validationStatus == ValidationStatus.DELETED

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_DELETED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

        assert len(mails_testing.outbox) == 0

    def test_delete_offerer_returns_404_if_offerer_attachment_is_not_found(self, authenticated_client, offerer):
        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, user_offerer_id=42)
        assert response.status_code == 404


class GetOffererVenuesTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_managed_venues"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - venues with joined data (1 query)
    expected_num_queries = 3

    def test_get_managed_venues(self, authenticated_client, offerer):
        now = datetime.datetime.utcnow()
        other_offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(
            name="Deuxième", publicName="Second", managingOfferer=offerer, isPermanent=True
        )
        old_bank_account = finance_factories.BankAccountFactory(offerer=offerer, label="Ancien compte")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer, label="Compte actuel")
        offerers_factories.VenueBankAccountLinkFactory(
            bankAccount=old_bank_account,
            venue=venue_1,
            timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)],
        )
        offerers_factories.VenueBankAccountLinkFactory(
            bankAccount=bank_account, venue=venue_1, timespan=[now - datetime.timedelta(days=3), None]
        )

        venue_2 = offerers_factories.VenueFactory(name="Premier", publicName=None, managingOfferer=offerer)
        offerers_factories.VenueRegistrationFactory(venue=venue_2)
        educational_factories.CollectiveDmsApplicationFactory(venue=venue_2, application=35)
        offerers_factories.VenueFactory(managingOfferer=other_offerer)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["ID"] == str(venue_2.id)
        assert rows[0]["SIRET"] == venue_2.siret
        assert rows[0]["Permanent"] == ""
        assert rows[0]["Nom"] == venue_2.name
        assert rows[0]["Activité principale"] == venue_2.venueTypeCode.value
        assert not rows[0].get("Type de lieu")
        assert rows[0]["Présence web"] == "https://example.com https://pass.culture.fr"
        assert rows[0]["Offres cibles"] == "Indiv. et coll."
        assert rows[0]["Compte bancaire associé"] == ""

        assert rows[1]["ID"] == str(venue_1.id)
        assert rows[1]["SIRET"] == venue_1.siret
        assert rows[1]["Permanent"] == "Lieu permanent"
        assert rows[1]["Nom"] == venue_1.publicName
        assert rows[1]["Activité principale"] == venue_1.venueTypeCode.value
        assert not rows[0].get("Type de lieu")
        assert rows[1]["Présence web"] == ""
        assert rows[1]["Offres cibles"] == ""
        assert rows[1]["Compte bancaire associé"] == "Compte actuel"


class GetOffererAddressesTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_offerer_addresses"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - addresses (1 query)
    expected_num_queries = 3

    def test_get_offerer_addresses(self, authenticated_client, offerer):
        offerers_factories.OffererAddressFactory(
            offerer=offerer, label="Première adresse", address__street="3 Bd Poissonnière"
        )
        offerers_factories.OffererAddressFactory(
            offerer=offerer, label="Deuxième adresse", address__street="5 Bd Poissonnière"
        )
        offerers_factories.OffererAddressFactory()  # other offerer

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["Intitulé"] == "Deuxième adresse"
        assert rows[0]["Adresse"] == "5 Bd Poissonnière 75002 Paris"
        assert rows[0]["Localisation"] == "48.87055, 2.34765"

        assert rows[1]["Intitulé"] == "Première adresse"
        assert rows[1]["Adresse"] == "3 Bd Poissonnière 75002 Paris"
        assert rows[1]["Localisation"] == "48.87055, 2.34765"


class GetOffererCollectiveDmsApplicationsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_collective_dms_applications"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - dms applications with joined data (1 query)
    expected_num_queries = 3

    def test_get_collective_dms_applications(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue_2 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900002")
        educational_factories.CollectiveDmsApplicationFactory(
            venue=venue_1,
            application=35,
            state="refuse",
            depositDate=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        educational_factories.CollectiveDmsApplicationFactory(
            venue=venue_2, application=36, depositDate=datetime.datetime.utcnow() - datetime.timedelta(days=2)
        )
        educational_factories.CollectiveDmsApplicationFactory(
            venue=venue_1,
            application=37,
            state="accepte",
            depositDate=datetime.datetime.utcnow() - datetime.timedelta(days=3),
        )
        educational_factories.CollectiveDmsApplicationWithNoVenueFactory(
            siret="12345678900003",
            application=38,
            depositDate=datetime.datetime.utcnow() - datetime.timedelta(days=4),
        )
        educational_factories.CollectiveDmsApplicationFactory(application=39)
        educational_factories.CollectiveDmsApplicationWithNoVenueFactory(siret="12345123456789")
        educational_factories.CollectiveDmsApplicationWithNoVenueFactory(siret="12345678000009")

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert rows[0]["ID"] == "35"
        assert rows[0]["Date de dépôt"] == (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime(
            "%d/%m/%Y"
        )
        assert rows[0]["État"] == "Refusé"
        assert rows[0]["Date de dernière mise à jour"] == (
            datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[0]["Lieu"] == venue_1.name
        assert rows[0]["SIRET"] == venue_1.siret

        assert rows[1]["ID"] == "36"
        assert rows[1]["Date de dépôt"] == (datetime.datetime.utcnow() - datetime.timedelta(days=2)).strftime(
            "%d/%m/%Y"
        )
        assert rows[1]["État"] == "En construction"
        assert rows[1]["Date de dernière mise à jour"] == (
            datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[1]["Lieu"] == venue_2.name
        assert rows[1]["SIRET"] == venue_2.siret

        assert rows[2]["ID"] == "37"
        assert rows[2]["Date de dépôt"] == (datetime.datetime.utcnow() - datetime.timedelta(days=3)).strftime(
            "%d/%m/%Y"
        )
        assert rows[2]["État"] == "Accepté"
        assert rows[2]["Date de dernière mise à jour"] == (
            datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[2]["Lieu"] == venue_1.name
        assert rows[2]["SIRET"] == venue_1.siret

        assert rows[3]["ID"] == "38"
        assert rows[3]["Date de dépôt"] == (datetime.datetime.utcnow() - datetime.timedelta(days=4)).strftime(
            "%d/%m/%Y"
        )
        assert rows[3]["État"] == "En construction"
        assert rows[3]["Date de dernière mise à jour"] == (
            datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[3]["Lieu"] == ""
        assert rows[3]["SIRET"] == "12345678900003"

    def test_offerer_with_no_dms_adage_application(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0


class GetOffererBankAccountTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_bank_accounts"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - bank accounts (1 query)
    expected_num_queries = 3

    def test_get_bank_accounts(self, authenticated_client, offerer):
        offerer = offerers_factories.OffererFactory()
        bank1 = finance_factories.BankAccountFactory(
            offerer=offerer,
            label="Premier compte",
            status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        )
        bank2 = finance_factories.BankAccountFactory(
            offerer=offerer,
            label="Deuxième compte",
            status=finance_models.BankAccountApplicationStatus.ON_GOING,
        )
        finance_factories.BankAccountFactory()  # not listed

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["ID"] == str(bank2.id)
        assert rows[0]["Intitulé du compte bancaire"] == bank2.label
        assert rows[0]["Statut du dossier DMS CB"] == "En instruction"

        assert rows[1]["ID"] == str(bank1.id)
        assert rows[1]["Intitulé du compte bancaire"] == bank1.label
        assert rows[1]["Statut du dossier DMS CB"] == "Accepté"


class CommentOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.comment_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_add_comment(self, authenticated_client, legit_user, offerer):
        comment = "Code APE non éligible"
        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form={"comment": comment})

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offerer.get", offerer_id=offerer.id, _external=True)
        assert response.location == expected_url

        db.session.refresh(offerer)
        assert len(offerer.action_history) == 1
        action = offerer.action_history[0]
        assert action.actionType == history_models.ActionType.COMMENT
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == comment

    def test_add_invalid_comment(self, authenticated_client, offerer):
        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form={"comment": ""})

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Les données envoyées comportent des erreurs" in redirected_response.data.decode("utf8")


class ListOfferersToValidateTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.list_offerers_to_validate"
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class ListOfferersToBeValidatedTest:
        # - session + authenticated user (2 queries)
        # - validation status count (1 query)
        # - offerer tags filter (1 query)
        expected_num_queries_when_no_query = 4
        # - get results (1 query)
        # - get results count (1 query)
        expected_num_queries = expected_num_queries_when_no_query + 2

        @pytest.mark.parametrize(
            "row_key,sort,order",
            [
                ("Date de la demande", None, None),
                ("Date de la demande", "", ""),
                ("Date de la demande", "dateCreated", "asc"),
                ("Date de la demande", "dateCreated", "desc"),
            ],
        )
        def test_list_offerers_to_be_validated(self, authenticated_client, row_key, sort, order):
            _validated_offerers = [offerers_factories.UserOffererFactory().offerer for _ in range(3)]
            to_be_validated_offerers = []
            for _ in range(4):
                user_offerer = offerers_factories.UserNotValidatedOffererFactory()
                history_factories.ActionHistoryFactory(
                    actionType=history_models.ActionType.OFFERER_NEW,
                    authorUser=users_factories.AdminFactory(),
                    offerer=user_offerer.offerer,
                    user=user_offerer.user,
                    comment=None,
                )
                to_be_validated_offerers.append(user_offerer.offerer)

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", order=order, sort=sort)
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            # Without sort, table is ordered by dateCreated desc
            to_be_validated_offerers.sort(
                key=attrgetter(sort or "dateCreated"), reverse=(order == "desc") if sort else True
            )
            assert [row[row_key] for row in rows] == [
                offerer.dateCreated.strftime("%d/%m/%Y") for offerer in to_be_validated_offerers
            ]

        def _test_payload_content(self, auth_client, top_acteur_column_expected):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
                offerer__validationStatus=ValidationStatus.NEW,
                user__phoneNumber="+33610203040",
            )
            tag = offerers_factories.OffererTagFactory(label="Magic Tag")
            category = offerers_models.OffererTagCategory.query.filter(
                offerers_models.OffererTagCategory.name == "homologation"
            ).one()
            offerers_factories.OffererTagCategoryMappingFactory(tagId=tag.id, categoryId=category.id)
            offerers_factories.OffererTagMappingFactory(tagId=tag.id, offererId=user_offerer.offerer.id)

            other_category_tag = offerers_factories.OffererTagFactory(label="Festival")
            other_category = offerers_factories.OffererTagCategoryFactory(name="spectacle", label="Spectacles")
            offerers_factories.OffererTagCategoryMappingFactory(
                tagId=other_category_tag.id, categoryId=other_category.id
            )
            offerers_factories.OffererTagMappingFactory(tagId=other_category_tag.id, offererId=user_offerer.offerer.id)

            commenter = users_factories.AdminFactory(firstName="Inspecteur", lastName="Validateur")
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 12, 0),
                actionType=history_models.ActionType.OFFERER_NEW,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                user=user_offerer.user,
                comment=None,
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 13, 1),
                actionType=history_models.ActionType.COMMENT,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                comment="Bla blabla",
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 14, 2),
                actionType=history_models.ActionType.OFFERER_PENDING,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                comment="Houlala",
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 15, 3),
                actionType=history_models.ActionType.USER_OFFERER_VALIDATED,
                authorUser=commenter,
                offerer=user_offerer.offerer,
                user=user_offerer.user,
                comment=None,
            )

            with assert_num_queries(self.expected_num_queries):
                response = auth_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Nom de la structure"] == user_offerer.offerer.name
            assert rows[0]["État"] == "Nouvelle"
            if top_acteur_column_expected:
                assert rows[0]["Top Acteur"] == ""  # no text
            else:
                assert "Top Acteur" not in rows[0]
            assert tag.label in rows[0]["Tags structure"]
            assert other_category_tag.label in rows[0]["Tags structure"]
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Dernier commentaire"] == "Houlala"
            assert rows[0]["SIREN"] == user_offerer.offerer.siren
            assert rows[0]["Email"] == user_offerer.user.email
            assert rows[0]["Responsable Structure"] == user_offerer.user.full_name
            assert rows[0]["Ville"] == user_offerer.offerer.city

            dms_adage_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")
            assert dms_adage_data == []

        def test_payload_content(self, authenticated_client, top_acteur_tag):
            self._test_payload_content(authenticated_client, True)

        def test_payload_content_as_read_only_user(self, client, read_only_bo_user, offerer_tags):
            auth_client = client.with_bo_session_auth(read_only_bo_user)
            self._test_payload_content(auth_client, False)

        def test_payload_content_no_action(self, authenticated_client):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
            )

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Nom de la structure"] == user_offerer.offerer.name
            assert rows[0]["État"] == "Nouvelle"
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Dernier commentaire"] == ""

        def test_dms_adage_additional_data(self, authenticated_client):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
            educational_factories.CollectiveDmsApplicationFactory(venue=venue, state="accepte")
            other_venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
            educational_factories.CollectiveDmsApplicationFactory(venue=other_venue, state="accepte")

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)

            dms_adage_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
            assert f"Nom : {venue.name}" in dms_adage_data
            assert f"SIRET : {venue.siret}" in dms_adage_data
            assert "Statut du dossier DMS ADAGE : Accepté" in dms_adage_data

        @pytest.mark.parametrize(
            "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
            (
                (31, {"per_page": 10}, 4, 1, 10),
                (31, {"per_page": 10, "page": 1}, 4, 1, 10),
                (31, {"per_page": 10, "page": 3}, 4, 3, 10),
                (31, {"per_page": 10, "page": 4}, 4, 4, 1),
                (20, {"per_page": 10, "page": 1}, 2, 1, 10),
                (27, {"page": 1}, 1, 1, 27),
                (10, {"per_page": 25, "page": 1}, 1, 1, 10),
                (1, {"per_page": None, "page": 1}, 1, 1, 1),
                (1, {"per_page": "", "page": 1}, 1, 1, 1),  # ensure that it does not crash (fallbacks to default)
            ),
        )
        def test_list_pagination(
            self,
            authenticated_client,
            total_items,
            pagination_config,
            expected_total_pages,
            expected_page,
            expected_items,
        ):
            for _ in range(total_items):
                offerers_factories.UserNotValidatedOffererFactory()

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", **pagination_config)
                )
                assert response.status_code == 200

            assert html_parser.count_table_rows(response.data) == expected_items
            assert html_parser.extract_pagination_info(response.data) == (
                expected_page,
                expected_total_pages,
                total_items,
            )

        @pytest.mark.parametrize(
            "region_filter, expected_offerer_names",
            (
                (["Bretagne"], {"A", "B", "D", "E"}),
                (["Normandie", "Pays de la Loire"], {"C", "F"}),
            ),
        )
        def test_list_filtering_by_region(
            self, authenticated_client, region_filter, expected_offerer_names, offerers_to_be_validated
        ):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        regions=region_filter,
                        status=["NEW", "PENDING"],
                    )
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == expected_offerer_names

        @pytest.mark.parametrize(
            "tag_filter, expected_offerer_names",
            (
                (["Top acteur"], {"B", "E", "F"}),
                (["Collectivité"], {"C", "E"}),
                (["Établissement public"], {"D", "F"}),
                (["Établissement public", "Top acteur"], {"F"}),
                (["Festival"], {"D", "F"}),
            ),
        )
        def test_list_filtering_by_tags(
            self, authenticated_client, tag_filter, expected_offerer_names, offerers_to_be_validated
        ):
            tags = (
                offerers_models.OffererTag.query.filter(offerers_models.OffererTag.label.in_(tag_filter))
                .with_entities(offerers_models.OffererTag.id)
                .all()
            )
            tags_ids = [_id for _id, in tags]

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate", tags=tags_ids, status=["NEW", "PENDING"]
                    )
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == expected_offerer_names

        def test_list_filtering_by_date(self, authenticated_client):
            # Created before requested range, excluded from results:
            offerers_factories.UserNotValidatedOffererFactory(offerer__dateCreated=datetime.datetime(2022, 11, 4, 4))
            # Created within requested range: Nov 4 23:45 UTC is Nov 5 00:45 CET
            user_offerer_2 = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 11, 4, 23, 45)
            )
            # Within requested range:
            user_offerer_3 = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 11, 6, 5)
            )
            # Excluded from results: Nov 8 23:15 UTC is Now 9 00:15 CET
            offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 11, 8, 23, 15)
            )
            # Excluded from results:
            offerers_factories.UserNotValidatedOffererFactory(offerer__dateCreated=datetime.datetime(2022, 11, 10, 7))

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        from_date="2022-11-05",
                        to_date="2022-11-08",
                    )
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert [int(row["ID"]) for row in rows] == [uo.offerer.id for uo in (user_offerer_3, user_offerer_2)]

        def test_list_filtering_by_invalid_date(self, authenticated_client):
            with assert_num_queries(self.expected_num_queries_when_no_query):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        from_date="05/11/2022",
                    )
                )
                assert response.status_code == 400

            assert "Date invalide" in response.data.decode("utf-8")

        @pytest.mark.parametrize("search", ["123004004", "123 004 004", "  123004004 ", "123004004\n"])
        def test_list_search_by_siren(self, authenticated_client, offerers_to_be_validated, search):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=search, status="PENDING")
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"D"}

        @pytest.mark.parametrize("postal_code", ["35400", "35 400"])
        def test_list_search_by_postal_code(self, authenticated_client, offerers_to_be_validated, postal_code):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=postal_code)
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"E"}

        def test_list_search_by_department_code(self, authenticated_client, offerers_to_be_validated):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q="35")
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"A", "E"}

        def test_list_search_by_city(self, authenticated_client, offerers_to_be_validated):
            # Ensure that outerjoin does not cause too many rows returned
            offerers_factories.UserOffererFactory.create_batch(3, offerer=offerers_to_be_validated[1])

            # Search "quimper" => results include "Quimper" and "Quimperlé"
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q="quimper", status="PENDING")
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"B", "D"}
            assert html_parser.extract_pagination_info(response.data) == (1, 1, 2)

        @pytest.mark.parametrize("search", ["1", "1234", "123456", "1234567", "12345678", "12345678912345", "  1234"])
        def test_list_search_by_invalid_number_of_digits(self, authenticated_client, search):
            with assert_num_queries(self.expected_num_queries_when_no_query):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=search)
                )
                assert response.status_code == 400

            assert (
                "Le nombre de chiffres ne correspond pas à un SIREN, code postal, département ou ID DMS CB"
                in response.data.decode("utf-8")
            )

        def test_list_search_by_email(self, authenticated_client, offerers_to_be_validated):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate", q="sadi@example.com", status="PENDING"
                    )
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"B"}

        def test_list_search_by_user_name(self, authenticated_client, offerers_to_be_validated):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q="Felix faure")
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"C"}

        @pytest.mark.parametrize(
            "search_filter, expected_offerer_names",
            (
                ("cinema de la plage", {"Cinéma de la Plage"}),
                ("cinéma", {"Cinéma de la Petite Plage", "Cinéma de la Plage", "Cinéma du Centre"}),
                ("Plage", {"Librairie de la Plage", "Cinéma de la Petite Plage", "Cinéma de la Plage"}),
                ("Librairie du Centre", set()),
            ),
        )
        def test_list_search_by_name(self, authenticated_client, search_filter, expected_offerer_names):
            for name in (
                "Librairie de la Plage",
                "Cinéma de la Petite Plage",
                "Cinéma du Centre",
                "Cinéma de la Plage",
            ):
                offerers_factories.NotValidatedOffererFactory(name=name)

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=search_filter)
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == expected_offerer_names

        @pytest.mark.parametrize(
            "status_filter, expected_status, expected_offerer_names",
            (
                ("NEW", 200, {"A", "C", "E"}),
                ("PENDING", 200, {"B", "D", "F"}),
                (["NEW", "PENDING"], 200, {"A", "B", "C", "D", "E", "F"}),
                ("VALIDATED", 200, {"G"}),
                ("REJECTED", 200, {"H"}),
                (None, 200, {"C", "A", "E"}),  # status NEW as default
                ("OTHER", 400, set()),  # unknown value
                (["REJECTED", "OTHER"], 400, set()),
            ),
        )
        def test_list_filtering_by_status(
            self, authenticated_client, status_filter, expected_status, expected_offerer_names, offerers_to_be_validated
        ):
            expected_num_queries = (
                self.expected_num_queries if expected_status == 200 else self.expected_num_queries - 2
            )
            with assert_num_queries(expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", status=status_filter)
                )
                assert response.status_code == expected_status

            if expected_status == 200:
                rows = html_parser.extract_table_rows(response.data)
                assert {row["Nom de la structure"] for row in rows} == expected_offerer_names
            else:
                assert html_parser.count_table_rows(response.data) == 0

        def test_list_filtering_by_instructor(self, authenticated_client, offerers_to_be_validated):
            _, pending1, _, pending2, _, pending3 = offerers_to_be_validated

            instructor = users_factories.AdminFactory()
            instructor_id = instructor.id
            other_instructor = users_factories.AdminFactory()

            history_factories.ActionHistoryFactory(
                actionType=history_models.ActionType.OFFERER_PENDING,
                authorUser=instructor,
                offerer=pending1,
            )

            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
                actionType=history_models.ActionType.OFFERER_PENDING,
                authorUser=other_instructor,
                offerer=pending2,
            )
            history_factories.ActionHistoryFactory(
                actionType=history_models.ActionType.USER_OFFERER_PENDING,
                authorUser=instructor,
                user=users_factories.NonAttachedProFactory(),
                offerer=pending2,
            )

            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
                actionType=history_models.ActionType.OFFERER_PENDING,
                authorUser=instructor,
                offerer=pending3,
            )
            history_factories.ActionHistoryFactory(
                actionType=history_models.ActionType.OFFERER_PENDING,
                authorUser=other_instructor,
                offerer=pending3,
            )

            # +1 query to fill in instructor filter
            with assert_num_queries(self.expected_num_queries + 1):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        status="PENDING",
                        instructors=instructor_id,
                    )
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {int(row["ID"]) for row in rows} == {pending1.id}

        @pytest.mark.parametrize(
            "dms_status_filter, expected_status, expected_offerer_names",
            (
                ("accepted", 200, {"A", "E"}),
                ("on_going", 200, {"B"}),
                (["accepted", "on_going"], 200, {"A", "B", "E"}),
                ("draft", 200, {"C"}),
                ("without_continuation", 200, {"D"}),
                ("refused", 200, {"A"}),
                (None, 200, {"A", "B", "C", "D", "E", "F"}),  # same as default
                ("OTHER", 400, set()),  # unknown value
                (["accepted", "OTHER"], 400, set()),
            ),
        )
        def test_list_filtering_by_dms_adage_status(
            self,
            authenticated_client,
            dms_status_filter,
            expected_status,
            expected_offerer_names,
            offerers_to_be_validated,
        ):
            expected_num_queries = (
                self.expected_num_queries if expected_status == 200 else self.expected_num_queries - 2
            )
            with assert_num_queries(expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        dms_adage_status=dms_status_filter,
                        status=["NEW", "PENDING"],
                    )
                )
                assert response.status_code == expected_status

            if expected_status == 200:
                rows = html_parser.extract_table_rows(response.data)
                assert {row["Nom de la structure"] for row in rows} == expected_offerer_names
            else:
                assert html_parser.count_table_rows(response.data) == 0

        @pytest.mark.parametrize(
            "query", ["123a456b789c", "123A456B789C", "PRO-123a456b789c", "124578235689", "PRO-124578235689"]
        )
        def test_list_filtering_by_dms_token(self, authenticated_client, query, offerers_to_be_validated):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, dmsToken="123a456b789c")
            offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, dmsToken="124578235689")

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=query)
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)

        @pytest.mark.parametrize(
            "query, dms_status_filter",
            (
                ("124578235689", "accepted"),
                ("PRO-124578235689", "on_going"),
                ("124578235689", None),
                (None, "accepted"),
            ),
        )
        def test_list_filtering_with_filters_using_same_joins(
            self, authenticated_client, query, dms_status_filter, offerers_to_be_validated
        ):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, dmsToken="124578235689")

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        q=query,
                        dms_adage_status=dms_status_filter,
                    )
                )
                assert response.status_code == 200

        def test_offerers_stats_are_displayed(self, authenticated_client, offerers_to_be_validated):
            offerers_factories.UserOffererFactory(offerer__validationStatus=ValidationStatus.PENDING)
            offerers_factories.UserOffererFactory(offerer__validationStatus=ValidationStatus.REJECTED)

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            cards = html_parser.extract_cards_text(response.data)
            assert "3 nouvelles structures" in cards
            assert "4 structures en attente" in cards
            assert "1 structure validée" in cards
            assert "2 structures rejetées" in cards

        def test_no_offerer(self, authenticated_client):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            cards = html_parser.extract_cards_text(response.data)
            assert "0 nouvelle structure" in cards
            assert "0 structure en attente" in cards
            assert "0 structure validée" in cards
            assert "0 structure rejetée" in cards
            assert html_parser.count_table_rows(response.data) == 0


class ValidateOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.validate_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_validate_offerer(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_id=user_offerer.offererId)

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.offerer.isValidated
        assert user_offerer.offerer.isActive
        assert user_offerer.user.has_pro_role
        assert not user_offerer.user.has_non_attached_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    def test_validate_rejected_offerer(self, legit_user, authenticated_client):
        offerer = offerers_factories.RejectedOffererFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303

        db.session.refresh(offerer)
        assert offerer.isValidated
        assert offerer.isActive

    def test_validate_offerer_returns_404_if_offerer_is_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, offerer_id=1)

        assert response.status_code == 404

    def test_cannot_validate_offerer_already_validated(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_id=user_offerer.offererId)

        assert response.status_code == 303

        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"La structure {user_offerer.offerer.name} est déjà validée"
        )


class GetRejectOffererFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_reject_offerer_form"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_get_reject_offerer_form(self, legit_user, authenticated_client):
        offerer = offerers_factories.NotValidatedOffererFactory()

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(3):  # session + current user + offerer
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class RejectOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.reject_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_reject_offerer(self, legit_user, authenticated_client):
        user = users_factories.NonAttachedProFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303

        db.session.refresh(user)
        db.session.refresh(offerer)
        db.session.refresh(user_offerer)
        assert not offerer.isValidated
        assert not offerer.isActive
        assert offerer.isRejected
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role
        assert user_offerer.validationStatus == ValidationStatus.REJECTED

        action = history_models.ActionHistory.query.filter_by(
            actionType=history_models.ActionType.OFFERER_REJECTED
        ).one()
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

        action = history_models.ActionHistory.query.filter_by(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED
        ).one()
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

    def test_reject_offerer_keep_pro_role(self, authenticated_client):
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user)  # already validated
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # deleted when rejected

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303

        db.session.refresh(user)
        db.session.refresh(offerer)
        assert offerer.isRejected
        assert user.has_pro_role
        assert not user.has_non_attached_pro_role

    def test_reject_offerer_returns_404_if_offerer_is_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, offerer_id=1)

        assert response.status_code == 404

    def test_cannot_reject_offerer_already_rejected(self, authenticated_client):
        offerer = offerers_factories.RejectedOffererFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà rejetée" in redirected_response.data.decode("utf8")

    def test_no_script_injection_in_offerer_name(self, legit_user, authenticated_client):
        offerer = offerers_factories.NotValidatedOffererFactory(name="<script>alert('coucou')</script>")

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "La structure <script>alert('coucou')</script> a été rejetée"
        )


class GetOffererPendingFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_offerer_pending_form"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    # session + current user (2 queries)
    # get current tags set for this offerer (1 query)
    # get all tags to fill in form choices (1 query)
    expected_num_queries = 4

    def test_get_offerer_pending_form(self, legit_user, authenticated_client):
        offerer = offerers_factories.NotValidatedOffererFactory()

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class SetOffererPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.set_offerer_pending"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_set_offerer_pending(self, legit_user, authenticated_client, offerer_tags):
        non_homologation_tag = offerers_factories.OffererTagFactory(name="Tag conservé")
        offerer = offerers_factories.NotValidatedOffererFactory(
            tags=[non_homologation_tag, offerer_tags[0], offerer_tags[1]]
        )

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"comment": "En attente de documents", "tags": [offerer_tags[0].id, offerer_tags[2].id]},
        )

        assert response.status_code == 303

        db.session.refresh(offerer)
        assert not offerer.isValidated
        assert offerer.isActive
        assert offerer.validationStatus == ValidationStatus.PENDING
        assert set(offerer.tags) == {non_homologation_tag, offerer_tags[0], offerer_tags[2]}
        action = history_models.ActionHistory.query.one()

        assert action.actionType == history_models.ActionType.OFFERER_PENDING
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "En attente de documents"
        assert action.extraData == {
            "modified_info": {
                "tags": {"old_info": offerer_tags[1].label, "new_info": offerer_tags[2].label},
            }
        }

    def test_set_offerer_pending_keep_pro_role(self, authenticated_client):
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user)  # already validated
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # deleted when rejected

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303

        db.session.refresh(user)
        db.session.refresh(offerer)
        assert offerer.isPending
        assert user.has_pro_role
        assert not user.has_non_attached_pro_role

    def test_set_offerer_pending_remove_pro_role(self, authenticated_client):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()  # validated offerer
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # with validated attachment
        offerers_factories.UserNotValidatedOffererFactory(user=user)  # other pending offerer validation
        offerers_factories.NotValidatedUserOffererFactory(user=user)  # other pending attachment

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303

        db.session.refresh(user)
        db.session.refresh(offerer)
        assert offerer.isPending
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

    def test_set_offerer_pending_returns_404_if_offerer_is_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, offerer_id=1, form={"comment": "Questionnaire"})
        assert response.status_code == 404


class ToggleTopActorTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.toggle_top_actor"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_toggle_is_top_actor(self, authenticated_client, top_acteur_tag):
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form={"is_top_actor": "on"})

        assert response.status_code == 303
        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == top_acteur_tag.id
        assert offerer_mappings[0].offererId == offerer.id

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303
        assert offerers_models.OffererTagMapping.query.count() == 0

    def test_toggle_is_top_actor_twice_true(self, authenticated_client, top_acteur_tag):
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer

        for _ in range(2):
            response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form={"is_top_actor": "on"})
            assert response.status_code == 303

        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == top_acteur_tag.id
        assert offerer_mappings[0].offererId == offerer.id

    def test_toggle_top_actor_returns_404_if_offerer_is_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, offerer_id=1, form={"is_top_actor": "on"})
        assert response.status_code == 404


class ListUserOffererToValidateTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.list_offerers_attachments_to_validate"
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (2 queries)
    # - offerer tags filter (1 query)
    expected_num_queries_when_no_query = 3
    # - get results (1 query)
    # - get results count (1 query)
    expected_num_queries = expected_num_queries_when_no_query + 2

    @pytest.mark.parametrize(
        "row_key,sort,order",
        [
            ("ID Compte pro", None, None),
            ("ID Compte pro", "id", "asc"),
            ("ID Compte pro", "id", "desc"),
            ("Date de la demande", "dateCreated", "asc"),
            ("Date de la demande", "dateCreated", "desc"),
        ],
    )
    def test_list_only_user_offerer_to_be_validated(self, authenticated_client, row_key, sort, order):
        to_be_validated = []
        for _ in range(2):
            validated_user_offerer = offerers_factories.UserOffererFactory()
            new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(offerer=validated_user_offerer.offerer)
            to_be_validated.append(new_user_offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, order=order, sort=sort))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        # Without sort, table is ordered by id desc
        to_be_validated.sort(key=attrgetter(sort or "id"), reverse=(order == "desc") if sort else True)
        if sort == "id" or not order:
            assert [int(row[row_key]) for row in rows] == [user_offerer.user.id for user_offerer in to_be_validated]
        elif sort == "dateCreated":
            assert [row[row_key] for row in rows] == [
                user_offerer.dateCreated.strftime("%d/%m/%Y") for user_offerer in to_be_validated
            ]

    def _test_payload_content(self, auth_client, offerer_tags):
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 2, 11, 30),
            offerer__tags=[offerer_tags[1]],
            dateCreated=datetime.datetime(2022, 11, 2, 11, 59),
        )
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer,
            validationStatus=ValidationStatus.NEW,
            dateCreated=datetime.datetime(2022, 11, 3, 11, 59),
            user__phoneNumber="+33612345678",
        )
        commenter = users_factories.AdminFactory(firstName="Inspecteur", lastName="Validateur")
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 3, 12, 0),
            actionType=history_models.ActionType.USER_OFFERER_NEW,
            authorUser=commenter,
            offerer=new_user_offerer.offerer,
            user=new_user_offerer.user,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 4, 13, 1),
            actionType=history_models.ActionType.COMMENT,
            authorUser=commenter,
            offerer=new_user_offerer.offerer,
            user=new_user_offerer.user,
            comment="Bla blabla",
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 5, 14, 2),
            actionType=history_models.ActionType.USER_OFFERER_PENDING,
            authorUser=commenter,
            offerer=new_user_offerer.offerer,
            user=new_user_offerer.user,
            comment="Bla blabla",
        )

        with assert_num_queries(self.expected_num_queries):
            response = auth_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID Compte pro"] == str(new_user_offerer.user.id)
        assert rows[0]["Email Compte pro"] == new_user_offerer.user.email
        assert rows[0]["Nom Compte pro"] == new_user_offerer.user.full_name
        assert rows[0]["État"] == "Nouveau"
        assert rows[0]["Tags Structure"] == offerer_tags[1].label
        assert rows[0]["Date de la demande"] == "03/11/2022"
        assert rows[0]["Nom Structure"] == owner_user_offerer.offerer.name
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["Dernier commentaire"] == "Bla blabla"

    def test_payload_content(self, authenticated_client, offerer_tags):
        self._test_payload_content(authenticated_client, offerer_tags)

    def test_payload_content_as_read_only_user(self, client, read_only_bo_user, offerer_tags):
        auth_client = client.with_bo_session_auth(read_only_bo_user)
        self._test_payload_content(auth_client, offerer_tags)

    def test_payload_content_no_action(self, authenticated_client, offerer_tags):
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 3),
            offerer__tags=[offerer_tags[2]],
            dateCreated=datetime.datetime(2022, 11, 24),
        )
        offerers_factories.UserOffererFactory(offerer=owner_user_offerer.offerer)  # other validated, not owner
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer, dateCreated=datetime.datetime(2022, 11, 25)
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID Compte pro"] == str(new_user_offerer.user.id)
        assert rows[0]["Email Compte pro"] == new_user_offerer.user.email
        assert rows[0]["Nom Compte pro"] == new_user_offerer.user.full_name
        assert rows[0]["État"] == "Nouveau"
        assert rows[0]["Tags Structure"] == offerer_tags[2].label
        assert rows[0]["Date de la demande"] == "25/11/2022"
        assert rows[0]["Nom Structure"] == owner_user_offerer.offerer.name
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["Dernier commentaire"] == ""

    @pytest.mark.parametrize(
        "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
        (
            (31, {"per_page": 10}, 4, 1, 10),
            (31, {"per_page": 10, "page": 1}, 4, 1, 10),
            (31, {"per_page": 10, "page": 3}, 4, 3, 10),
            (31, {"per_page": 10, "page": 4}, 4, 4, 1),
            (20, {"per_page": 10, "page": 1}, 2, 1, 10),
            (27, {"page": 1}, 1, 1, 27),
            (10, {"per_page": 25, "page": 1}, 1, 1, 10),
            (1, {"per_page": None, "page": 1}, 1, 1, 1),
            (1, {"per_page": "", "page": 1}, 1, 1, 1),  # ensure that it does not crash (fallbacks to default)
        ),
    )
    def test_list_pagination(
        self, authenticated_client, total_items, pagination_config, expected_total_pages, expected_page, expected_items
    ):
        for _ in range(total_items):
            offerers_factories.NotValidatedUserOffererFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **pagination_config))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == expected_items
        assert html_parser.extract_pagination_info(response.data) == (
            expected_page,
            expected_total_pages,
            total_items,
        )

    @pytest.mark.parametrize(
        "status_filter, expected_status, expected_users_emails",
        (
            ("NEW", 200, {"a@example.com", "c@example.com", "e@example.com"}),
            ("PENDING", 200, {"b@example.com", "d@example.com", "f@example.com"}),
            (
                ["NEW", "PENDING"],
                200,
                {"a@example.com", "b@example.com", "c@example.com", "d@example.com", "e@example.com", "f@example.com"},
            ),
            ("VALIDATED", 200, {"g@example.com"}),
            ("REJECTED", 200, set()),
            (
                None,
                200,
                {"a@example.com", "e@example.com", "c@example.com"},
            ),  # status NEW as default
            ("OTHER", 400, set()),  # unknown value
        ),
    )
    def test_list_filtering_by_status(
        self, authenticated_client, status_filter, expected_status, expected_users_emails, user_offerer_to_be_validated
    ):
        with assert_num_queries(
            self.expected_num_queries_when_no_query if expected_status == 400 else self.expected_num_queries
        ):
            response = authenticated_client.get(url_for(self.endpoint, status=status_filter))
            assert response.status_code == expected_status

        if expected_status == 200:
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Email Compte pro"] for row in rows} == expected_users_emails
        else:
            assert html_parser.count_table_rows(response.data) == 0

    def test_list_filtering_by_instructor(self, authenticated_client, user_offerer_to_be_validated):
        _, pending1, _, pending2, _, pending3 = user_offerer_to_be_validated

        instructor = users_factories.AdminFactory()
        instructor_id = instructor.id
        other_instructor = users_factories.AdminFactory()

        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_PENDING,
            authorUser=instructor,
            user=pending1.user,
            offerer=pending1.offerer,
        )

        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            actionType=history_models.ActionType.USER_OFFERER_PENDING,
            authorUser=other_instructor,
            user=pending2.user,
            offerer=pending2.offerer,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_PENDING,
            authorUser=instructor,
            user=users_factories.NonAttachedProFactory(),
            offerer=pending2.offerer,
        )

        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            actionType=history_models.ActionType.USER_OFFERER_PENDING,
            authorUser=instructor,
            user=pending3.user,
            offerer=pending3.offerer,
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_PENDING,
            authorUser=other_instructor,
            user=pending3.user,
            offerer=pending3.offerer,
        )

        # +1 query to fill in instructor filter
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, status="PENDING", instructors=instructor_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {pending1.user.email}

    @pytest.mark.parametrize(
        "offerer_status_filter, expected_status, expected_users_emails",
        (
            ("NEW", 200, {"a@example.com", "b@example.com"}),
            ("PENDING", 200, {"d@example.com", "e@example.com"}),
            (
                ["NEW", "PENDING"],
                200,
                {"a@example.com", "b@example.com", "d@example.com", "e@example.com"},
            ),
            ("VALIDATED", 200, {"c@example.com", "f@example.com"}),
            ("REJECTED", 200, set()),
            (
                None,
                200,
                {"a@example.com", "b@example.com", "c@example.com", "d@example.com", "e@example.com", "f@example.com"},
            ),  # same as default
            ("OTHER", 400, set()),  # unknown value
        ),
    )
    def test_list_filtering_by_offerer_status(
        self,
        authenticated_client,
        offerer_status_filter,
        expected_status,
        expected_users_emails,
        user_offerer_to_be_validated,
    ):
        with assert_num_queries(self.expected_num_queries if expected_status == 200 else self.expected_num_queries - 2):
            response = authenticated_client.get(
                url_for(self.endpoint, offerer_status=offerer_status_filter, status=["NEW", "PENDING"])
            )
            assert response.status_code == expected_status

        if expected_status == 200:
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Email Compte pro"] for row in rows} == expected_users_emails
        else:
            assert html_parser.count_table_rows(response.data) == 0

    @pytest.mark.parametrize(
        "region_filter, expected_users_emails",
        (
            (["Martinique"], {"a@example.com", "d@example.com"}),
            (["Guadeloupe", "Provence-Alpes-Côte d'Azur"], {"b@example.com", "e@example.com"}),
        ),
    )
    def test_list_filtering_by_region(
        self, authenticated_client, region_filter, expected_users_emails, user_offerer_to_be_validated
    ):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, regions=region_filter, status=["NEW", "PENDING"])
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == expected_users_emails

    @pytest.mark.parametrize(
        "tag_filter, expected_users_emails",
        (
            (["Top acteur"], {"b@example.com", "e@example.com", "f@example.com"}),
            (["Collectivité"], {"c@example.com", "e@example.com"}),
            (["Établissement public"], {"d@example.com", "f@example.com"}),
            (["Établissement public", "Top acteur"], {"f@example.com"}),
        ),
    )
    def test_list_filtering_by_tags(
        self, authenticated_client, tag_filter, expected_users_emails, user_offerer_to_be_validated
    ):
        tags = (
            offerers_models.OffererTag.query.filter(offerers_models.OffererTag.label.in_(tag_filter))
            .with_entities(offerers_models.OffererTag.id)
            .all()
        )
        tags_ids = [_id for _id, in tags]

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, tags=tags_ids, status=["NEW", "PENDING"]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == expected_users_emails

    def test_list_filtering_by_date(self, authenticated_client):
        # Created before requested range, excluded from results:
        offerers_factories.NotValidatedUserOffererFactory(dateCreated=datetime.datetime(2022, 11, 24, 22, 30))
        # Created within requested range: Nov 24 23:45 UTC is Nov 25 00:45 CET
        user_offerer_2 = offerers_factories.NotValidatedUserOffererFactory(
            dateCreated=datetime.datetime(2022, 11, 24, 23, 45)
        )
        # Within requested range:
        user_offerer_3 = offerers_factories.NotValidatedUserOffererFactory(
            dateCreated=datetime.datetime(2022, 11, 25, 9, 15)
        )
        # Excluded from results because on the day after, Metropolitan French time:
        offerers_factories.NotValidatedUserOffererFactory(dateCreated=datetime.datetime(2022, 11, 25, 23, 30))

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_date="2022-11-25",
                    to_date="2022-11-25",
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert [int(row["ID Compte pro"]) for row in rows] == [uo.user.id for uo in (user_offerer_3, user_offerer_2)]

    @pytest.mark.parametrize("postal_code", ["97100", "97 100"])
    def test_list_search_by_postal_code(self, authenticated_client, user_offerer_to_be_validated, postal_code):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=postal_code, status="PENDING"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"b@example.com"}

    def test_list_search_by_department_code(self, authenticated_client, user_offerer_to_be_validated):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="972"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"a@example.com"}

    def test_list_search_by_city(self, authenticated_client, user_offerer_to_be_validated):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="Fort-De-France"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"a@example.com"}

    def test_list_search_by_email(self, authenticated_client, user_offerer_to_be_validated):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="a@example.com"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"a@example.com"}


class ValidateOffererAttachmentTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.validate_user_offerer"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_validate_offerer_attachment(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.isValidated
        assert user_offerer.user.has_pro_role
        assert not user_offerer.user.has_non_attached_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value.__dict__
        )

    def test_validate_offerer_attachment_returns_404_if_offerer_is_not_found(self, authenticated_client, offerer):
        response = self.post_to_endpoint(authenticated_client, user_offerer_id=42)
        assert response.status_code == 404

    def test_cannot_validate_offerer_attachment_already_validated(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        db.session.expire_all()

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà validé" in redirected_response.data.decode("utf8")


class GetRejectOffererAttachmentFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_reject_user_offerer_form"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    # session + current user + UserOfferer
    expected_num_queries = 3

    def test_get_reject_offerer_attachment_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        url = url_for(self.endpoint, user_offerer_id=user_offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class RejectOffererAttachmentTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.reject_user_offerer"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_reject_offerer_attachment(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 1
        assert users_offerers[0].validationStatus == ValidationStatus.REJECTED

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_REJECTION.value.__dict__
        )

    def test_reject_offerer_returns_404_if_offerer_attachment_is_not_found(self, authenticated_client, offerer):
        response = self.post_to_endpoint(authenticated_client, user_offerer_id=42)
        assert response.status_code == 404


class SetOffererAttachmentPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.set_user_offerer_pending"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_set_offerer_attachment_pending(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client, user_offerer_id=user_offerer.id, form={"comment": "En attente de documents"}
        )

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert not user_offerer.isValidated
        assert user_offerer.validationStatus == ValidationStatus.PENDING
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_PENDING
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None
        assert action.comment == "En attente de documents"

    def test_set_offerer_attachment_pending_keep_pro_role(self, authenticated_client):
        user = offerers_factories.UserOffererFactory().user  # already validated
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=user)

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        db.session.refresh(user)
        assert user_offerer.isPending
        assert user.has_pro_role
        assert not user.has_non_attached_pro_role

    def test_set_offerer_attachment_pending_remove_pro_role(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.UserNotValidatedOffererFactory(user=user_offerer.user)  # other pending offerer validation
        offerers_factories.NotValidatedUserOffererFactory(user=user_offerer.user)  # other pending attachment

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.isPending
        assert not user_offerer.user.has_pro_role
        assert user_offerer.user.has_non_attached_pro_role


class AddUserOffererAndValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.add_user_offerer_and_validate"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_add_user_offerer_and_validate(self, legit_user, authenticated_client):
        offerer = offerers_factories.UserOffererFactory().offerer
        user = users_factories.UserFactory()
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED,
            authorUser=legit_user,
            offerer=offerer,
            user=user,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"pro_user_id": user.id, "comment": "Le rattachement avait été rejeté par erreur"},
        )

        assert response.status_code == 303
        db.session.refresh(offerer)
        db.session.refresh(user)
        assert len(offerer.UserOfferers) == 2
        assert user.has_pro_role
        assert len(user.UserOfferers) == 1
        assert user.UserOfferers[0].isValidated
        assert user.UserOfferers[0].offerer == offerer

        action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_VALIDATED
        ).one()
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "Le rattachement avait été rejeté par erreur"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value.__dict__
        )

    def test_add_existing_user_offerer(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=user_offerer.offererId,
            form={"pro_user_id": user_offerer.userId, "comment": "test"},
        )

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "L'ID ne correspond pas à un ancien rattachement à la structure"
        )

        assert offerers_models.UserOfferer.query.count() == 1  # existing before request
        assert history_models.ActionHistory.query.count() == 0
        assert len(mails_testing.outbox) == 0

    def test_add_user_not_related(self, legit_user, authenticated_client):
        offerer = offerers_factories.UserOffererFactory().offerer
        user = users_factories.UserFactory()

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"pro_user_id": user.id, "comment": "test"}
        )

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "L'ID ne correspond pas à un ancien rattachement à la structure"
        )

    def test_add_user_empty(self, legit_user, authenticated_client):
        offerer = offerers_factories.UserOffererFactory().offerer
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED,
            authorUser=legit_user,
            offerer=offerer,
            user=users_factories.UserFactory(),
        )

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"pro_user_id": 0, "comment": "test"}
        )

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Les données envoyées comportent des erreurs. Compte pro : Aucun compte pro n'est sélectionné ;"
        )


class BatchOffererValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_validate_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_validate(self, legit_user, authenticated_client):
        _offerers = offerers_factories.NotValidatedOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(offerer.id) for offerer in _offerers)

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=_offerers[0].id, form={"object_ids": parameter_ids}
        )

        assert response.status_code == 303
        for offerer in _offerers:
            db.session.refresh(offerer)
            assert offerer.isValidated
            action = history_models.ActionHistory.query.filter(
                history_models.ActionHistory.offererId == offerer.id,
            ).one()
            assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId is None
            assert action.offererId == offerer.id
            assert action.venueId is None
            assert action.comment is None


class GetBatchOffererPendingFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_batch_offerer_pending_form"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    # session + current user (2 queries)
    # get all tags to fill in form choices (1 query)
    expected_num_queries = 3

    def test_get_batch_offerer_pending_form(self, legit_user, authenticated_client):
        offerers_factories.NotValidatedOffererFactory()

        url = url_for(self.endpoint)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class SetBatchOffererPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_set_offerer_pending"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_pending(self, legit_user, authenticated_client, offerer_tags):
        _offerers = offerers_factories.NotValidatedOffererFactory.create_batch(
            10, tags=[offerer_tags[0], offerer_tags[1]]
        )
        parameter_ids = ",".join(str(offerer.id) for offerer in _offerers)
        comment = "test pending comment"
        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=_offerers[0].id,
            form={"object_ids": parameter_ids, "comment": comment, "tags": [offerer_tags[0].id, offerer_tags[2].id]},
        )

        assert response.status_code == 303
        for offerer in _offerers:
            db.session.refresh(offerer)
            assert not offerer.isValidated
            assert offerer.validationStatus == ValidationStatus.PENDING
            assert set(offerer.tags) == {offerer_tags[0], offerer_tags[2]}
            action = history_models.ActionHistory.query.filter(
                history_models.ActionHistory.offererId == offerer.id,
            ).one()

            assert action.actionType == history_models.ActionType.OFFERER_PENDING
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId is None
            assert action.offererId == offerer.id
            assert action.venueId is None
            assert action.comment == comment
            assert action.extraData == {
                "modified_info": {
                    "tags": {
                        "new_info": f"{offerer_tags[0].label}, {offerer_tags[2].label}",
                        "old_info": offerer_tags[1].label,
                    },
                }
            }


class GetBatchOffererRejectFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_batch_reject_offerer_form"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_get_offerer_attachment_pending_form(self, legit_user, authenticated_client):
        offerers_factories.NotValidatedOffererFactory()

        url = url_for(self.endpoint)
        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class BatchOffererRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_reject_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_reject(self, legit_user, authenticated_client):
        _offerers = offerers_factories.NotValidatedOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(offerer.id) for offerer in _offerers)
        comment = "test comment"

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=_offerers[0].id,
            form={"object_ids": parameter_ids, "comment": comment},
        )

        assert response.status_code == 303

        for offerer in _offerers:
            action = history_models.ActionHistory.query.filter(
                history_models.ActionHistory.offererId == offerer.id,
            ).one()
            assert action.actionType == history_models.ActionType.OFFERER_REJECTED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId is None
            assert action.offererId == offerer.id
            assert action.venueId is None
            assert action.comment == comment


class BatchOffererAttachmentValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_validate_user_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_attachment_validate(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NotValidatedUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        response = self.post_to_endpoint(
            authenticated_client, form={"object_ids": parameter_ids, "comment": "test comment"}
        )

        assert response.status_code == 303
        for user_offerer in user_offerers:
            db.session.refresh(user_offerer)
            assert user_offerer.isValidated
            assert user_offerer.user.has_pro_role

            action = history_models.ActionHistory.query.filter(
                history_models.ActionHistory.offererId == user_offerer.offererId,
                history_models.ActionHistory.userId == user_offerer.userId,
            ).one()
            assert action.actionType == history_models.ActionType.USER_OFFERER_VALIDATED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId == user_offerer.user.id
            assert action.offererId == user_offerer.offerer.id
            assert action.venueId is None

        assert len(mails_testing.outbox) == len(user_offerers)

        # emails are not sorted by user_offerers
        assert {mail["To"] for mail in mails_testing.outbox} == {
            user_offerer.user.email for user_offerer in user_offerers
        }
        for mail in mails_testing.outbox:
            assert (
                mail["template"]
                == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value.__dict__
            )


class GetOffererAttachmentPendingFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_user_offerer_pending_form"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    # session + current user + UserOfferer
    expected_num_queries = 3

    def test_get_offerer_attachment_pending_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        url = url_for(self.endpoint, user_offerer_id=user_offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class SetBatchOffererAttachmentPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_set_user_offerer_pending"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_attachment_pending(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NotValidatedUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=user_offerers[0].offerer.id,
            form={"object_ids": parameter_ids, "comment": "test comment"},
        )

        assert response.status_code == 303
        for user_offerer in user_offerers:
            db.session.refresh(user_offerer)
            assert not user_offerer.isValidated
            assert user_offerer.validationStatus == ValidationStatus.PENDING
            action = history_models.ActionHistory.query.filter(
                history_models.ActionHistory.offererId == user_offerer.offererId,
                history_models.ActionHistory.userId == user_offerer.userId,
            ).one()
            assert action.actionType == history_models.ActionType.USER_OFFERER_PENDING
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId == user_offerer.user.id
            assert action.offererId == user_offerer.offerer.id
            assert action.venueId is None
            assert action.comment == "test comment"


class GetOffererAttachmentRejectFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_batch_reject_user_offerer_form"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_get_batch_reject_user_offerer_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        url = url_for(self.endpoint, user_offerer_id=user_offerer.id)
        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class BatchOffererAttachmentRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_reject_user_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_attachment_reject(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NotValidatedUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        response = self.post_to_endpoint(
            authenticated_client, form={"object_ids": parameter_ids, "comment": "test comment"}
        )

        assert response.status_code == 303
        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 10
        assert all(user_offerer.validationStatus == ValidationStatus.REJECTED for user_offerer in users_offerers)

        for user_offerer in user_offerers:
            action = history_models.ActionHistory.query.filter(
                history_models.ActionHistory.offererId == user_offerer.offererId,
                history_models.ActionHistory.userId == user_offerer.userId,
            ).one()
            assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId == user_offerer.user.id
            assert action.offererId == user_offerer.offerer.id
            assert action.comment == "test comment"
            assert action.venueId is None

        assert len(mails_testing.outbox) == len(user_offerers)

        # emails are not sorted by user_offerers
        assert {mail["To"] for mail in mails_testing.outbox} == {
            user_offerer.user.email for user_offerer in user_offerers
        }
        for mail in mails_testing.outbox:
            assert (
                mail["template"]
                == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_REJECTION.value.__dict__
            )


class ListOffererTagsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer_tag.list_offerer_tags"
    needed_permission = perm_models.Permissions.READ_TAGS

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch categories and tags (2 queries)
    expected_num_queries = 4

    def test_list_offerer_tags(self, authenticated_client):
        category = offerers_factories.OffererTagCategoryFactory(label="indépendant")
        offerer_tag = offerers_factories.OffererTagFactory(
            name="scottish-tag",
            label="Taggy McTagface",
            description="FREEDOOOOOOOOOM",
            categories=[category],
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="tags-tab-pane")
        assert len(rows) == 1
        assert rows[0]["Nom"] == offerer_tag.name
        assert rows[0]["Libellé"] == offerer_tag.label
        assert rows[0]["Description"] == offerer_tag.description
        assert rows[0]["Catégories"] == category.label

    def test_list_offerer_tag_categories(self, authenticated_client):
        offerers_factories.OffererTagCategoryFactory(name="homologation", label="Homologation")
        offerers_factories.OffererTagCategoryFactory(name="comptage", label="Comptage partenaires")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="categories-tab-pane")
        assert len(rows) == 2
        assert rows[0]["Nom"] == "comptage"
        assert rows[0]["Libellé"] == "Comptage partenaires"
        assert rows[1]["Nom"] == "homologation"
        assert rows[1]["Libellé"] == "Homologation"


class CreateTagButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_OFFERER_TAG
    button_label = "Créer un tag structure"

    @property
    def path(self):
        return url_for("backoffice_web.offerer_tag.list_offerer_tags")


class CreateTagCategoryButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_TAGS_N2
    button_label = "Créer une catégorie"

    @property
    def path(self):
        return url_for("backoffice_web.offerer_tag.list_offerer_tags")


class UpdateOffererTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer_tag.update_offerer_tag"
    endpoint_kwargs = {"offerer_tag_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERER_TAG

    def test_update_offerer_tag(self, authenticated_client):
        offerer_tag_not_to_edit = offerers_factories.OffererTagFactory(name="zzzzzzzz-end-of-the-list")
        category_to_keep = offerers_factories.OffererTagCategoryFactory(label="AAA")
        category_to_remove = offerers_factories.OffererTagCategoryFactory(label="BBB")
        category_to_add = offerers_factories.OffererTagCategoryFactory(label="ZZZ")
        offerer_tag_to_edit = offerers_factories.OffererTagFactory(
            name="tag-you-are-it",
            label="C'est toi le loup",
            description="Le jeu du loup c'est le 'tag' en anglais hihi",
            categories=[category_to_keep, category_to_remove],
        )

        new_name = "very-serious-tag"
        new_label = "Tag très sérieux"
        new_description = "Pas le temps de jouer"
        new_categories = [category_to_keep.id, category_to_add.id]

        base_form = {
            "name": new_name,
            "label": new_label,
            "description": new_description,
            "categories": new_categories,
        }
        response = self.post_to_endpoint(authenticated_client, offerer_tag_id=offerer_tag_to_edit.id, form=base_form)
        assert response.status_code == 303

        # Test redirection
        expected_url = url_for("backoffice_web.offerer_tag.list_offerer_tags", _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(expected_url)

        rows = html_parser.extract_table_rows(response.data)
        assert html_parser.count_table_rows(response.data) == 2
        assert rows[0]["Nom"] == new_name
        assert rows[0]["Libellé"] == new_label
        assert rows[0]["Description"] == new_description
        assert all(label in rows[0]["Catégories"] for label in [category_to_keep.label, category_to_add.label])

        assert rows[1]["Nom"] == offerer_tag_not_to_edit.name

    def test_update_with_wrong_data(self, authenticated_client):
        offerer_tag_to_edit = offerers_factories.OffererTagFactory(
            name="tag-alog",
            label="Le tagalog c'est du philippin",
        )
        base_form = {
            "name": "",
            "label": "Le tagalog c'est du philippin",
        }
        response = self.post_to_endpoint(authenticated_client, offerer_tag_id=offerer_tag_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offerer_tag.list_offerer_tags", _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(expected_url)

        assert "Les données envoyées comportent des erreurs" in html_parser.extract_alert(response.data)
        assert offerer_tag_to_edit.name != ""

    def test_update_with_already_existing_tag(self, authenticated_client):
        offerers_factories.OffererTagFactory(
            name="i-was-here-first",
        )
        offerer_tag_to_edit = offerers_factories.OffererTagFactory(
            name="a-silly-name",
        )
        base_form = {
            "name": "i-was-here-first",
            "label": "",
            "description": "",
            "categories": [],
        }

        response = self.post_to_endpoint(authenticated_client, offerer_tag_id=offerer_tag_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offerer_tag.list_offerer_tags", _external=True)
        response = authenticated_client.get(expected_url)

        assert html_parser.extract_alert(response.data) == "Ce nom de tag existe déjà"
        assert offerer_tag_to_edit.name == "a-silly-name"


class CreateOffererTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer_tag.create_offerer_tag"
    needed_permission = perm_models.Permissions.MANAGE_OFFERER_TAG

    def test_create_offerer_tag(self, authenticated_client):
        category = offerers_factories.OffererTagCategoryFactory(label="La catégorie des sucreries")

        name = "tag-ada"
        label = "Fraise Tag-ada"
        description = "Un tag délicieux mais dangereux"
        categories = [category.id]

        base_form = {
            "name": name,
            "label": label,
            "description": description,
            "categories": categories,
        }
        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer_tag.list_offerer_tags", _external=True)

        created_tag = offerers_models.OffererTag.query.one()
        assert created_tag.name == name
        assert created_tag.label == label
        assert created_tag.description == description
        assert created_tag.categories == [category]

    def test_create_with_wrong_data(self, authenticated_client):
        base_form = {
            "name": "",
            "label": "Mon nom est Personne",
        }
        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303
        assert "Les données envoyées comportent des erreurs" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )
        assert offerers_models.OffererTag.query.count() == 0

    def test_create_with_already_existing_tag(self, authenticated_client):
        offerers_factories.OffererTagFactory(
            name="i-was-here-first",
        )
        base_form = {
            "name": "i-was-here-first",
        }
        response = self.post_to_endpoint(authenticated_client, form=base_form)
        assert response.status_code == 303
        assert html_parser.extract_alert(authenticated_client.get(response.location).data) == "Ce tag existe déjà"
        assert offerers_models.OffererTag.query.count() == 1


class DeleteOffererTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer_tag.delete_offerer_tag"
    endpoint_kwargs = {"offerer_tag_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_TAGS_N2

    def test_delete_offerer_tag(self, authenticated_client):
        tags = offerers_factories.OffererTagFactory.create_batch(3)
        offerers_factories.OffererFactory(tags=tags[1:])

        response = self.post_to_endpoint(authenticated_client, offerer_tag_id=tags[1].id)

        assert response.status_code == 303
        assert set(offerers_models.OffererTag.query.all()) == {tags[0], tags[2]}
        assert offerers_models.Offerer.query.one().tags == [tags[2]]

    def test_delete_non_existing_tag(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_tag_id=tag.id + 1)

        assert response.status_code == 404
        assert offerers_models.OffererTag.query.count() == 1


class CreateOffererTagCategoryTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer_tag.create_offerer_tag_category"
    needed_permission = perm_models.Permissions.MANAGE_TAGS_N2

    def test_create_offerer_tag_category(self, authenticated_client):
        form_data = {
            "name": "nouvelle-categorie",
            "label": "Nouvelle catégorie",
        }
        response = self.post_to_endpoint(authenticated_client, form=form_data)

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_web.offerer_tag.list_offerer_tags", active_tab="categories", _external=True
        )

        created_category = offerers_models.OffererTagCategory.query.one()
        assert created_category.name == form_data["name"]
        assert created_category.label == form_data["label"]

    def test_create_with_already_existing_category(self, authenticated_client, offerer_tags):
        form_data = {"name": "homologation", "label": "Duplicate category"}
        response = self.post_to_endpoint(authenticated_client, form=form_data)

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "Cette catégorie existe déjà"
        )

        assert offerers_models.OffererTagCategory.query.count() == 2  # 2 categories in fixture


class GetIndividualOffererSubscriptionTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_individual_subscription"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = {perm_models.Permissions.VALIDATE_OFFERER, perm_models.Permissions.READ_PRO_AE_INFO}

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get data (1 query)
    expected_num_queries = 3

    icon_class_re = re.compile(r"^(bi-|text-).*")

    def _assert_steps(self, data, expected):
        soup = html_parser.get_soup(data)
        steps = soup.find_all("div", {"class": "steps"})

        classes_by_step = {}

        for step in steps:
            step_label = step.text.strip()
            i = step.select(".icon-container i")
            if i:
                assert len(i) == 1
                classes_by_step[step_label] = [
                    class_ for class_ in i[0].get("class") if self.icon_class_re.match(class_)
                ]
            else:
                classes_by_step[step_label] = None

        assert classes_by_step == expected

    def test_without_subscription_data(self, authenticated_client):
        offerer = offerers_factories.NotValidatedOffererFactory()
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        self._assert_steps(
            response.data,
            {
                "Mail envoyé": None,
                "Casier judiciaire": None,
                "Diplômes": None,
                "Certifications professionnelles": None,
            },
        )

    def test_with_subscription_data(self, authenticated_client):
        individual_subscription = offerers_factories.IndividualOffererSubscription(
            isCriminalRecordReceived=True, isExperienceReceived=True
        )
        offerer = individual_subscription.offerer
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        self._assert_steps(
            response.data,
            {
                "Mail envoyé": ["bi-check-circle-fill", "text-success"],
                "Casier judiciaire": ["bi-check-circle-fill", "text-success"],
                "Diplômes": ["bi-exclamation-circle-fill", "text-warning"],
                "Certifications professionnelles": ["bi-check-circle-fill", "text-success"],
            },
        )

    def test_with_adage_expected(self, authenticated_client, adage_tag):
        individual_subscription = offerers_factories.IndividualOffererSubscription(
            offerer__tags=[adage_tag], isCertificateReceived=True
        )
        offerer = individual_subscription.offerer
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        self._assert_steps(
            response.data,
            {
                "Mail envoyé": ["bi-check-circle-fill", "text-success"],
                "Casier judiciaire": ["bi-exclamation-circle-fill", "text-warning"],
                "Diplômes": ["bi-check-circle-fill", "text-success"],
                "Certifications professionnelles": ["bi-exclamation-circle-fill", "text-warning"],
                "Référencement ADAGE": ["bi-exclamation-circle-fill", "text-warning"],
            },
        )

    @pytest.mark.parametrize(
        "state,expected_adage_classes",
        [
            ("en_construction", ["bi-exclamation-circle-fill", "text-warning"]),
            ("en_instruction", ["bi-hourglass-split", "text-info"]),
            ("accepte", ["bi-check-circle-fill", "text-success"]),
            ("refuse", ["bi-x-circle-fill", "text-danger"]),
        ],
    )
    def test_with_adage_application(self, authenticated_client, adage_tag, state, expected_adage_classes):
        individual_subscription = offerers_factories.IndividualOffererSubscription(
            offerer__tags=[adage_tag],
            isCriminalRecordReceived=True,
            isCertificateReceived=True,
            isExperienceReceived=True,
        )
        offerer = individual_subscription.offerer
        educational_factories.CollectiveDmsApplicationFactory(venue__managingOfferer=offerer, state=state)
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        self._assert_steps(
            response.data,
            {
                "Mail envoyé": ["bi-check-circle-fill", "text-success"],
                "Casier judiciaire": ["bi-check-circle-fill", "text-success"],
                "Diplômes": ["bi-check-circle-fill", "text-success"],
                "Certifications professionnelles": ["bi-check-circle-fill", "text-success"],
                "Référencement ADAGE": expected_adage_classes,
            },
        )


class SaveIndividualSubscriptionButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER
    button_label = "Enregistrer"

    @property
    def path(self):
        individual_subscription = offerers_factories.IndividualOffererSubscription()
        return url_for(
            "backoffice_web.offerer.get_individual_subscription", offerer_id=individual_subscription.offerer.id
        )


class UpdateIndividualOffererSubscriptionTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.update_individual_subscription"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def _assert_data(self, individual_subscription: offerers_models.IndividualOffererSubscription, form_data: dict):
        assert individual_subscription.isEmailSent is form_data["is_email_sent"]
        assert individual_subscription.dateEmailSent == datetime.date.fromisoformat(form_data["date_email_sent"])
        assert individual_subscription.isCriminalRecordReceived is form_data["is_criminal_record_received"]
        assert individual_subscription.dateCriminalRecordReceived == (
            datetime.date.fromisoformat(form_data["date_criminal_record_received"])
            if form_data["date_criminal_record_received"]
            else None
        )
        assert individual_subscription.isCertificateReceived is form_data["is_certificate_received"]
        assert individual_subscription.certificateDetails == (form_data["certificate_details"] or None)
        assert individual_subscription.isExperienceReceived is form_data["is_experience_received"]
        assert individual_subscription.experienceDetails == (form_data["experience_details"] or None)
        assert individual_subscription.has1yrExperience is form_data["has_1yr_experience"]
        assert individual_subscription.has5yrExperience is form_data["has_4yr_experience"]
        assert individual_subscription.isCertificateValid is form_data["is_certificate_valid"]

    def test_create(self, authenticated_client):
        offerer = offerers_factories.NotValidatedOffererFactory()

        form_data = {
            "is_email_sent": True,
            "date_email_sent": (datetime.date.today() - datetime.timedelta(days=2)).isoformat(),
            "collective_offers": False,
            "individual_offers": True,
            "is_criminal_record_received": False,
            "date_criminal_record_received": None,
            "is_certificate_received": False,
            "certificate_details": "",
            "is_experience_received": False,
            "experience_details": "",
            "has_1yr_experience": False,
            "has_4yr_experience": False,
            "is_certificate_valid": False,
        }

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=form_data)

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_web.offerer.get", offerer_id=offerer.id, active_tab="subscription", _external=True
        )

        individual_subscription = offerers_models.IndividualOffererSubscription.query.filter_by(
            offererId=offerer.id
        ).one()
        self._assert_data(individual_subscription, form_data)

    def test_update(self, authenticated_client):
        individual_subscription = offerers_factories.IndividualOffererSubscription()
        offerer = individual_subscription.offerer

        form_data = {
            "is_email_sent": True,
            "date_email_sent": (datetime.date.today() - datetime.timedelta(days=2)).isoformat(),
            "collective_offers": True,
            "individual_offers": False,
            "is_criminal_record_received": True,
            "date_criminal_record_received": datetime.date.today().isoformat(),
            "is_certificate_received": True,
            "certificate_details": "BAC+42",
            "is_experience_received": True,
            "experience_details": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
            "Duis non nulla luctus, malesuada augue ac, pulvinar velit.",
            "has_1yr_experience": False,
            "has_4yr_experience": True,
            "is_certificate_valid": True,
        }

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=form_data)

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_web.offerer.get", offerer_id=offerer.id, active_tab="subscription", _external=True
        )
        self._assert_data(individual_subscription, form_data)


class GetEntrepriseInfoTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_entreprise_info"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTREPRISE_INFO

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get offerer (1 query)
    expected_num_queries = 3

    def test_offerer_entreprise_info(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456782")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert "Nom : MINISTERE DE LA CULTURE" in sirene_content
        assert "SIRET du siège social : 12345678200010" in sirene_content
        assert "Adresse : 3 RUE DE VALOIS" in sirene_content
        assert "Code postal : 75001" in sirene_content
        assert "Ville : PARIS" in sirene_content
        assert "SIREN actif : Oui" in sirene_content
        assert "Diffusible : Oui" in sirene_content
        assert "Catégorie juridique : Entrepreneur individuel" in sirene_content
        assert "Code APE : 90.03A" in sirene_content
        assert "Activité principale : Création artistique relevant des arts plastiques" in sirene_content

    def test_siren_not_found(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="000000000")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert (
            "Ce SIREN est inconnu dans la base de données Sirene, y compris dans les non-diffusibles" in sirene_content
        )

    def test_offerer_not_found(self, authenticated_client):
        url = url_for(self.endpoint, offerer_id=1)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 404

    def test_offerer_without_siren(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren=None)
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 404

    def test_offerer_with_invalid_siren(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="222222222")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert (
            "Erreur Le format du numéro SIREN est détecté comme invalide, nous ne pouvons pas récupérer de données sur l'entreprise."
            in sirene_content
        )


class GetEntrepriseInfoRcsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_entreprise_rcs_info"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTREPRISE_INFO

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get offerer (1 query)
    expected_num_queries = 3

    def test_get_rcs_info_registered(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="010000008")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        content = html_parser.content_as_text(response.data)
        assert "Activité commerciale : Oui" in content
        assert "Date d'immatriculation : 02/01/2023" in content
        assert "Date de radiation" not in content
        assert "Activité du siège social : TEST" in content

    def test_get_rcs_info_not_registered(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="020000006")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        content = html_parser.content_as_text(response.data)
        assert content == "Activité commerciale : Non"

    def test_get_rcs_info_deregistered(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="030099006")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        content = html_parser.content_as_text(response.data)
        assert "Activité commerciale : Oui" in content
        assert "Date d'immatriculation : 02/01/2023" in content
        assert "Date de radiation : 31/12/2023" in content
        assert "Activité du siège social : TEST" in content

    def test_offerer_without_siren(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren=None)
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 404


class GetEntrepriseInfoUrssafTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_entreprise_urssaf_info"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_SENSITIVE_INFO

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get offerer (1 query)
    # insert action (1 query)
    expected_num_queries = 4

    def test_get_urssaf_info_ok(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456782")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        content = html_parser.content_as_text(response.data)
        assert "À jour des cotisations sociales : Oui" in content
        assert "État : La délivrance de l'attestation de vigilance a été validée par l'Urssaf." in content
        expected_dates = TestingBackend._get_urssaf_dates()
        assert (
            f"Attestation de vigilance valide du {expected_dates[0].strftime('%d/%m/%Y')} "
            f"au {expected_dates[1].strftime('%d/%m/%Y')}" in content
        )

    def test_get_urssaf_info_taxes_not_paid(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="009000001")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        content = html_parser.content_as_text(response.data)
        assert "À jour des cotisations sociales : Non" in content
        assert (
            "État : La délivrance de l'attestation de vigilance a été refusée par l'Urssaf car l'entité n'est pas à "
            "jour de ses cotisations sociales." in content
        )
        assert "Attestation de vigilance valide" not in content

    def test_offerer_without_siren(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren=None)
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url)
            assert response.status_code == 404


class GetEntrepriseInfoDgfipTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_entreprise_dgfip_info"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_SENSITIVE_INFO

    # get session (1 query)
    # get user with profile and permissions (1 query)
    # get offerer (1 query)
    # insert action (1 query)
    expected_num_queries = 4

    def test_get_dgfip_info_ok(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456782")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        content = html_parser.content_as_text(response.data)
        assert "À jour des obligations fiscales : Oui" in content
        assert f"Date de délivrance de l'attestation : {datetime.date.today().strftime('%d/%m/%Y')}" in content
        assert (
            f"Date de la période analysée : {(datetime.date.today() - datetime.timedelta(days=10)).strftime('%d/%m/%Y')}"
            in content
        )

    def test_get_dgfip_info_taxes_not_paid(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="009000001")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        content = html_parser.content_as_text(response.data)
        assert "À jour des obligations fiscales : Non" in content
        assert "Date de délivrance de l'attestation" not in content
        assert "Date de la période analysée" not in content

    def test_offerer_without_siren(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren=None)
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url)
            assert response.status_code == 404
