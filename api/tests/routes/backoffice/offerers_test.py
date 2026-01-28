import datetime
import re
from decimal import Decimal
from operator import attrgetter
from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.connectors.clickhouse import query_mock as clickhouse_query_mock
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.entreprise.backends.testing import TestingBackend
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.search.models import IndexationReason
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice.filters import format_date
from pcapi.routes.backoffice.filters import format_date_time
from pcapi.routes.backoffice.pro.forms import TypeOptions
from pcapi.utils import date as date_utils

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

    # - session + current user (1 queries)
    # - offerer with joined data except tags (1 query)
    # - get offerer tags (1 query)
    # - get all tags for edit form (1 query)
    expected_num_queries = 4

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

    def test_get_offerer(self, authenticated_client, offerer_tags):
        offerer = offerers_factories.VenueFactory(
            offererAddress__address=geography_factories.AddressFactory(
                departmentCode="31", postalCode="31000", city="Toulouse"
            )
        ).managingOfferer
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
        assert "Département : 31 " in content
        assert "Ville : Toulouse " in content
        assert "Peut créer une offre EAC : Oui" in content
        assert "Présence CB dans les partenaires culturels : 0 OK / 1 KO " in content
        assert "Tags : Collectivité Top acteur " in content
        assert "Validation des offres : Suivre les règles" in content
        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Entité juridique" in badges
        assert "Validée" in badges
        assert "Suspendue" not in badges

    def test_offerer_detail_contains_venue_bank_information_stats(
        self,
        authenticated_client,
        offerer,
    ):
        venue_with_accepted_bank_account = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_accepted_bank_account,
            timespan=[
                date_utils.get_naive_utc_now() - datetime.timedelta(days=365),
                None,
            ],
            bankAccount=finance_factories.BankAccountFactory(label="Nouveau compte", offererId=offerer.id),
        )
        venue_with_two_bank_accounts = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_two_bank_accounts,
            timespan=[
                date_utils.get_naive_utc_now() - datetime.timedelta(days=365),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            ],
            bankAccount=finance_factories.BankAccountFactory(label="Ancien compte", offererId=offerer.id),
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_two_bank_accounts,
            timespan=[date_utils.get_naive_utc_now() - datetime.timedelta(days=1), None],
            bankAccount=finance_factories.BankAccountFactory(label="Nouveau compte", offererId=offerer.id),
        )

        venue_with_expired_bank_account = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue_with_expired_bank_account,
            timespan=[
                date_utils.get_naive_utc_now() - datetime.timedelta(days=365),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            ],
            bankAccount=finance_factories.BankAccountFactory(label="Ancien compte", offererId=offerer.id),
        )

        soft_deleted_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        soft_deleted_venue.isSoftDeleted = True
        db.session.add(soft_deleted_venue)
        db.session.flush()

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Présence CB dans les partenaires culturels : 2 OK / 1 KO " in html_parser.content_as_text(response.data)

    def test_offerer_with_adage_venue_has_adage_data(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(allowedOnAdage=True)
        offerers_factories.VenueFactory(managingOfferer=offerer, adageId="1234")
        offerers_factories.VenueFactory(managingOfferer=offerer, adageId=None)
        soft_deleted_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        soft_deleted_venue.isSoftDeleted = True
        db.session.add(soft_deleted_venue)
        db.session.flush()

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Peut créer une offre EAC : Oui" in html_parser.content_as_text(response.data)
        # One venue with adageId out of two physical venues
        assert "Partenaires culturels cartographiés sur ADAGE : 1/2" in html_parser.content_as_text(response.data)

    def test_offerer_with_no_adage_venue_has_adage_data(self, authenticated_client, offerer):
        offerer = offerers_factories.OffererFactory(allowedOnAdage=True)
        offerers_factories.VenueFactory(managingOfferer=offerer, adageId=None)

        url = url_for(self.endpoint, offerer_id=offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Peut créer une offre EAC : Oui" in html_parser.content_as_text(response.data)
        assert "Partenaires culturels cartographiés sur ADAGE : 0/1" in html_parser.content_as_text(response.data)

    def test_offerer_with_no_individual_subscription_tab(self, authenticated_client, offerer):
        offerer_id = offerer.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        assert not html_parser.get_soup(response.data).find(class_="subscription-tab-pane")

    def test_offerer_with_individual_subscription_tab_no_data(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory(name="auto-entrepreneur")
        offerer = offerers_factories.NewOffererFactory(tags=[tag])
        offerer_id = offerer.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        assert html_parser.get_soup(response.data).find(class_="subscription-tab-pane")

    def test_offerer_with_individual_subscription_data(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory(name="auto-entrepreneur")
        offerer = offerers_factories.NewOffererFactory(tags=[tag])
        offerers_factories.IndividualOffererSubscriptionFactory(offerer=offerer)
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

    def test_get_caledonian_offerer(self, authenticated_client):
        nc_offerer = offerers_factories.CaledonianVenueFactory().managingOfferer
        url = url_for(self.endpoint, offerer_id=nc_offerer.id)
        db.session.expire(nc_offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert nc_offerer.name in content
        assert f"Offerer ID : {nc_offerer.id} " in content
        assert "SIREN" not in content
        assert nc_offerer.siren not in content
        assert f"RID7 : {nc_offerer.rid7} " in content
        assert "Région : Nouvelle-Calédonie " in content
        assert "Département : 988 " in content
        assert "Ville : Nouméa " in content
        assert "Peut créer une offre EAC : Non" in content

    def test_offerer_with_several_locations(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(
            managingOfferer=offerer,
            offererAddress__address=geography_factories.AddressFactory(
                departmentCode="35", postalCode="35400", city="Saint-Malo"
            ),
        )
        offerers_factories.VenueFactory(
            managingOfferer=offerer,
            offererAddress__address=geography_factories.AddressFactory(
                departmentCode="971", postalCode="97110", city="Pointe-à-Pitre"
            ),
        )
        offerers_factories.VenueFactory(
            managingOfferer=offerer,
            offererAddress__address=geography_factories.AddressFactory(
                departmentCode="29", postalCode="29200", city="Brest"
            ),
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)
        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert offerer.name in content
        assert f"Offerer ID : {offerer.id} " in content
        assert "Régions : Bretagne, Guadeloupe " in content
        assert "Départements : 29, 35, 971 " in content
        assert "Villes : Brest, Pointe-à-Pitre, Saint-Malo " in content

    def test_get_closed_offerer(self, authenticated_client):
        closed_offerer = offerers_factories.ClosedOffererFactory()
        url = url_for(self.endpoint, offerer_id=closed_offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Entité juridique Fermée " in response_text

    def test_get_offerer_with_fraudulent_booking(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        bookings_factories.FraudulentBookingTagFactory(booking__stock__offer__venue__managingOfferer=offerer)
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert "Réservations frauduleuses" in response_text

    def test_get_offerer_which_does_not_exist(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, offerer_id=12345))
        assert response.status_code == 404

    class ValidateButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.VALIDATE_OFFERER
        button_label = "Valider"

        @property
        def path(self):
            offerer = offerers_factories.NewOffererFactory()
            return url_for("backoffice_web.offerer.get", offerer_id=offerer.id)

    class PendingButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.VALIDATE_OFFERER
        button_label = "Mettre en attente"

        @property
        def path(self):
            offerer = offerers_factories.NewOffererFactory()
            return url_for("backoffice_web.offerer.get", offerer_id=offerer.id)

    class RejectButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.VALIDATE_OFFERER
        button_label = "Rejeter"

        @property
        def path(self):
            offerer = offerers_factories.NewOffererFactory()
            return url_for("backoffice_web.offerer.get", offerer_id=offerer.id)

    class CloseButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.CLOSE_OFFERER
        button_label = "Fermer l'entité juridique"

        @property
        def path(self):
            offerer = offerers_factories.OffererFactory()
            return url_for("backoffice_web.offerer.get", offerer_id=offerer.id)

        def test_no_button_when_closed(self, authenticated_client):
            offerer = offerers_factories.ClosedOffererFactory()
            path = url_for("backoffice_web.offerer.get", offerer_id=offerer.id)

            response = authenticated_client.get(path)
            assert response.status_code == 200

            assert self.button_label not in response.data.decode("utf-8")


class ActivateOrDeactivateOffererHelper(PostEndpointHelper):
    offerer_initial_status = ValidationStatus.VALIDATED
    offerer_initially_active = True
    indexation_reason = NotImplemented
    default_form_data = {"comment": "Test"}

    def test_should_update_sendinblue_contacts(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(
            validationStatus=self.offerer_initial_status, isActive=self.offerer_initially_active
        )
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        users_offerer = offerers_factories.UserOffererFactory.create_batch(2, offerer=offerer)

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=self.default_form_data)
        assert response.status_code == 303

        assert {sib_request["email"] for sib_request in testing.sendinblue_requests} == {
            venue.bookingEmail,
            users_offerer[0].user.email,
            users_offerer[1].user.email,
        }

    def test_should_update_zendesk_sell(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(
            validationStatus=self.offerer_initial_status, isActive=self.offerer_initially_active
        )
        offerers_factories.VenueFactory(managingOfferer=offerer)

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=self.default_form_data)
        assert response.status_code == 303

        assert testing.zendesk_sell_requests == [
            {
                "action": "update",
                "id": offerer.id,
                "type": "Offerer",
                "zendesk_id": "1111111",
            }
        ]

    @patch("pcapi.core.search.async_index_collective_offer_template_ids")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_should_reindex_offers(
        self,
        mock_async_index_venue_ids,
        mock_async_index_offers_of_venue_ids,
        mock_async_index_collective_offer_template_ids,
        authenticated_client,
    ):
        offerer = offerers_factories.OffererFactory(
            validationStatus=self.offerer_initial_status, isActive=self.offerer_initially_active
        )
        venues = offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer)
        collective_offer_templates = []
        for venue in venues:
            offers_factories.OfferFactory(venue=venue)
            collective_offer_templates += educational_factories.CollectiveOfferTemplateFactory.create_batch(
                2, venue=venue
            )

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=self.default_form_data)
        assert response.status_code == 303

        mock_async_index_venue_ids.assert_called_once_with(
            {venue.id for venue in venues},
            reason=self.indexation_reason,
        )
        mock_async_index_offers_of_venue_ids.assert_called_once_with(
            {venue.id for venue in venues},
            reason=self.indexation_reason,
        )
        mock_async_index_collective_offer_template_ids.assert_called_once_with(
            {collective_offer_template.id for collective_offer_template in collective_offer_templates},
            reason=self.indexation_reason,
        )


class ActivateOffererHelper(ActivateOrDeactivateOffererHelper):
    offerer_initially_active = False
    indexation_reason = IndexationReason.OFFERER_ACTIVATION


class DeactivateOffererHelper(ActivateOrDeactivateOffererHelper):
    offerer_initially_active = True
    indexation_reason = IndexationReason.OFFERER_DEACTIVATION


class SuspendOffererTest(DeactivateOffererHelper):
    endpoint = "backoffice_web.offerer.suspend_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_suspend_offerer(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"comment": "Test suspension"}
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id)
        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == f"L'entité juridique {offerer.name} ({offerer.id}) a été suspendue"
        )

        updated_offerer = db.session.query(offerers_models.Offerer).filter_by(id=offerer.id).one()
        assert not updated_offerer.isActive

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.OFFERER_SUSPENDED
        assert action.authorUser == legit_user
        assert action.comment == "Test suspension"

    def test_cant_suspend_offerer_with_bookings(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        offers_factories.OfferFactory(venue__managingOfferer=offerer)
        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer)

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id)
        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de suspendre une entité juridique pour laquelle il existe des réservations"
        )

        not_updated_offerer = db.session.query(offerers_models.Offerer).filter_by(id=offerer.id).one()
        assert not_updated_offerer.isActive

        assert db.session.query(history_models.ActionHistory).count() == 0


class UnsuspendOffererTest(ActivateOffererHelper):
    endpoint = "backoffice_web.offerer.unsuspend_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_unsuspend_offerer(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory(isActive=False)

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"comment": "Test réactivation"}
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.offerer.get", offerer_id=offerer.id)
        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == f"L'entité juridique {offerer.name} ({offerer.id}) a été réactivée"
        )

        updated_offerer = db.session.query(offerers_models.Offerer).filter_by(id=offerer.id).one()
        assert updated_offerer.isActive

        action = db.session.query(history_models.ActionHistory).one()
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
        assert (
            db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == offerer_to_delete_id).count()
            == 0
        )

        expected_url = url_for("backoffice_web.pro.search_pro")
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == f"L'entité juridique {offerer_to_delete_name} ({offerer_to_delete_id}) a été supprimée"
        )

    def test_cant_delete_offerer_with_bookings(self, legit_user, authenticated_client):
        offerer_to_delete = offerers_factories.OffererFactory()
        offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer_to_delete)
        offerer_to_delete_id = offerer_to_delete.id

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_delete.id)
        assert response.status_code == 303
        assert (
            db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == offerer_to_delete_id).count()
            == 1
        )

        expected_url = url_for("backoffice_web.offerer.get", offerer_id=offerer_to_delete.id)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de supprimer une entité juridique pour laquelle il existe des réservations"
        )

    def test_cant_delete_offerer_with_custom_reimbursement_rule(self, legit_user, authenticated_client):
        offerer_to_delete = offerers_factories.OffererFactory()
        finance_factories.CustomReimbursementRuleFactory(offer=None, offerer=offerer_to_delete)
        offerer_to_delete_id = offerer_to_delete.id

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_delete.id, follow_redirects=True)
        assert response.status_code == 200  # after redirect
        assert (
            db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == offerer_to_delete_id).count()
            == 1
        )

        assert (
            html_parser.extract_alert(response.data)
            == "Impossible de supprimer une entité juridique ayant un tarif dérogatoire (passé, actif ou futur)"
        )

    def test_no_script_injection_in_offerer_name(self, legit_user, authenticated_client):
        offerer_id = offerers_factories.NewOffererFactory(name="<script>alert('coucou')</script>").id

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_id)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"L'entité juridique <script>alert('coucou')</script> ({offerer_id}) a été supprimée"
        )


class UpdateOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.update_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_update_offerer(self, legit_user, authenticated_client):
        offerer_to_edit = offerers_factories.OffererFactory()
        venues = offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer_to_edit)
        users_offerer = offerers_factories.UserOffererFactory.create_batch(2, offerer=offerer_to_edit)

        old_name = offerer_to_edit.name
        new_name = "Librairie bretonne"

        base_form = {
            "name": new_name,
            "tags": [tag.id for tag in offerer_to_edit.tags],
        }

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_edit.id, form=base_form)
        assert response.status_code == 303

        # Test redirection
        expected_url = url_for("backoffice_web.offerer.get", offerer_id=offerer_to_edit.id)
        assert response.location == expected_url

        # Test region update
        response = authenticated_client.get(expected_url)

        # Test history
        history_url = url_for("backoffice_web.offerer.get_history", offerer_id=offerer_to_edit.id)
        history_response = authenticated_client.get(history_url)

        offerer_to_edit = db.session.query(offerers_models.Offerer).filter_by(id=offerer_to_edit.id).one()
        assert offerer_to_edit.name == new_name

        assert len(offerer_to_edit.action_history) == 1
        assert offerer_to_edit.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert offerer_to_edit.action_history[0].authorUser == legit_user
        assert set(offerer_to_edit.action_history[0].extraData["modified_info"].keys()) == {"name"}

        history_rows = html_parser.extract_table_rows(history_response.data)
        assert len(history_rows) == 1
        assert history_rows[0]["Type"] == "Modification des informations"
        assert f"Nom juridique : {old_name} → {offerer_to_edit.name}" in history_rows[0]["Commentaire"]

        assert len(testing.sendinblue_requests) == 4
        assert {sendinblue_request["email"] for sendinblue_request in testing.sendinblue_requests} == {
            venues[0].bookingEmail,
            venues[1].bookingEmail,
            users_offerer[0].user.email,
            users_offerer[1].user.email,
        }

    def test_update_offerer_tags(self, legit_user, authenticated_client):
        offerer_to_edit = offerers_factories.OffererFactory()
        tag1 = offerers_factories.OffererTagFactory(label="Premier tag")
        tag2 = offerers_factories.OffererTagFactory(label="Deuxième tag")
        tag3 = offerers_factories.OffererTagFactory(label="Troisième tag")
        offerers_factories.OffererTagMappingFactory(tagId=tag1.id, offererId=offerer_to_edit.id)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer_to_edit)

        base_form = {
            "name": offerer_to_edit.name,
            "tags": [tag2.id, tag3.id],
        }

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer_to_edit.id, form=base_form)
        assert response.status_code == 303

        # Test history
        history_url = url_for("backoffice_web.offerer.get_history", offerer_id=offerer_to_edit.id)
        history_response = authenticated_client.get(history_url)

        db.session.query(offerers_models.Offerer).filter_by(id=offerer_to_edit.id).one()

        history_rows = html_parser.extract_table_rows(history_response.data)
        assert len(history_rows) == 1
        assert history_rows[0]["Type"] == "Modification des informations"
        assert history_rows[0]["Auteur"] == legit_user.full_name
        assert "Premier tag → Deuxième tag, Troisième tag" in history_rows[0]["Commentaire"]

        assert len(testing.sendinblue_requests) == 1
        assert testing.sendinblue_requests[0]["email"] == venue.bookingEmail

    def test_update_offerer_empty_name(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory(name="Original")

        base_form = {
            "name": "",
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
        assert db.session.query(offerers_models.OffererConfidenceRule).count() == 0
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

    # get session + user (1 query)
    # get offerer (1 query)
    # get collective offer templates count (1 query)
    expected_num_queries = 3

    @pytest.mark.parametrize(
        "venue_factory,expected_revenue_text",
        [
            (offerers_factories.VenueFactory, "Chiffre d'affaires 70,48 €"),
            (offerers_factories.CaledonianVenueFactory, "Chiffre d'affaires 70,48 € (8410 CFP)"),
        ],
    )
    def test_get_stats(self, authenticated_client, venue_factory, expected_revenue_text):
        venue = venue_factory()
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            validation=offers_models.OfferValidationStatus.APPROVED.value,
        )
        url = url_for(self.endpoint, offerer_id=venue.managingOffererId)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert (
            "Offres 137 individuelles 125 réservables | 12 non réservables 56 collectives 54 réservables | 2 non réservables 1 vitrine"
            == cards_text[0]
        )
        assert "Réservations 876 individuelles 678 collectives" == cards_text[1]
        assert expected_revenue_text in cards_text[2]

    @pytest.mark.settings(CLICKHOUSE_BACKEND="pcapi.connectors.clickhouse.backend.ClickhouseBackend")
    @patch(
        "pcapi.connectors.clickhouse.backend.BaseBackend.run_query",
        side_effect=ApiErrors(errors={"clickhouse": "Error : plouf"}, status_code=400),
    )
    def test_clickhouse_connector_raises_api_error(self, mock_run_query, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerer_id = venue.managingOffererId

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        assert (
            "Offres N/A individuelle N/A réservable | N/A non réservable N/A collective N/A réservable | N/A non réservable 0 vitrine"
            in html_parser.extract_cards_text(response.data)[0]
        )
        assert "Réservations N/A individuelle N/A collective" in html_parser.extract_cards_text(response.data)[1]
        assert "Chiffre d'affaires N/A" in html_parser.extract_cards_text(response.data)[2]

    @pytest.mark.settings(CLICKHOUSE_BACKEND="pcapi.connectors.clickhouse.backend.ClickhouseBackend")
    @patch("pcapi.connectors.clickhouse.backend.BaseBackend.run_query")
    def test_offerer_without_venues(self, mock_run_query, authenticated_client):
        offerer_id = offerers_factories.OffererFactory().id

        with assert_num_queries(self.expected_num_queries - 1):  # do not count collective offer templates
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        mock_run_query.assert_not_called()
        assert (
            "Offres N/A individuelle N/A réservable | N/A non réservable N/A collective N/A réservable | N/A non réservable N/A vitrine"
            in html_parser.extract_cards_text(response.data)[0]
        )
        assert "Réservations N/A individuelle N/A collective" in html_parser.extract_cards_text(response.data)[1]
        assert "Chiffre d'affaires N/A" in html_parser.extract_cards_text(response.data)[2]


class GetOffererRevenueDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_revenue_details"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # session + user
    # offerer
    expected_num_queries = 2

    @patch(
        "pcapi.connectors.clickhouse.testing_backend.TestingBackend.run_query",
        return_value=[
            clickhouse_query_mock.MockAggregatedRevenueQueryResult(
                2024,
                individual=Decimal("246.80"),
                expected_individual=Decimal("357.90"),
                collective=Decimal("750"),
                expected_collective=Decimal("1250"),
            ),
            clickhouse_query_mock.MockAggregatedRevenueQueryResult(
                2022,
                individual=Decimal("123.40"),
                expected_individual=Decimal("123.40"),
                collective=Decimal("1500"),
                expected_collective=Decimal("1500"),
            ),
        ],
    )
    def test_offerer_revenue_details_from_clickhouse(self, mock_run_query, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=offerer)
        offerer_id = offerer.id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        mock_run_query.assert_called_once()

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3
        assert rows[0]["Année"] == "En cours"
        assert rows[0]["CA offres IND"] == "111,10 €"
        assert rows[0]["CA offres EAC"] == "500,00 €"
        assert rows[1]["Année"] == "2024"
        assert rows[1]["CA offres IND"] == "246,80 €"
        assert rows[1]["CA offres EAC"] == "750,00 €"
        assert rows[2]["Année"] == "2022"
        assert rows[2]["CA offres IND"] == "123,40 €"
        assert rows[2]["CA offres EAC"] == "1 500,00 €"

    @pytest.mark.settings(CLICKHOUSE_BACKEND="pcapi.connectors.clickhouse.backend.ClickhouseBackend")
    @patch("pcapi.connectors.clickhouse.backend.BaseBackend.run_query")
    def test_offerer_revenue_details_when_no_venue(self, mock_run_query, authenticated_client):
        offerer_id = offerers_factories.OffererFactory().id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, offerer_id=offerer_id))
            assert response.status_code == 200

        mock_run_query.assert_not_called()
        assert "€" not in html_parser.content_as_text(response.data)


class GetOffererHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_history"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (1 queries)
    # - full history with joined data (1 query)
    expected_num_queries = 2

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
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=2),
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

        assert rows[0]["Type"] == "Commentaire interne"
        assert rows[0]["Date/Heure"].startswith(action.actionDate.strftime("%d/%m/%Y à "))
        assert rows[0]["Commentaire"] == action.comment
        assert rows[0]["Auteur"] == action.authorUser.full_name

        assert rows[1]["Type"] == "Fraude et Conformité"
        assert (
            rows[1]["Commentaire"]
            == "Informations modifiées : Validation des offres : Revue manuelle → Validation auto"
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
        assert rows[0]["Type"] == "Nouvelle entité juridique"
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
            comment="Commentaire sur une autre entité juridique",
        )

        url = url_for(self.endpoint, offerer_id=user_offerer.offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 4

        assert rows[0]["Type"] == "Entité juridique validée"
        assert rows[0]["Date/Heure"] == "06/10/2022 à 18h04"  # CET (Paris time)
        assert rows[0]["Commentaire"] == ""
        assert rows[0]["Auteur"] == admin.full_name

        assert rows[1]["Type"] == "Commentaire interne"
        assert rows[1]["Date/Heure"] == "05/10/2022 à 17h03"  # CET (Paris time)
        assert rows[1]["Commentaire"] == "Documents reçus"
        assert rows[1]["Auteur"] == legit_user.full_name

        assert rows[2]["Type"] == "Entité juridique mise en attente"
        assert rows[2]["Date/Heure"] == "04/10/2022 à 16h02"  # CET (Paris time)
        assert rows[2]["Commentaire"] == "Documents complémentaires demandés"
        assert rows[2]["Auteur"] == admin.full_name

        assert rows[3]["Type"] == "Nouvelle entité juridique"
        assert rows[3]["Date/Heure"] == "03/10/2022 à 15h01"  # CET (Paris time)
        assert rows[3]["Commentaire"] == ""
        assert rows[3]["Auteur"] == user_offerer.user.full_name

    def test_get_offerer_rejected_action(self, authenticated_client, legit_user):
        bo_user = users_factories.AdminFactory()
        offerer = offerers_factories.RejectedOffererFactory()
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.OFFERER_REJECTED,
            authorUser=bo_user,
            offerer=offerer,
            comment="Relancé 3 fois",
            extraData={"rejection_reason": offerers_models.OffererRejectionReason.OUT_OF_TIME.name},
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Type"] == "Entité juridique rejetée"
        assert rows[0]["Commentaire"] == "Raison : Non réponse aux questionnaires Relancé 3 fois"
        assert rows[0]["Auteur"] == bo_user.full_name

    def test_get_offerer_closed_action(self, authenticated_client, legit_user):
        bo_user = users_factories.AdminFactory()
        offerer = offerers_factories.ClosedOffererFactory()
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.OFFERER_CLOSED,
            authorUser=bo_user,
            offerer=offerer,
            comment="Demande de l'acteur culturel avant arrêt de son activité",
            extraData={"zendesk_id": 12345, "drive_link": "https://drive.example.com/path/to/document"},
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Type"] == "Entité juridique fermée"
        assert rows[0]["Commentaire"] == (
            "Demande de l'acteur culturel avant arrêt de son activité"
            "N° de ticket Zendesk : 12345 Document Drive : https://drive.example.com/path/to/document"
        )
        assert rows[0]["Auteur"] == bo_user.full_name

    def test_get_action_with_soft_deleted_venue(self, authenticated_client, legit_user):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, publicName="Soft-deleted Venue")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=bank_account,
            timespan=(
                date_utils.get_naive_utc_now() - datetime.timedelta(days=10),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            ),
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            authorUser=None,
            offerer=offerer,
            venue=venue,
            bankAccount=bank_account,
            comment=None,
        )
        venue.isSoftDeleted = True
        db.session.flush()

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Type"] == "Partenaire culturel dissocié d'un compte bancaire"
        assert rows[0]["Commentaire"] == "Partenaire culturel : Soft-deleted Venue (supprimé)"
        assert rows[0]["Auteur"] == ""


class GetOffererUsersTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_pro_users"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (1 queries)
    # - users with joined data (1 query)
    # - offerer_invitation data
    expected_num_queries = 3

    def test_get_pro_users(self, authenticated_client, offerer):
        uo1 = offerers_factories.UserOffererFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName=None, lastName=None)
        )
        uo2 = offerers_factories.UserOffererFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName="Jean", lastName="Bon")
        )
        uo3 = offerers_factories.NewUserOffererFactory(offerer=offerer)
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

        assert rows[1]["ID"] == str(uo2.user.id)
        assert rows[1]["Statut"] == "Validé"
        assert rows[1]["Prénom / Nom"] == uo2.user.full_name
        assert rows[1]["Email"] == uo2.user.email
        assert rows[1]["Invitation"] == ""

        assert rows[2]["ID"] == str(uo3.user.id)
        assert rows[2]["Statut"] == "Nouveau"
        assert rows[2]["Prénom / Nom"] == uo3.user.full_name
        assert rows[2]["Email"] == uo3.user.email
        assert rows[2]["Invitation"] == ""

        assert rows[3]["ID"] == str(uo4.user.id)
        assert rows[3]["Statut"] == "Validé Suspendu"
        assert rows[3]["Prénom / Nom"] == uo4.user.full_name
        assert rows[3]["Email"] == uo4.user.email
        assert rows[3]["Invitation"] == ""

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

        assert (url_for("backoffice_web.pro.connect_as").encode() in response.data) == result

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

    def test_user_offerer_details_tab(self, authenticated_client, offerer):
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert len(rows) == 1

        assert rows[0]["ID"] == str(user.id)
        assert rows[0]["Statut"] == "Validé"
        assert rows[0]["Prénom / Nom"] == user.full_name
        assert rows[0]["Email"] == user.email


class GetDeleteOffererAttachmentFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_delete_user_offerer_form"
    endpoint_kwargs = {"offerer_id": 1, "user_offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_get_delete_offerer_attachment_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        url = url_for(self.endpoint, offerer_id=user_offerer.offerer.id, user_offerer_id=user_offerer.id)
        with assert_num_queries(2):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class DeleteOffererAttachmentTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.delete_user_offerer"
    endpoint_kwargs = {"offerer_id": 1, "user_offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_delete_offerer_attachment(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=user_offerer.offerer.id, user_offerer_id=user_offerer.id
        )

        assert response.status_code == 303

        users_offerers = db.session.query(offerers_models.UserOfferer).all()
        assert len(users_offerers) == 1
        assert users_offerers[0].validationStatus == ValidationStatus.DELETED

        action = db.session.query(history_models.ActionHistory).one()
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

    # - session + authenticated user (1 query)
    # - venues with joined data (1 query)
    # - venue providers (selectinload: 1 query)
    expected_num_queries = 3

    def test_get_managed_venues(self, authenticated_client, offerer):
        now = date_utils.get_naive_utc_now()
        other_offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(
            name="Deuxième", publicName="Second", managingOfferer=offerer, isPermanent=True, isOpenToPublic=True
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

        venue_2 = offerers_factories.VenueFactory(
            name="Premier", publicName="NumeroUn", managingOfferer=offerer, isOpenToPublic=False
        )
        offerers_factories.VenueRegistrationFactory(venue=venue_2)
        educational_factories.CollectiveDmsApplicationFactory(venue=venue_2, application=35)
        bookings_factories.FraudulentBookingTagFactory(booking__stock__offer__venue=venue_2)
        offerers_factories.VenueFactory(managingOfferer=other_offerer)
        providers_factories.VenueProviderFactory(venue=venue_2, provider__name="Partenaire Tech")

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert rows[0]["ID"] == str(venue_2.id)
        assert rows[0]["SIRET"] == venue_2.siret
        assert rows[0]["Permanent"] == ""
        assert rows[0]["Ouvert au public"] == ""
        assert rows[0]["Nom"] == venue_2.publicName
        assert rows[0]["Activité principale"] == venue_2.venueTypeCode.value
        assert not rows[0].get("Activité principale du partenaire")
        assert rows[0]["Présence web"] == "https://example.com https://pass.culture.fr"
        assert rows[0]["Offres cibles"] == "Indiv. et coll."
        assert rows[0]["Compte bancaire associé"] == ""
        assert rows[0]["Partenaire technique"] == "Partenaire Tech (actif)"
        assert rows[0]["Fraude"] == "Réservations frauduleuses"

        assert rows[1]["ID"] == str(venue_1.id)
        assert rows[1]["SIRET"] == venue_1.siret
        assert rows[1]["Permanent"] == "Partenaire culturel permanent"
        assert rows[1]["Ouvert au public"] == "Partenaire culturel ouvert au public"
        assert rows[1]["Nom"] == venue_1.publicName
        assert rows[1]["Activité principale"] == venue_1.venueTypeCode.value
        assert not rows[0].get("Activité principale du partenaire")
        assert rows[1]["Présence web"] == ""
        assert rows[1]["Offres cibles"] == ""
        assert rows[1]["Compte bancaire associé"] == "Compte actuel"
        assert rows[1]["Partenaire technique"] == ""
        assert rows[1]["Fraude"] == ""

    def test_get_caledonian_managed_venues(self, authenticated_client):
        offerer = offerers_factories.CaledonianOffererFactory()
        venue = offerers_factories.CaledonianVenueFactory(managingOfferer=offerer)
        bank_account = finance_factories.BankAccountFactory(offerer=offerer, label="Compte NC")
        offerers_factories.VenueBankAccountLinkFactory(bankAccount=bank_account, venue=venue)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1

        assert rows[0]["ID"] == str(venue.id)
        assert rows[0]["RIDET"] == venue.ridet
        assert rows[0]["Permanent"] == "Partenaire culturel permanent"
        assert rows[0]["Nom"] == venue.publicName
        assert rows[0]["Activité principale"] == venue.venueTypeCode.value
        assert not rows[0].get("Activité principale du partenaire")
        assert rows[0]["Présence web"] == ""
        assert rows[0]["Offres cibles"] == ""
        assert rows[0]["Compte bancaire associé"] == "Compte NC"


class GetOffererAddressesTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_offerer_addresses"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (1 query)
    # - addresses (1 query)
    expected_num_queries = 2

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

        assert rows[0]["Intitulé"] == "Première adresse"
        assert rows[0]["Adresse"] == "3 Bd Poissonnière 75002 Paris"
        assert rows[0]["Localisation"] == "48.87055, 2.34765"

        assert rows[1]["Intitulé"] == "Deuxième adresse"
        assert rows[1]["Adresse"] == "5 Bd Poissonnière 75002 Paris"
        assert rows[1]["Localisation"] == "48.87055, 2.34765"

    def test_offerer_addresses_linked_to_venues_should_display_common_name(self, authenticated_client, offerer):
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            offererAddress__address__street="3 Bd Poissonnière",
        )
        venue_2 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            offererAddress__address__street="3 Bd Poissonnière",
        )
        offerers_factories.OffererAddressFactory(
            offerer=offerer, label="Autre localisation", address__street="5 Bd Poissonnière"
        )
        offerers_factories.OffererAddressFactory()  # other offerer

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2

        assert venue.common_name in rows[0]["Intitulé"]
        assert venue_2.common_name in rows[0]["Intitulé"]
        assert rows[0]["Adresse"] == "3 Bd Poissonnière 75002 Paris"
        assert rows[0]["Localisation"] == "48.87055, 2.34765"

        assert rows[1]["Intitulé"] == "Autre localisation"
        assert rows[1]["Adresse"] == "5 Bd Poissonnière 75002 Paris"
        assert rows[1]["Localisation"] == "48.87055, 2.34765"


class GetOffererCollectiveDmsApplicationsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_collective_dms_applications"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (1 query)
    # - dms applications with joined data (1 query)
    expected_num_queries = 2

    def test_get_collective_dms_applications(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900001")
        venue_2 = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678900002")
        educational_factories.CollectiveDmsApplicationFactory(
            venue=venue_1,
            application=35,
            state="refuse",
            depositDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
        )
        educational_factories.CollectiveDmsApplicationFactory(
            venue=venue_2, application=36, depositDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=2)
        )
        educational_factories.CollectiveDmsApplicationFactory(
            venue=venue_1,
            application=37,
            state="accepte",
            depositDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=3),
        )
        educational_factories.CollectiveDmsApplicationWithNoVenueFactory(
            siret="12345678900003",
            application=38,
            depositDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=4),
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
        assert rows[0]["Date de dépôt"] == (date_utils.get_naive_utc_now() - datetime.timedelta(days=1)).strftime(
            "%d/%m/%Y"
        )
        assert rows[0]["État"] == "Refusé"
        assert rows[0]["Date de dernière mise à jour"] == (
            date_utils.get_naive_utc_now() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[0]["Partenaire culturel"] == venue_1.name
        assert rows[0]["SIRET"] == venue_1.siret

        assert rows[1]["ID"] == "36"
        assert rows[1]["Date de dépôt"] == (date_utils.get_naive_utc_now() - datetime.timedelta(days=2)).strftime(
            "%d/%m/%Y"
        )
        assert rows[1]["État"] == "En construction"
        assert rows[1]["Date de dernière mise à jour"] == (
            date_utils.get_naive_utc_now() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[1]["Partenaire culturel"] == venue_2.name
        assert rows[1]["SIRET"] == venue_2.siret

        assert rows[2]["ID"] == "37"
        assert rows[2]["Date de dépôt"] == (date_utils.get_naive_utc_now() - datetime.timedelta(days=3)).strftime(
            "%d/%m/%Y"
        )
        assert rows[2]["État"] == "Accepté"
        assert rows[2]["Date de dernière mise à jour"] == (
            date_utils.get_naive_utc_now() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[2]["Partenaire culturel"] == venue_1.name
        assert rows[2]["SIRET"] == venue_1.siret

        assert rows[3]["ID"] == "38"
        assert rows[3]["Date de dépôt"] == (date_utils.get_naive_utc_now() - datetime.timedelta(days=4)).strftime(
            "%d/%m/%Y"
        )
        assert rows[3]["État"] == "En construction"
        assert rows[3]["Date de dernière mise à jour"] == (
            date_utils.get_naive_utc_now() - datetime.timedelta(hours=1)
        ).strftime("%d/%m/%Y")
        assert rows[3]["Partenaire culturel"] == ""
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

    # - session + authenticated user (1 query)
    # - bank accounts (1 query)
    expected_num_queries = 2

    def test_get_bank_accounts(self, authenticated_client, offerer):
        now = date_utils.get_naive_utc_now()
        offerer = offerers_factories.OffererFactory()
        bank1 = finance_factories.BankAccountFactory(
            offerer=offerer,
            label="Premier compte",
            status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        )
        finance_factories.BankAccountStatusHistoryFactory(
            bankAccount=bank1,
            status=finance_models.BankAccountApplicationStatus.ACCEPTED,
            timespan=[
                now - datetime.timedelta(days=3),
            ],
        )

        bank2 = finance_factories.BankAccountFactory(
            offerer=offerer,
            label="Deuxième compte",
            status=finance_models.BankAccountApplicationStatus.ON_GOING,
        )
        finance_factories.BankAccountStatusHistoryFactory(
            bankAccount=bank2,
            status=finance_models.BankAccountApplicationStatus.DRAFT,
            timespan=[now - datetime.timedelta(days=13), now - datetime.timedelta(days=2)],
        )
        finance_factories.BankAccountStatusHistoryFactory(
            bankAccount=bank2,
            status=finance_models.BankAccountApplicationStatus.ON_GOING,
            timespan=[
                now - datetime.timedelta(days=2),
            ],
        )
        bank_with_no_history = finance_factories.BankAccountFactory(
            offerer=offerer,
            label="Compte sans histoire",
            status=finance_models.BankAccountApplicationStatus.ACCEPTED,
        )
        finance_factories.BankAccountFactory()  # not listed

        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3

        assert rows[0]["ID"] == str(bank_with_no_history.id)
        assert rows[0]["Intitulé du compte bancaire"] == bank_with_no_history.label
        assert rows[0]["Statut du dossier DN CB"] == "Accepté"
        assert rows[0]["Date de dernière mise à jour"] == ""

        assert rows[1]["ID"] == str(bank2.id)
        assert rows[1]["Intitulé du compte bancaire"] == bank2.label
        assert rows[1]["Statut du dossier DN CB"] == "En instruction"
        assert rows[1]["Date de dernière mise à jour"].startswith(
            (now - datetime.timedelta(days=2)).strftime("%d/%m/%Y à")
        )

        assert rows[2]["ID"] == str(bank1.id)
        assert rows[2]["Intitulé du compte bancaire"] == bank1.label
        assert rows[2]["Statut du dossier DN CB"] == "Accepté"
        assert rows[2]["Date de dernière mise à jour"].startswith(
            (now - datetime.timedelta(days=3)).strftime("%d/%m/%Y à")
        )


class CommentOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.comment_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_add_comment(self, authenticated_client, legit_user, offerer):
        comment = "Code APE non éligible"
        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form={"comment": comment})

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.offerer.get", offerer_id=offerer.id)
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
        # - session + authenticated user (1 query)
        # - validation status count (1 query)
        # - offerer tags filter (1 query)
        expected_num_queries_when_no_query = 3
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

        def test_payload_content(self, authenticated_client, offerer_tags):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
                offerer__validationStatus=ValidationStatus.NEW,
                user__phoneNumber="+33610203040",
            )
            offerer = user_offerer.offerer
            offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress__address__city="Marseille")
            offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress__address__city="Lyon")
            tag = offerers_factories.OffererTagFactory(label="Magic Tag")
            category = (
                db.session.query(offerers_models.OffererTagCategory)
                .filter(offerers_models.OffererTagCategory.name == "homologation")
                .one()
            )
            offerers_factories.OffererTagCategoryMappingFactory(tagId=tag.id, categoryId=category.id)
            offerers_factories.OffererTagMappingFactory(tagId=tag.id, offererId=offerer.id)

            other_category_tag = offerers_factories.OffererTagFactory(label="Festival")
            other_category = offerers_factories.OffererTagCategoryFactory(name="spectacle", label="Spectacles")
            offerers_factories.OffererTagCategoryMappingFactory(
                tagId=other_category_tag.id, categoryId=other_category.id
            )
            offerers_factories.OffererTagMappingFactory(tagId=other_category_tag.id, offererId=offerer.id)

            commenter = users_factories.AdminFactory(firstName="Inspecteur", lastName="Validateur")
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 12, 0),
                actionType=history_models.ActionType.OFFERER_NEW,
                authorUser=commenter,
                offerer=offerer,
                user=user_offerer.user,
                comment=None,
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 13, 1),
                actionType=history_models.ActionType.COMMENT,
                authorUser=commenter,
                offerer=offerer,
                comment="Bla blabla",
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 14, 2),
                actionType=history_models.ActionType.OFFERER_PENDING,
                authorUser=commenter,
                offerer=offerer,
                comment="Houlala",
            )
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 10, 3, 15, 3),
                actionType=history_models.ActionType.USER_OFFERER_VALIDATED,
                authorUser=commenter,
                offerer=offerer,
                user=user_offerer.user,
                comment=None,
            )

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(offerer.id)
            assert rows[0]["Nom"] == offerer.name
            assert rows[0]["État"] == "Nouvelle"
            assert tag.label in rows[0]["Tags"]
            assert other_category_tag.label in rows[0]["Tags"]
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Documents reçus"] == ""
            assert rows[0]["Dernier commentaire"] == "Houlala"
            assert rows[0]["SIREN"] == offerer.siren
            assert rows[0]["Email"] == user_offerer.user.email
            assert rows[0]["Responsable"] == user_offerer.user.full_name
            assert rows[0]["Ville"] == "Lyon, Marseille"

            dms_adage_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")
            assert dms_adage_data == []

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
            assert rows[0]["Nom"] == user_offerer.offerer.name
            assert rows[0]["État"] == "Nouvelle"
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Dernier commentaire"] == ""

        def test_payload_content_ae_documents_not_received(self, authenticated_client):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            offerers_factories.IndividualOffererSubscriptionFactory(
                offerer=user_offerer.offerer, isEmailSent=True, isCriminalRecordReceived=True
            )

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Documents reçus"] == "Non"

        def test_payload_content_ae_documents_received(self, authenticated_client):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            offerers_factories.IndividualOffererSubscriptionFactory(
                offerer=user_offerer.offerer,
                isEmailSent=True,
                isCriminalRecordReceived=True,
                isExperienceReceived=True,
            )

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Documents reçus"] == "Oui"

        def test_dms_adage_additional_data(self, authenticated_client):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
            accepted_application = educational_factories.CollectiveDmsApplicationFactory(venue=venue, state="accepte")
            other_venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
            other_accepted_application = educational_factories.CollectiveDmsApplicationFactory(
                venue=other_venue, state="accepte"
            )
            other_rejected_application = educational_factories.CollectiveDmsApplicationFactory(
                venue=other_venue, state="refuse"
            )
            venueless_application = educational_factories.CollectiveDmsApplicationWithNoVenueFactory(
                siret=user_offerer.offerer.siren + "12345", state="accepte"
            )

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)

            dms_adage_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
            assert (
                f"Nom : {venue.name} SIRET : {accepted_application.siret} Statut du dossier DN ADAGE : Accepté Date de dernière modification : {format_date_time(accepted_application.lastChangeDate)}"
                in dms_adage_data
            )
            assert (
                f"Nom : {other_venue.name} SIRET : {other_accepted_application.siret} Statut du dossier DN ADAGE : Accepté Date de dernière modification : {format_date_time(other_accepted_application.lastChangeDate)}"
                in dms_adage_data
            )
            assert (
                f"Nom : {other_venue.name} SIRET : {other_rejected_application.siret} Statut du dossier DN ADAGE : Refusé Date de dernière modification : {format_date_time(other_rejected_application.lastChangeDate)}"
                in dms_adage_data
            )
            assert (
                f"Dossier sans partenaire culturel SIRET : {venueless_application.siret} Statut du dossier DN ADAGE : Accepté Date de dernière modification : {format_date_time(venueless_application.lastChangeDate)}"
                in dms_adage_data
            )

        @pytest.mark.parametrize(
            "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
            (
                (31, {"limit": 10}, 4, 1, 10),
                (31, {"limit": 10, "page": 1}, 4, 1, 10),
                (31, {"limit": 10, "page": 3}, 4, 3, 10),
                (31, {"limit": 10, "page": 4}, 4, 4, 1),
                (20, {"limit": 10, "page": 1}, 2, 1, 10),
                (27, {"page": 1}, 1, 1, 27),
                (10, {"limit": 25, "page": 1}, 1, 1, 10),
                (1, {"limit": None, "page": 1}, 1, 1, 1),
                (1, {"limit": "", "page": 1}, 1, 1, 1),  # ensure that it does not crash (fallbacks to default)
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
            assert {row["Nom"] for row in rows} == expected_offerer_names

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
                db.session.query(offerers_models.OffererTag)
                .filter(offerers_models.OffererTag.label.in_(tag_filter))
                .with_entities(offerers_models.OffererTag.id)
                .all()
            )
            tags_ids = [_id for (_id,) in tags]

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate", tags=tags_ids, status=["NEW", "PENDING"]
                    )
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom"] for row in rows} == expected_offerer_names

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
            with assert_num_queries(self.expected_num_queries_when_no_query + 1):  # rollback transaction
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        from_date="05/11/2022",
                    )
                )
                assert response.status_code == 400

            assert "Date invalide" in response.data.decode("utf-8")

        @pytest.mark.parametrize("search_filter", ["123004004", "123 004 004", "  123004004 ", "123004004\n"])
        def test_list_search_by_siren(self, authenticated_client, offerers_to_be_validated, search_filter):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=search_filter, status="PENDING")
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom"] for row in rows} == {"D"}

        def test_list_search_by_rid7(self, authenticated_client):
            nc_offerer = offerers_factories.NotValidatedCaledonianOffererFactory()
            rid7 = nc_offerer.siren[2:]

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=rid7)
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom"] for row in rows} == {nc_offerer.name}

        @pytest.mark.parametrize("postal_code", ["35400", "35 400"])
        def test_list_search_by_postal_code(self, authenticated_client, offerers_to_be_validated, postal_code):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=postal_code)
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom"] for row in rows} == {"E"}

        def test_list_search_by_department_code(self, authenticated_client, offerers_to_be_validated):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q="35")
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom"] for row in rows} == {"A", "E"}

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
            assert {row["Nom"] for row in rows} == {"B", "D"}
            assert html_parser.extract_pagination_info(response.data) == (1, 1, 2)

        @pytest.mark.parametrize("search_filter", ["1", "1234", "123456", "12345678", "12345678912345", "  1234"])
        def test_list_search_by_invalid_number_of_digits(self, authenticated_client, search_filter):
            with assert_num_queries(self.expected_num_queries_when_no_query + 1):  # rollback transaction
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=search_filter)
                )
                assert response.status_code == 400

            assert (
                "Le nombre de chiffres ne correspond pas à un SIREN, RID7, code postal, département ou ID DN CB"
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
            assert {row["Nom"] for row in rows} == {"B"}

        def test_list_search_by_user_name(self, authenticated_client, offerers_to_be_validated):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q="Felix faure")
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom"] for row in rows} == {"C"}

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
                offerers_factories.NewOffererFactory(name=name)

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", q=search_filter)
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom"] for row in rows} == expected_offerer_names

        @pytest.mark.parametrize(
            "status_filter, expected_status, expected_offerer_names",
            (
                ("NEW", 200, {"A", "C", "E"}),
                ("PENDING", 200, {"B", "D", "F"}),
                (["NEW", "PENDING"], 200, {"A", "B", "C", "D", "E", "F"}),
                ("VALIDATED", 200, {"G"}),
                ("REJECTED", 200, {"H"}),
                ("CLOSED", 200, {"Z"}),
                (None, 200, {"C", "A", "E"}),  # status NEW as default
                ("OTHER", 400, set()),  # unknown value
                (["REJECTED", "OTHER"], 400, set()),
            ),
        )
        def test_list_filtering_by_status(
            self, authenticated_client, status_filter, expected_status, expected_offerer_names, offerers_to_be_validated
        ):
            offerers_factories.ClosedOffererFactory(name="Z")

            expected_num_queries = (
                self.expected_num_queries if expected_status == 200 else self.expected_num_queries - 1
            )
            with assert_num_queries(expected_num_queries):
                response = authenticated_client.get(
                    url_for("backoffice_web.validation.list_offerers_to_validate", status=status_filter)
                )
                assert response.status_code == expected_status

            if expected_status == 200:
                rows = html_parser.extract_table_rows(response.data)
                assert {row["Nom"] for row in rows} == expected_offerer_names
            else:
                assert html_parser.count_table_rows(response.data) == 0

        def test_list_filtering_by_ae_documents_received(self, authenticated_client, offerers_to_be_validated):
            _, yes, no1, no2, _, _ = offerers_to_be_validated

            offerers_factories.IndividualOffererSubscriptionFactory(
                offerer=yes, isEmailSent=True, isCriminalRecordReceived=True, isExperienceReceived=True
            )
            offerers_factories.IndividualOffererSubscriptionFactory(
                offerer=no1, isEmailSent=True, isCertificateReceived=True
            )
            offerers_factories.IndividualOffererSubscriptionFactory(offerer=no2, isEmailSent=True)

            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(
                    url_for(
                        "backoffice_web.validation.list_offerers_to_validate",
                        status=["NEW", "PENDING"],
                        ae_documents_received="no",
                    )
                )
                assert response.status_code == 200

            rows = html_parser.extract_table_rows(response.data)
            assert {int(row["ID"]) for row in rows} == {no1.id, no2.id}

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
                actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=10),
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
                actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=10),
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
                self.expected_num_queries if expected_status == 200 else self.expected_num_queries - 1
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
                assert {row["Nom"] for row in rows} == expected_offerer_names
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
            assert "3 nouvelles entités juridiques" in cards
            assert "4 entités juridiques en attente" in cards
            assert "1 entité juridique validée" in cards
            assert "2 entités juridiques rejetées" in cards

        def test_no_offerer(self, authenticated_client):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for("backoffice_web.validation.list_offerers_to_validate"))
                assert response.status_code == 200

            cards = html_parser.extract_cards_text(response.data)
            assert "0 nouvelle entité juridique" in cards
            assert "0 entité juridique en attente" in cards
            assert "0 entité juridique validée" in cards
            assert "0 entité juridique rejetée" in cards
            assert html_parser.count_table_rows(response.data) == 0


class GetValidateOrRejectOffererFormTestHelper(GetEndpointHelper):
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    # session + offerer + pending bank accounts + pending collective applications
    expected_num_queries = 4

    def test_get_form(self, legit_user, authenticated_client):
        offerer = offerers_factories.NewOffererFactory()
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert offerer.name.upper() in content
        assert "coordonnées bancaires" not in content

    def test_get_form_with_bank_account(self, legit_user, authenticated_client):
        offerer = offerers_factories.NewOffererFactory()
        finance_factories.BankAccountFactory.create(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.REFUSED
        )
        bank_account = finance_factories.BankAccountFactory.create(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.ON_GOING
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            "Un dossier de coordonnées bancaires est en cours sur Démarche Numérique pour cette entité juridique, son traitement n'est pas automatique, ne l'oublions pas : "
            f"Dossier n°{bank_account.dsApplicationId} : En instruction" in content
        )

    def test_get_form_with_several_bank_accounts(self, legit_user, authenticated_client):
        offerer = offerers_factories.NewOffererFactory()
        for status in list(finance_models.BankAccountApplicationStatus):
            finance_factories.BankAccountFactory.create(offerer=offerer, status=status)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            "3 dossiers de coordonnées bancaires sont en cours sur Démarche Numérique pour cette entité juridique, leur traitement n'est pas automatique, ne les oublions pas"
            in content
        )

    def test_get_form_with_collective_application(self, legit_user, authenticated_client):
        offerer = offerers_factories.NewOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        educational_factories.CollectiveDmsApplicationFactory(venue=venue, state=GraphQLApplicationStates.refused.value)
        collective_application = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue, state=GraphQLApplicationStates.on_going.value
        )

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            "Un dossier ADAGE est en cours sur Démarche Numérique pour cette entité juridique, son traitement n'est pas automatique, ne l'oublions pas : "
            f"Dossier n°{collective_application.application} : En instruction" in content
        )

    def test_get_form_with_several_collective_applications(self, legit_user, authenticated_client):
        offerer = offerers_factories.NewOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        for state in list(GraphQLApplicationStates):
            educational_factories.CollectiveDmsApplicationFactory(venue=venue, state=state.value)

        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            "2 dossiers ADAGE sont en cours sur Démarche Numérique pour cette entité juridique, leur traitement n'est pas automatique, ne les oublions pas"
            in content
        )


class GetValidateOffererFormTest(GetValidateOrRejectOffererFormTestHelper):
    endpoint = "backoffice_web.validation.get_validate_offerer_form"


class ValidateOffererTest(ActivateOffererHelper):
    endpoint = "backoffice_web.validation.validate_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER
    offerer_initial_status = ValidationStatus.NEW
    indexation_reason = IndexationReason.OFFERER_VALIDATION

    @pytest.mark.parametrize(
        "review_all_offers,confidence_level", [("", None), ("on", offerers_models.OffererConfidenceLevel.MANUAL_REVIEW)]
    )
    def test_validate_offerer(self, legit_user, authenticated_client, review_all_offers, confidence_level):
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        offerer = user_offerer.offerer

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"comment": "Test", "review_all_offers": review_all_offers},
        )

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert offerer.isValidated
        assert offerer.isActive
        assert user_offerer.user.has_pro_role
        assert not user_offerer.user.has_non_attached_pro_role

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "Test"

        assert offerer.confidenceLevel == confidence_level

        if confidence_level:
            assert action.extraData["modified_info"] == {
                "confidenceRule.confidenceLevel": {"old_info": None, "new_info": confidence_level.name}
            }

    def test_validate_offerer_from_htmx(self, legit_user, authenticated_client):
        offerer = offerers_factories.RejectedOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200

        cells = html_parser.extract_plain_row(response.data, id=f"offerer-row-{offerer.id}")
        assert cells[2] == str(offerer.id)

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
            == f"L'entité juridique {user_offerer.offerer.name} est déjà validée"
        )

    def test_offers_set_as_pending_when_review_all_offers_checked(self, authenticated_client):
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        offerer = user_offerer.offerer
        approved_offer = offers_factories.OfferFactory(
            venue__managingOfferer=offerer,
            validation=offer_mixin.OfferValidationStatus.APPROVED,
            lastValidationType=offer_mixin.OfferValidationType.AUTO,
            lastValidationDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            lastValidationPrice=10.10,
        )
        draft_offer = offers_factories.DraftOfferFactory(
            venue__managingOfferer=offerer,
        )
        pending_offer = offers_factories.OfferFactory(
            venue__managingOfferer=offerer, validation=offer_mixin.OfferValidationStatus.PENDING
        )
        rejected_offer = offers_factories.OfferFactory(
            venue__managingOfferer=offerer, validation=offer_mixin.OfferValidationStatus.REJECTED
        )
        other_offer = offers_factories.OfferFactory(
            validation=offer_mixin.OfferValidationStatus.APPROVED,
            lastValidationType=offer_mixin.OfferValidationType.AUTO,
            lastValidationDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            lastValidationPrice=10.10,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"comment": "Test", "review_all_offers": "on"},
        )

        assert response.status_code == 303

        assert approved_offer.validation == offer_mixin.OfferValidationStatus.PENDING
        assert approved_offer.lastValidationType is None
        assert approved_offer.lastValidationDate is None
        assert approved_offer.lastValidationPrice is None

        assert draft_offer.validation == offer_mixin.OfferValidationStatus.DRAFT
        assert pending_offer.validation == offer_mixin.OfferValidationStatus.PENDING
        assert rejected_offer.validation == offer_mixin.OfferValidationStatus.REJECTED
        assert other_offer.validation == offer_mixin.OfferValidationStatus.APPROVED

    def test_offers_do_not_set_as_pending_when_review_all_offers_not_checked(self, authenticated_client):
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        offerer = user_offerer.offerer
        approved_offer = offers_factories.OfferFactory(
            venue__managingOfferer=offerer,
            validation=offer_mixin.OfferValidationStatus.APPROVED,
            lastValidationType=offer_mixin.OfferValidationType.AUTO,
            lastValidationDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            lastValidationPrice=10.10,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"comment": "Test", "review_all_offers": ""},
        )

        assert response.status_code == 303

        assert approved_offer.validation == offer_mixin.OfferValidationStatus.APPROVED
        assert approved_offer.lastValidationType == offer_mixin.OfferValidationType.AUTO


class GetRejectOffererFormTest(GetValidateOrRejectOffererFormTestHelper):
    endpoint = "backoffice_web.validation.get_reject_offerer_form"


class RejectOffererTest(DeactivateOffererHelper):
    endpoint = "backoffice_web.validation.reject_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER
    default_form_data = {"rejection_reason": "ELIGIBILITY"}
    offerer_initial_status = ValidationStatus.VALIDATED

    def test_reject_offerer(self, legit_user, authenticated_client):
        user = users_factories.NonAttachedProFactory()
        offerer = offerers_factories.NewOffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        form = {"rejection_reason": "ELIGIBILITY"}

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=form)

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

        action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.OFFERER_REJECTED)
            .one()
        )
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.extraData == {"rejection_reason": offerers_models.OffererRejectionReason.ELIGIBILITY.name}

        action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.USER_OFFERER_REJECTED)
            .one()
        )
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

    def test_reject_offerer_htmx(self, legit_user, authenticated_client):
        user = users_factories.NonAttachedProFactory()
        offerer = offerers_factories.NewOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        form = {"rejection_reason": "ELIGIBILITY"}

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form=form,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"offerer-row-{offerer.id}")
        assert cells[2] == str(offerer.id)

    def test_reject_offerer_keep_pro_role(self, authenticated_client):
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user)  # already validated
        offerer = offerers_factories.NewOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # deleted when rejected
        form = {"rejection_reason": "ELIGIBILITY"}

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=form)

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
        offerer = offerers_factories.RejectedOffererFactory(name="Test")
        form = {"rejection_reason": "ELIGIBILITY"}

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=form)

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'entité juridique Test est déjà rejetée"
        )

    def test_cannot_reject_offerer_without_reason(self, authenticated_client):
        offerer = offerers_factories.NewOffererFactory()
        form = {"rejection_reason": ""}

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=form)

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Les données envoyées comportent des erreurs. Raison du rejet : Information obligatoire ;"
        )

    def test_no_script_injection_in_offerer_name(self, legit_user, authenticated_client):
        offerer = offerers_factories.NewOffererFactory(name="<script>alert('coucou')</script>")
        form = {"rejection_reason": "ELIGIBILITY"}

        response = self.post_to_endpoint(authenticated_client, offerer_id=offerer.id, form=form)
        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'entité juridique <script>alert('coucou')</script> a été rejetée"
        )


class GetOffererPendingFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_offerer_pending_form"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    # session + current user (1 query)
    # get current tags set for this offerer (1 query)
    # get all tags to fill in form choices (1 query)
    expected_num_queries = 3

    def test_get_offerer_pending_form(self, legit_user, authenticated_client):
        offerer = offerers_factories.NewOffererFactory()
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class SetOffererPendingTest(DeactivateOffererHelper):
    endpoint = "backoffice_web.validation.set_offerer_pending"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_set_offerer_pending(self, legit_user, authenticated_client, offerer_tags):
        non_homologation_tag = offerers_factories.OffererTagFactory(name="Tag conservé")
        offerer = offerers_factories.NewOffererFactory(tags=[non_homologation_tag, offerer_tags[0], offerer_tags[1]])

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
        action = db.session.query(history_models.ActionHistory).one()

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

    def test_set_offerer_pending_from_htmx(self, legit_user, authenticated_client, offerer_tags):
        non_homologation_tag = offerers_factories.OffererTagFactory(name="Tag conservé")
        offerer = offerers_factories.NewOffererFactory(tags=[non_homologation_tag, offerer_tags[0], offerer_tags[1]])

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"comment": "En attente de documents", "tags": [offerer_tags[0].id, offerer_tags[2].id]},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200

        cells = html_parser.extract_plain_row(response.data, id=f"offerer-row-{offerer.id}")
        assert cells[2] == str(offerer.id)

    def test_set_offerer_pending_keep_pro_role(self, authenticated_client):
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user)  # already validated
        offerer = offerers_factories.NewOffererFactory()
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
        offerers_factories.NewUserOffererFactory(user=user)  # other pending attachment

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


class ListUserOffererToValidateTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.list_offerers_attachments_to_validate"
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # - session + authenticated user (1 query)
    # - offerer tags filter (1 query)
    expected_num_queries_when_no_query = 2
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
            new_user_offerer = offerers_factories.NewUserOffererFactory(offerer=validated_user_offerer.offerer)
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

    def test_payload_content(self, authenticated_client, offerer_tags):
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 2, 11, 30),
            offerer__tags=[offerer_tags[1]],
            dateCreated=datetime.datetime(2022, 11, 2, 11, 59),
        )
        new_user_offerer = offerers_factories.NewUserOffererFactory(
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
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID Compte pro"] == str(new_user_offerer.user.id)
        assert rows[0]["Email Compte pro"] == new_user_offerer.user.email
        assert rows[0]["Nom Compte pro"] == new_user_offerer.user.full_name
        assert rows[0]["État"] == "Nouveau"
        assert rows[0]["Tags Entité juridique"] == offerer_tags[1].label
        assert rows[0]["Date de la demande"] == "03/11/2022"
        assert rows[0]["Nom Entité juridique"] == owner_user_offerer.offerer.name
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["Dernier commentaire"] == "Bla blabla"

    def test_payload_content_no_action(self, authenticated_client, offerer_tags):
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 3),
            offerer__tags=[offerer_tags[2]],
            dateCreated=datetime.datetime(2022, 11, 24),
        )
        offerers_factories.UserOffererFactory(offerer=owner_user_offerer.offerer)  # other validated, not owner
        new_user_offerer = offerers_factories.NewUserOffererFactory(
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
        assert rows[0]["Tags Entité juridique"] == offerer_tags[2].label
        assert rows[0]["Date de la demande"] == "25/11/2022"
        assert rows[0]["Nom Entité juridique"] == owner_user_offerer.offerer.name
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["Dernier commentaire"] == ""

    @pytest.mark.parametrize(
        "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
        (
            (31, {"limit": 10}, 4, 1, 10),
            (31, {"limit": 10, "page": 1}, 4, 1, 10),
            (31, {"limit": 10, "page": 3}, 4, 3, 10),
            (31, {"limit": 10, "page": 4}, 4, 4, 1),
            (20, {"limit": 10, "page": 1}, 2, 1, 10),
            (27, {"page": 1}, 1, 1, 27),
            (10, {"limit": 25, "page": 1}, 1, 1, 10),
            (1, {"limit": None, "page": 1}, 1, 1, 1),
            (1, {"limit": "", "page": 1}, 1, 1, 1),  # ensure that it does not crash (fallbacks to default)
        ),
    )
    def test_list_pagination(
        self, authenticated_client, total_items, pagination_config, expected_total_pages, expected_page, expected_items
    ):
        for _ in range(total_items):
            offerers_factories.NewUserOffererFactory()

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
        if expected_status == 400:
            expected_num_queries = self.expected_num_queries_when_no_query + 1
        else:
            expected_num_queries = self.expected_num_queries
        with assert_num_queries(expected_num_queries):
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
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=10),
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
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=10),
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
        with assert_num_queries(self.expected_num_queries if expected_status == 200 else self.expected_num_queries - 1):
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
            db.session.query(offerers_models.OffererTag)
            .filter(offerers_models.OffererTag.label.in_(tag_filter))
            .with_entities(offerers_models.OffererTag.id)
            .all()
        )
        tags_ids = [_id for (_id,) in tags]

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, tags=tags_ids, status=["NEW", "PENDING"]))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == expected_users_emails

    def test_list_filtering_by_date(self, authenticated_client):
        # Created before requested range, excluded from results:
        offerers_factories.NewUserOffererFactory(dateCreated=datetime.datetime(2022, 11, 24, 22, 30))
        # Created within requested range: Nov 24 23:45 UTC is Nov 25 00:45 CET
        user_offerer_2 = offerers_factories.NewUserOffererFactory(dateCreated=datetime.datetime(2022, 11, 24, 23, 45))
        # Within requested range:
        user_offerer_3 = offerers_factories.NewUserOffererFactory(dateCreated=datetime.datetime(2022, 11, 25, 9, 15))
        # Excluded from results because on the day after, Metropolitan French time:
        offerers_factories.NewUserOffererFactory(dateCreated=datetime.datetime(2022, 11, 25, 23, 30))

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
        user_offerer = offerers_factories.NewUserOffererFactory()

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.isValidated
        assert user_offerer.user.has_pro_role
        assert not user_offerer.user.has_non_attached_pro_role

        action = db.session.query(history_models.ActionHistory).one()
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

    def test_validate_offerer_attachment_htmx(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_offerer_id=user_offerer.id,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"user-offerer-row-{user_offerer.id}")
        assert cells[2] == str(user_offerer.user.id)

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

    # session + UserOfferer
    expected_num_queries = 2

    def test_get_reject_offerer_attachment_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

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
        user_offerer = offerers_factories.NewUserOffererFactory()

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        users_offerers = db.session.query(offerers_models.UserOfferer).all()
        assert len(users_offerers) == 1
        assert users_offerers[0].validationStatus == ValidationStatus.REJECTED

        action = db.session.query(history_models.ActionHistory).one()
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

    def test_reject_offerer_attachment_htmx(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_offerer_id=user_offerer.id,
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"user-offerer-row-{user_offerer.id}")
        assert cells[2] == str(user_offerer.user.id)

    def test_reject_offerer_returns_404_if_offerer_attachment_is_not_found(self, authenticated_client, offerer):
        response = self.post_to_endpoint(authenticated_client, user_offerer_id=42)
        assert response.status_code == 404


class SetOffererAttachmentPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.set_user_offerer_pending"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_set_offerer_attachment_pending(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client, user_offerer_id=user_offerer.id, form={"comment": "En attente de documents"}
        )

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert not user_offerer.isValidated
        assert user_offerer.validationStatus == ValidationStatus.PENDING
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_PENDING
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None
        assert action.comment == "En attente de documents"

    def test_set_offerer_attachment_pending_htmx(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_offerer_id=user_offerer.id,
            form={"comment": "En attente de documents"},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        cells = html_parser.extract_plain_row(response.data, id=f"user-offerer-row-{user_offerer.id}")
        assert cells[2] == str(user_offerer.user.id)

    def test_set_offerer_attachment_pending_keep_pro_role(self, authenticated_client):
        user = offerers_factories.UserOffererFactory().user  # already validated
        user_offerer = offerers_factories.NewUserOffererFactory(user=user)

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
        offerers_factories.NewUserOffererFactory(user=user_offerer.user)  # other pending attachment

        response = self.post_to_endpoint(authenticated_client, user_offerer_id=user_offerer.id)

        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.isPending
        assert not user_offerer.user.has_pro_role
        assert user_offerer.user.has_non_attached_pro_role


class InviteUserButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
    button_label = "Inviter un collaborateur"

    @property
    def path(self):
        offerer = offerers_factories.OffererFactory()
        return url_for("backoffice_web.offerer.get_pro_users", offerer_id=offerer.id)


class InviteUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.invite_user"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_invite_user(self, legit_user, authenticated_client, offerer):
        invited_email = "someone@example.com"

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"email": invited_email}, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == f"L'invitation a été envoyée à {invited_email}"

        invitation = db.session.query(offerers_models.OffererInvitation).one()
        assert invitation.offererId == offerer.id
        assert invitation.email == invited_email
        assert invitation.user == legit_user
        assert invitation.status == offerers_models.InvitationStatus.PENDING

        assert mails_testing.outbox[0]["To"] == invited_email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value.__dict__
        )

    def test_invite_user_already_invited(self, authenticated_client, offerer):
        email = offerers_factories.OffererInvitationFactory(offerer=offerer).email

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"email": email}, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "Une invitation a déjà été envoyée à ce collaborateur"
        assert db.session.query(offerers_models.OffererInvitation).count() == 1

    def test_invite_user_already_associated(self, authenticated_client, offerer):
        user = offerers_factories.UserOffererFactory(offerer=offerer).user

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"email": user.email}, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "Ce collaborateur est déjà rattaché à l'entité juridique"
        assert db.session.query(offerers_models.OffererInvitation).count() == 0

    def test_invite_user_empty(self, authenticated_client, offerer):
        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, form={"email": ""}, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Adresse email : Email obligatoire, doit contenir entre 3 et 128 caractères ;"
        )
        assert db.session.query(offerers_models.OffererInvitation).count() == 0


class ResendInvitationTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.resend_invitation"
    endpoint_kwargs = {"offerer_id": 1, "invitation_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_resend_invitation(self, legit_user, authenticated_client, offerer):
        invitation = offerers_factories.OffererInvitationFactory(offerer=offerer)
        offerers_factories.OffererInvitationFactory(offerer=offerer)

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, invitation_id=invitation.id, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == f"L'invitation a été renvoyée à {invitation.email}"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == invitation.email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value.__dict__
        )

    def test_resend_invitation_with_matching_user(self, legit_user, authenticated_client, offerer):
        invited_email = "someone@example.com"
        users_factories.ProFactory(email=invited_email)
        invitation = offerers_factories.OffererInvitationFactory(offerer=offerer, email=invited_email)

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, invitation_id=invitation.id, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == f"L'invitation a été renvoyée à {invited_email}"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == invited_email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL.value.__dict__
        )

    def test_can_not_resend_accepted_invitation(self, authenticated_client, offerer):
        invitation = offerers_factories.OffererInvitationFactory(
            offerer=offerer, status=offerers_models.InvitationStatus.ACCEPTED
        )

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, invitation_id=invitation.id, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == f"L'invitation de {invitation.email} est déjà acceptée"
        assert not mails_testing.outbox


class DeleteInvitationTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.delete_invitation"
    endpoint_kwargs = {"offerer_id": 1, "invitation_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_delete_invitation(self, legit_user, authenticated_client, offerer):
        invitation_1_id = offerers_factories.OffererInvitationFactory(offerer=offerer, email="invite@example.com").id
        invitation_2_id = offerers_factories.OffererInvitationFactory(offerer=offerer).id

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, invitation_id=invitation_1_id, follow_redirects=True
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "L'invitation de invite@example.com a été supprimée"

        assert db.session.query(offerers_models.OffererInvitation).with_entities(
            offerers_models.OffererInvitation.id
        ).all() == [(invitation_2_id,)]

    def test_can_not_delete_accepted_invitation(self, authenticated_client, offerer):
        invitation_id = offerers_factories.OffererInvitationFactory(
            offerer=offerer, status=offerers_models.InvitationStatus.ACCEPTED
        ).id

        response = self.post_to_endpoint(
            authenticated_client, offerer_id=offerer.id, invitation_id=invitation_id, follow_redirects=True
        )

        assert response.status_code == 404  # no pending invitation (menu item is not available)
        assert db.session.query(offerers_models.OffererInvitation).count() == 1


class GetBatchValidateOrRejectOffererFormTestHelper(PostEndpointHelper):
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_get_form(self, legit_user, authenticated_client):
        offerers_factories.NewOffererFactory()

        url = url_for(self.endpoint)
        with assert_num_queries(1):  # session
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200

    def test_post_form(self, legit_user, authenticated_client):
        offerers = offerers_factories.NewOffererFactory.create_batch(3)
        parameter_ids = ",".join(str(offerer.id) for offerer in offerers)

        bank_account_1 = finance_factories.BankAccountFactory.create(
            offerer=offerers[0], status=finance_models.BankAccountApplicationStatus.DRAFT
        )
        bank_account_2 = finance_factories.BankAccountFactory.create(
            offerer=offerers[2], status=finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS
        )

        collective_application = educational_factories.CollectiveDmsApplicationFactory.create(
            venue=offerers_factories.VenueFactory(managingOfferer=offerers[1]),
            state=GraphQLApplicationStates.draft.value,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": parameter_ids},
            expected_num_queries=3,  # session + pending bank accounts + pending collective applications
        )
        assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert (
            "2 dossiers de coordonnées bancaires sont en cours sur Démarche Numérique pour ces entités juridiques, leur traitement n'est pas automatique, ne les oublions pas : "
            f"Dossier n°{bank_account_1.dsApplicationId} : En construction"
            f"Dossier n°{bank_account_2.dsApplicationId} : À corriger"
            "Un dossier ADAGE est en cours sur Démarche Numérique pour ces entités juridiques, son traitement n'est pas automatique, ne l'oublions pas : "
            f"Dossier n°{collective_application.application} : En construction" in content
        )


class GetBatchOffererValidateFormTest(GetBatchValidateOrRejectOffererFormTestHelper):
    endpoint = "backoffice_web.validation.get_batch_validate_offerer_form"


class BatchOffererValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_validate_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    @pytest.mark.parametrize(
        "review_all_offers,confidence_level", [("", None), ("on", offerers_models.OffererConfidenceLevel.MANUAL_REVIEW)]
    )
    def test_batch_set_offerer_validate(self, legit_user, authenticated_client, review_all_offers, confidence_level):
        _offerers = offerers_factories.NewOffererFactory.create_batch(3)
        parameter_ids = ",".join(str(offerer.id) for offerer in _offerers)

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=_offerers[0].id,
            form={"object_ids": parameter_ids, "comment": "Test", "review_all_offers": review_all_offers},
        )

        assert response.status_code == 200
        for offerer in _offerers:
            db.session.refresh(offerer)
            assert offerer.isValidated
            action = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.offererId == offerer.id,
                )
                .one()
            )
            assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId is None
            assert action.offererId == offerer.id
            assert action.venueId is None
            assert action.comment == "Test"

            assert offerer.confidenceLevel == confidence_level

            if confidence_level:
                assert action.extraData["modified_info"] == {
                    "confidenceRule.confidenceLevel": {"old_info": None, "new_info": confidence_level.name}
                }

            # ensure that the row is rendered
            cells = html_parser.extract_plain_row(response.data, id=f"offerer-row-{offerer.id}")
            assert cells[2] == str(offerer.id)


class GetBatchOffererPendingFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_batch_offerer_pending_form"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    # session + current user (1 query)
    # get all tags to fill in form choices (1 query)
    expected_num_queries = 2

    def test_get_batch_offerer_pending_form(self, legit_user, authenticated_client):
        offerers_factories.NewOffererFactory()

        url = url_for(self.endpoint)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class SetBatchOffererPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_set_offerer_pending"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_pending(self, legit_user, authenticated_client, offerer_tags):
        _offerers = offerers_factories.NewOffererFactory.create_batch(3, tags=[offerer_tags[0], offerer_tags[1]])
        parameter_ids = ",".join(str(offerer.id) for offerer in _offerers)
        comment = "test pending comment"
        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=_offerers[0].id,
            form={"object_ids": parameter_ids, "comment": comment, "tags": [offerer_tags[0].id, offerer_tags[2].id]},
        )

        assert response.status_code == 200
        for offerer in _offerers:
            db.session.refresh(offerer)
            assert not offerer.isValidated
            assert offerer.validationStatus == ValidationStatus.PENDING
            assert set(offerer.tags) == {offerer_tags[0], offerer_tags[2]}
            action = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.offererId == offerer.id,
                )
                .one()
            )

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
            # ensure that the row is rendered
            cells = html_parser.extract_plain_row(response.data, id=f"offerer-row-{offerer.id}")
            assert cells[2] == str(offerer.id)


class GetBatchOffererRejectFormTest(GetBatchValidateOrRejectOffererFormTestHelper):
    endpoint = "backoffice_web.validation.get_batch_reject_offerer_form"


class BatchOffererRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_reject_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    @pytest.mark.parametrize(
        "rejection_reason",
        (
            "ELIGIBILITY",
            "ERROR",
            "ADAGE_DECLINED",
            "OUT_OF_TIME",
            "NON_RECEIVED_DOCS",
            "CLOSED_BUSINESS",
            "OTHER",
        ),
    )
    def test_batch_set_offerer_reject(self, legit_user, authenticated_client, rejection_reason):
        _offerers = offerers_factories.NewOffererFactory.create_batch(3)
        parameter_ids = ",".join(str(offerer.id) for offerer in _offerers)
        comment = "test comment"

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=_offerers[0].id,
            form={"object_ids": parameter_ids, "comment": comment, "rejection_reason": rejection_reason},
        )

        assert response.status_code == 200

        for offerer in _offerers:
            action = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.offererId == offerer.id,
                )
                .one()
            )
            assert action.actionType == history_models.ActionType.OFFERER_REJECTED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId is None
            assert action.offererId == offerer.id
            assert action.venueId is None
            assert action.comment == comment
            assert action.extraData == {"rejection_reason": rejection_reason}

            # ensure that the row is rendered
            cells = html_parser.extract_plain_row(response.data, id=f"offerer-row-{offerer.id}")
            assert cells[2] == str(offerer.id)


class BatchOffererAttachmentValidateTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_validate_user_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_attachment_validate(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NewUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": parameter_ids, "comment": "test comment"},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        for user_offerer in user_offerers:
            db.session.refresh(user_offerer)
            assert user_offerer.isValidated
            assert user_offerer.user.has_pro_role

            action = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.offererId == user_offerer.offererId,
                    history_models.ActionHistory.userId == user_offerer.userId,
                )
                .one()
            )
            assert action.actionType == history_models.ActionType.USER_OFFERER_VALIDATED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId == user_offerer.user.id
            assert action.offererId == user_offerer.offerer.id
            assert action.venueId is None
            cells = html_parser.extract_plain_row(response.data, id=f"user-offerer-row-{user_offerer.id}")
            assert cells[2] == str(user_offerer.user.id)

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

    # session + UserOfferer
    expected_num_queries = 2

    def test_get_offerer_attachment_pending_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        url = url_for(self.endpoint, user_offerer_id=user_offerer.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class SetBatchOffererAttachmentPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_set_user_offerer_pending"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_attachment_pending(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NewUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=user_offerers[0].offerer.id,
            form={"object_ids": parameter_ids, "comment": "test comment"},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        for user_offerer in user_offerers:
            db.session.refresh(user_offerer)
            assert not user_offerer.isValidated
            assert user_offerer.validationStatus == ValidationStatus.PENDING
            action = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.offererId == user_offerer.offererId,
                    history_models.ActionHistory.userId == user_offerer.userId,
                )
                .one()
            )
            assert action.actionType == history_models.ActionType.USER_OFFERER_PENDING
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId == user_offerer.user.id
            assert action.offererId == user_offerer.offerer.id
            assert action.venueId is None
            assert action.comment == "test comment"
            cells = html_parser.extract_plain_row(response.data, id=f"user-offerer-row-{user_offerer.id}")
            assert cells[2] == str(user_offerer.user.id)


class GetOffererAttachmentRejectFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.validation.get_batch_reject_user_offerer_form"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_get_batch_reject_user_offerer_form(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.NewUserOffererFactory()

        url = url_for(self.endpoint, user_offerer_id=user_offerer.id)
        with assert_num_queries(1):  # session
            response = authenticated_client.get(url)
            # Rendering is not checked, but at least the fetched frame does not crash
            assert response.status_code == 200


class BatchOffererAttachmentRejectTest(PostEndpointHelper):
    endpoint = "backoffice_web.validation.batch_reject_user_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_batch_set_offerer_attachment_reject(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NewUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        response = self.post_to_endpoint(
            authenticated_client,
            form={"object_ids": parameter_ids, "comment": "test comment"},
            headers={"hx-request": "true"},
        )

        assert response.status_code == 200
        users_offerers = db.session.query(offerers_models.UserOfferer).all()
        assert len(users_offerers) == 10
        assert all(user_offerer.validationStatus == ValidationStatus.REJECTED for user_offerer in users_offerers)

        for user_offerer in user_offerers:
            action = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.offererId == user_offerer.offererId,
                    history_models.ActionHistory.userId == user_offerer.userId,
                )
                .one()
            )
            assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
            assert action.actionDate is not None
            assert action.authorUserId == legit_user.id
            assert action.userId == user_offerer.user.id
            assert action.offererId == user_offerer.offerer.id
            assert action.comment == "test comment"
            assert action.venueId is None
            cells = html_parser.extract_plain_row(response.data, id=f"user-offerer-row-{user_offerer.id}")
            assert cells[2] == str(user_offerer.user.id)

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

    # - fetch session + user (1 query)
    # - fetch categories and tags (2 queries)
    expected_num_queries = 3

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
    button_label = "Créer un tag"

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
        expected_url = url_for("backoffice_web.offerer_tag.list_offerer_tags")
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

        expected_url = url_for("backoffice_web.offerer_tag.list_offerer_tags")
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

        expected_url = url_for("backoffice_web.offerer_tag.list_offerer_tags")
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
        assert response.location == url_for("backoffice_web.offerer_tag.list_offerer_tags")

        created_tag = db.session.query(offerers_models.OffererTag).one()
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
        assert db.session.query(offerers_models.OffererTag).count() == 0

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
        assert db.session.query(offerers_models.OffererTag).count() == 1


class DeleteOffererTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer_tag.delete_offerer_tag"
    endpoint_kwargs = {"offerer_tag_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_TAGS_N2

    def test_delete_offerer_tag(self, authenticated_client):
        tags = offerers_factories.OffererTagFactory.create_batch(3)
        offerers_factories.OffererFactory(tags=tags[1:])

        response = self.post_to_endpoint(authenticated_client, offerer_tag_id=tags[1].id)

        assert response.status_code == 303
        assert set(db.session.query(offerers_models.OffererTag).all()) == {tags[0], tags[2]}
        assert db.session.query(offerers_models.Offerer).one().tags == [tags[2]]

    def test_delete_non_existing_tag(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_tag_id=tag.id + 1)

        assert response.status_code == 404
        assert db.session.query(offerers_models.OffererTag).count() == 1


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
        assert response.location == url_for("backoffice_web.offerer_tag.list_offerer_tags", active_tab="categories")

        created_category = db.session.query(offerers_models.OffererTagCategory).one()
        assert created_category.name == form_data["name"]
        assert created_category.label == form_data["label"]

    def test_create_with_already_existing_category(self, authenticated_client, offerer_tags):
        form_data = {"name": "homologation", "label": "Duplicate category"}
        response = self.post_to_endpoint(authenticated_client, form=form_data)

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "Cette catégorie existe déjà"
        )

        assert db.session.query(offerers_models.OffererTagCategory).count() == 2  # 2 categories in fixture


class GetIndividualOffererSubscriptionTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_individual_subscription"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = {perm_models.Permissions.VALIDATE_OFFERER, perm_models.Permissions.READ_PRO_AE_INFO}

    # get session + USER (1 query)
    # get data (1 query)
    expected_num_queries = 2

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
        offerer = offerers_factories.NewOffererFactory()
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        self._assert_steps(
            response.data,
            {
                "Envoi du mail": None,
                "Casier judiciaire": None,
                "Diplômes": None,
                "Certifications professionnelles": None,
            },
        )

    def test_with_subscription_data(self, authenticated_client):
        individual_subscription = offerers_factories.IndividualOffererSubscriptionFactory(
            isCriminalRecordReceived=True,
            isExperienceReceived=True,
            dateReminderEmailSent=datetime.date.today() - datetime.timedelta(days=1),
        )
        individual_subscription.dateReminderEmailSent = individual_subscription.dateEmailSent + datetime.timedelta(
            days=30
        )

        offerer = individual_subscription.offerer
        url = url_for(self.endpoint, offerer_id=offerer.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        self._assert_steps(
            response.data,
            {
                f"Mail envoyé le {format_date(individual_subscription.dateEmailSent)} Relance envoyée le {format_date(individual_subscription.dateReminderEmailSent)}": [
                    "bi-check-circle-fill",
                    "text-success",
                ],
                "Casier judiciaire": ["bi-check-circle-fill", "text-success"],
                "Diplômes": ["bi-exclamation-circle-fill", "text-warning"],
                "Certifications professionnelles": ["bi-check-circle-fill", "text-success"],
            },
        )

    def test_with_adage_expected(self, authenticated_client, adage_tag):
        individual_subscription = offerers_factories.IndividualOffererSubscriptionFactory(
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
                f"Mail envoyé le {format_date(individual_subscription.dateEmailSent)}": [
                    "bi-check-circle-fill",
                    "text-success",
                ],
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
        individual_subscription = offerers_factories.IndividualOffererSubscriptionFactory(
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
                f"Mail envoyé le {format_date(individual_subscription.dateEmailSent)}": [
                    "bi-check-circle-fill",
                    "text-success",
                ],
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
        individual_subscription = offerers_factories.IndividualOffererSubscriptionFactory()
        return url_for(
            "backoffice_web.offerer.get_individual_subscription", offerer_id=individual_subscription.offerer.id
        )


class CreateIndividualOffererSubscriptionTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.create_individual_subscription"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def test_create(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()

        response = self.post_to_endpoint(authenticated_client, offerer_id=user_offerer.offerer.id)
        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_web.offerer.get", offerer_id=user_offerer.offerer.id, active_tab="subscription"
        )
        assert user_offerer.offerer.individualSubscription is not None
        individual_subscription = user_offerer.offerer.individualSubscription

        assert individual_subscription.isEmailSent is True
        assert individual_subscription.dateEmailSent == datetime.date.today()
        assert individual_subscription.isCriminalRecordReceived is False
        assert individual_subscription.dateCriminalRecordReceived is None
        assert individual_subscription.isCertificateReceived is False
        assert individual_subscription.certificateDetails is None
        assert individual_subscription.isExperienceReceived is False
        assert individual_subscription.experienceDetails is None
        assert individual_subscription.has1yrExperience is False
        assert individual_subscription.has5yrExperience is False
        assert individual_subscription.isCertificateValid is False

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.REMINDER_OFFERER_INDIVIDUAL_SUBSCRIPTION.value.__dict__
        )

    def test_create_if_individual_subscription_already_exists(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        individual_subscription = offerers_factories.IndividualOffererSubscriptionFactory(
            offerer=user_offerer.offerer, isEmailSent=False
        )

        response = self.post_to_endpoint(authenticated_client, offerer_id=user_offerer.offerer.id)
        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_web.offerer.get", offerer_id=user_offerer.offerer.id, active_tab="subscription"
        )

        assert individual_subscription.isEmailSent is True
        assert individual_subscription.dateEmailSent == datetime.date.today()
        assert individual_subscription.isCriminalRecordReceived is False
        assert individual_subscription.dateCriminalRecordReceived is None
        assert individual_subscription.isCertificateReceived is False
        assert individual_subscription.certificateDetails is None
        assert individual_subscription.isExperienceReceived is False
        assert individual_subscription.experienceDetails is None
        assert individual_subscription.has1yrExperience is False
        assert individual_subscription.has5yrExperience is False
        assert individual_subscription.isCertificateValid is False

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert (
            mails_testing.outbox[0]["template"]
            == sendinblue_template_ids.TransactionalEmail.REMINDER_OFFERER_INDIVIDUAL_SUBSCRIPTION.value.__dict__
        )


class UpdateIndividualOffererSubscriptionTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.update_individual_subscription"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER

    def _assert_data(self, individual_subscription: offerers_models.IndividualOffererSubscription, form_data: dict):
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

    def test_update(self, authenticated_client):
        individual_subscription = offerers_factories.IndividualOffererSubscriptionFactory()
        offerer = individual_subscription.offerer

        form_data = {
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
            "backoffice_web.offerer.get", offerer_id=offerer.id, active_tab="subscription"
        )
        self._assert_data(individual_subscription, form_data)


class GetEntrepriseInfoTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_entreprise_info"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTREPRISE_INFO

    # get session + user (1 query)
    # get offerer (1 query)
    expected_num_queries = 2

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
        assert "Code APE : 9003A" in sirene_content
        assert "Activité principale : Création artistique relevant des arts plastiques" in sirene_content

    def test_siren_not_found(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="000000000")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries + 1):  # rollback transaction
            response = authenticated_client.get(url)
            assert response.status_code == 200

        # Values come from TestingBackend, check display
        sirene_content = html_parser.extract_cards_text(response.data)[0]
        assert (
            "Ce SIREN est inconnu dans la base de données Sirene, y compris dans les non-diffusibles" in sirene_content
        )

    def test_offerer_not_found(self, authenticated_client):
        url = url_for(self.endpoint, offerer_id=1)

        with assert_num_queries(self.expected_num_queries + 1):  # rollback transaction
            response = authenticated_client.get(url)
            assert response.status_code == 404

    def test_offerer_with_invalid_siren(self, authenticated_client):
        offerer = offerers_factories.OffererFactory(siren="222222222")
        url = url_for(self.endpoint, offerer_id=offerer.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries + 1):  # rollback transaction
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

    # get session + user (1 query)
    # get offerer (1 query)
    expected_num_queries = 2

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
        assert "03/02/2023 : Observation 1" in content
        assert "Date inconnue : Observation 2" in content

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


class GetEntrepriseInfoUrssafTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_entreprise_urssaf_info"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_SENSITIVE_INFO

    # get session + user (1 query)
    # get offerer (1 query)
    # insert action (1 query)
    expected_num_queries = 3

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


class GetEntrepriseInfoDgfipTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_entreprise_dgfip_info"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_SENSITIVE_INFO

    # get session + user (1 query)
    # get offerer (1 query)
    # insert action (1 query)
    expected_num_queries = 3

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


class GetCloseOffererFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.offerer.get_close_offerer_form"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.CLOSE_OFFERER

    # session + offerer + individual bookings + collective bookings
    expected_num_queries = 4

    def test_get_close_offerer_form_with_no_ongoing_booking(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()

        url = url_for(self.endpoint, offerer_id=offerer.id)
        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        html_parser.assert_no_alert(response.data)

    def test_get_close_offerer_form_with_ongoing_bookings(self, legit_user, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        bookings_factories.BookingFactory.create_batch(2, stock__offer__venue__managingOfferer=offerer)
        educational_factories.CollectiveBookingFactory(offerer=offerer)

        url = url_for(self.endpoint, offerer_id=offerer.id)
        db.session.expire(offerer)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == (
            "La fermeture de l'entité juridique entraînera l'annulation automatique de :"
            "2 réservations individuelles"
            "1 réservation collective"
        )


class CloseOffererTest(PostEndpointHelper):
    endpoint = "backoffice_web.offerer.close_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.CLOSE_OFFERER

    def test_close_offerer(self, legit_user, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"comment": "Test", "zendesk_id": "12345", "drive_link": "https://drive.example.com/test"},
            follow_redirects=True,
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == f"L'entité juridique {offerer.name} a été fermée"

        db.session.refresh(user_offerer)
        assert offerer.isClosed
        assert offerer.isActive
        assert not user_offerer.user.has_pro_role
        assert user_offerer.user.has_non_attached_pro_role

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.OFFERER_CLOSED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "Test"
        assert action.extraData["zendesk_id"] == 12345
        assert action.extraData["drive_link"] == "https://drive.example.com/test"

    @pytest.mark.parametrize(
        "validation_status",
        [ValidationStatus.NEW, ValidationStatus.PENDING, ValidationStatus.REJECTED, ValidationStatus.CLOSED],
    )
    def test_close_offerer_not_validated(self, authenticated_client, validation_status):
        offerer = offerers_factories.OffererFactory(validationStatus=validation_status)

        response = self.post_to_endpoint(
            authenticated_client,
            offerer_id=offerer.id,
            form={"comment": "Test", "zendesk_id": "12345", "drive_link": "https://drive.example.com/test"},
            follow_redirects=True,
        )

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "Seule une entité juridique validée peut être fermée"

        db.session.refresh(offerer)
        assert offerer.validationStatus == validation_status

    def test_validate_offerer_returns_404_if_offerer_is_not_found(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, offerer_id=1)

        assert response.status_code == 404


class CreateVenueTest(PostEndpointHelper):
    """
    Create venue without siret based on existing venue with siret.
    """

    endpoint = "backoffice_web.offerer.create_venue"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.CREATE_PRO_ENTITY

    def test_create_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        form_data = {"public_name": "Public Name", "attachement_venue": venue.id}
        response = self.post_to_endpoint(authenticated_client, offerer_id=venue.managingOffererId, form=form_data)
        assert response.status_code == 303

        new_venue: offerers_models.Venue = (
            db.session.query(offerers_models.Venue).filter_by(publicName=form_data["public_name"]).one()
        )
        assert new_venue.name == form_data["public_name"]
        assert new_venue.publicName == form_data["public_name"]
        assert new_venue.venueTypeCode == venue.venueTypeCode
        assert new_venue.isOpenToPublic is False
        assert new_venue.isPermanent is True
        assert new_venue.offererAddress.address == venue.offererAddress.address
        assert new_venue.offererAddress != venue.offererAddress

        assert response.location == url_for("backoffice_web.venue.get", venue_id=new_venue.id)
