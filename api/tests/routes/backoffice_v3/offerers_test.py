import datetime
from operator import attrgetter

from flask import g
from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional import sendinblue_template_ids
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice_v3 import offerers

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


@pytest.fixture(scope="function", name="venue")
def venue_fixture(offerer) -> offerers_models.Venue:
    venue = offerers_factories.VenueFactory(managingOfferer=offerer)
    finance_factories.BankInformationFactory(
        venue=venue,
        status=finance_models.BankInformationStatus.ACCEPTED,
    )
    return venue


@pytest.fixture(scope="function", name="offer")
def offer_fixture(venue) -> offers_models.Offer:
    return offers_factories.OfferFactory(
        venue=venue,
        isActive=True,
        validation=offers_models.OfferValidationStatus.APPROVED.value,
    )


@pytest.fixture(scope="function", name="booking")
def booking_fixture(offer) -> bookings_models.Booking:
    stock = offers_factories.StockFactory(offer=offer)
    return bookings_factories.BookingFactory(
        status=bookings_models.BookingStatus.USED,
        quantity=1,
        amount=10,
        stock=stock,
    )


class GetOffererTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer.get"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_get_offerer(self, authenticated_client, offerer, top_acteur_tag):
        offerers_factories.OffererTagMappingFactory(tagId=top_acteur_tag.id, offererId=offerer.id)

        url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert offerer.name in content
        assert f"Offerer ID : {offerer.id} " in content
        assert f"SIREN : {offerer.siren} " in content
        assert "Région : Occitanie " in content
        assert f"Ville : {offerer.city} " in content
        assert f"Code postal : {offerer.postalCode} " in content
        assert f"Adresse : {offerer.address} " in content
        assert "Présence CB dans les lieux : 0 OK / 0 KO " in content
        assert "Tags structure : Top Acteur " in content

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Structure" in badges
        assert "Validée" in badges
        assert "Suspendue" not in badges

    def test_offerer_detail_contains_venue_bank_information_stats(
        self,
        authenticated_client,
        offerer,
        venue_with_accepted_self_reimbursement_point,
        venue_with_accepted_reimbursement_point,
        venue_with_expired_reimbursement_point,
        venue_with_rejected_bank_info,
        random_venue,
    ):
        # when
        response = authenticated_client.get(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id))

        # then
        assert response.status_code == 200
        assert "Présence CB dans les lieux : 2 OK / 2 KO " in html_parser.content_as_text(response.data)

    def test_offerer_with_educational_venue_has_adage_data(self, authenticated_client, offerer, venue_with_adage_id):
        # when
        response = authenticated_client.get(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id))

        # then
        assert response.status_code == 200
        assert "Référencement Adage : 1/1" in html_parser.content_as_text(response.data)

    def test_offerer_with_no_educational_venue_has_adage_data(
        self, authenticated_client, offerer, venue_with_accepted_bank_info
    ):
        # when
        response = authenticated_client.get(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id))

        # then
        assert response.status_code == 200
        assert "Référencement Adage : 0/1" in html_parser.content_as_text(response.data)


class DeleteOffererTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offerer.delete_offerer"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.DELETE_PRO_ENTITY

    def test_delete_offerer(self, legit_user, authenticated_client):
        offerer_to_delete = offerers_factories.OffererFactory()
        offerer_to_delete_name = offerer_to_delete.name
        offerer_to_delete_id = offerer_to_delete.id

        response = self.delete_offerer(authenticated_client, offerer_to_delete)
        assert response.status_code == 303
        assert offerers_models.Offerer.query.filter(offerers_models.Offerer.id == offerer_to_delete.id).count() == 0

        expected_url = url_for("backoffice_v3_web.search_pro", _external=True)
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

        response = self.delete_offerer(authenticated_client, offerer_to_delete)
        assert response.status_code == 303
        assert offerers_models.Offerer.query.filter(offerers_models.Offerer.id == offerer_to_delete_id).count() == 1

        expected_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_to_delete.id, _external=True)
        assert response.location == expected_url
        response = authenticated_client.get(expected_url)
        assert (
            html_parser.extract_alert(response.data)
            == "Impossible d'effacer une structure juridique pour laquelle il existe des réservations"
        )

    def delete_offerer(self, authenticated_client, offerer_to_delete):
        # generate csrf token
        offerer_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_to_delete.id)
        authenticated_client.get(offerer_url)

        url = url_for("backoffice_v3_web.offerer.delete_offerer", offerer_id=offerer_to_delete.id)

        form = {"csrf_token": g.get("csrf_token", "")}
        return authenticated_client.post(url, form=form)


class UpdateOffererTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offerer.update_offerer"
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
        old_address = offerer_to_edit.address
        new_address = "1 Rue de Siam"

        base_form = {
            "name": new_name,
            "city": new_city,
            "postal_code": new_postal_code,
            "address": new_address,
            "tags": [tag.id for tag in offerer_to_edit.tags],
        }

        response = self.update_offerer(authenticated_client, offerer_to_edit, base_form)
        assert response.status_code == 303

        # Test redirection
        expected_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_to_edit.id, _external=True)
        assert response.location == expected_url

        # Test region update
        response = authenticated_client.get(expected_url)
        assert f"Région : {expected_new_region}" in html_parser.content_as_text(response.data)

        # Test history
        history_url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer_to_edit.id)
        response = authenticated_client.get(history_url)

        offerer_to_edit = offerers_models.Offerer.query.get(offerer_to_edit.id)
        assert offerer_to_edit.name == new_name
        assert offerer_to_edit.city == new_city
        assert offerer_to_edit.postalCode == new_postal_code
        assert offerer_to_edit.address == new_address

        assert len(offerer_to_edit.action_history) == 1
        assert offerer_to_edit.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert offerer_to_edit.action_history[0].authorUser == legit_user
        assert set(offerer_to_edit.action_history[0].extraData["modified_info"].keys()) == {
            "name",
            "city",
            "postalCode",
            "address",
        }

        history_rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(history_rows) == 1
        assert history_rows[0]["Type"] == history_models.ActionType.INFO_MODIFIED.value
        assert f"Nom juridique : {old_name} => {offerer_to_edit.name}" in history_rows[0]["Commentaire"]
        assert f"Ville : {old_city} => {offerer_to_edit.city}" in history_rows[0]["Commentaire"]
        assert f"Code postal : {old_postal_code} => {offerer_to_edit.postalCode}" in history_rows[0]["Commentaire"]
        assert f"Adresse : {old_address} => {offerer_to_edit.address}" in history_rows[0]["Commentaire"]

    def test_update_offerer_tags(self, legit_user, authenticated_client):
        offerer_to_edit = offerers_factories.OffererFactory(
            address="Place de la Liberté", postalCode="29200", city="Brest"
        )
        tag1 = offerers_factories.OffererTagFactory(label="Premier tag")
        tag2 = offerers_factories.OffererTagFactory(label="Deuxième tag")
        tag3 = offerers_factories.OffererTagFactory(label="Troisième tag")
        offerers_factories.OffererTagMappingFactory(tagId=tag1.id, offererId=offerer_to_edit.id)

        base_form = {
            "name": offerer_to_edit.name,
            "city": offerer_to_edit.city,
            "postal_code": offerer_to_edit.postalCode,
            "address": offerer_to_edit.address,
            "tags": [tag2.id, tag3.id],
        }

        response = self.update_offerer(authenticated_client, offerer_to_edit, base_form)
        assert response.status_code == 303

        # Test history
        history_url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer_to_edit.id)
        response = authenticated_client.get(history_url)

        updated_offerer = offerers_models.Offerer.query.get(offerer_to_edit.id)
        assert updated_offerer.city == "Brest"
        assert updated_offerer.postalCode == "29200"
        assert updated_offerer.address == "Place de la Liberté"

        history_rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
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
            "address": offerer.address,
            "tags": [],
        }

        response = self.update_offerer(authenticated_client, offerer, base_form)
        assert response.status_code == 400
        assert "Les données envoyées comportent des erreurs" in html_parser.extract_alert(response.data)

        assert offerer.name == "Original"
        assert len(offerer.action_history) == 0

    def update_offerer(self, authenticated_client, offerer_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_to_edit.id)
        authenticated_client.get(edit_url)

        url = url_for("backoffice_v3_web.offerer.update_offerer", offerer_id=offerer_to_edit.id)

        form["csrf_token"] = g.get("csrf_token", "")
        return authenticated_client.post(url, form=form)


class GetOffererStatsTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer.get_stats"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_get_stats(self, authenticated_client, offerer, offer, booking):
        url = url_for("backoffice_v3_web.offerer.get_stats", offerer_id=offerer.id)

        # get session (1 query)
        # get user with profile and permissions (1 query)
        # get total revenue (1 query)
        # get offerers offers stats (1 query)
        with assert_num_queries(4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = response.data.decode("utf-8")

        # cast to integer to avoid errors due to amount formatting
        assert str(int(booking.amount)) in content
        assert "1 IND" in content  # one active individual offer


class GetOffererStatsDataTest:
    def test_get_data(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
        individual_offerer_bookings,
        collective_offerer_booking,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 2
        assert stats.active.collective == 4
        assert stats.inactive.individual == 3
        assert stats.inactive.collective == 5

        total_revenue = data.total_revenue

        assert total_revenue == 1694.0

    def test_individual_offers_only(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        individual_offerer_bookings,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 2
        assert stats.active.collective == 0
        assert stats.inactive.individual == 3
        assert stats.inactive.collective == 0

        total_revenue = data.total_revenue

        assert total_revenue == 30.0

    def test_collective_offers_only(
        self,
        offerer,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
        collective_offerer_booking,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 0
        assert stats.active.collective == 4
        assert stats.inactive.individual == 0
        assert stats.inactive.collective == 5

        total_revenue = data.total_revenue

        assert total_revenue == 1664.0

    def test_active_offers_only(
        self,
        offerer,
        offerer_active_individual_offers,
        offerer_active_collective_offers,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 2
        assert stats.active.collective == 4
        assert stats.inactive.individual == 0
        assert stats.inactive.collective == 0

        total_revenue = data.total_revenue

        assert total_revenue == 0.0

    def test_inactive_offers_only(
        self,
        offerer,
        offerer_inactive_individual_offers,
        offerer_inactive_collective_offers,
    ):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 0
        assert stats.active.collective == 0
        assert stats.inactive.individual == 3
        assert stats.inactive.collective == 5

        total_revenue = data.total_revenue

        assert total_revenue == 0.0

    def test_no_bookings(self, offerer):
        offerer_id = offerer.id

        # get active/inactive stats (1 query)
        # get total revenue (1 query)
        with assert_num_queries(2):
            data = offerers.get_stats_data(offerer_id)

        stats = data.stats

        assert stats.active.individual == 0
        assert stats.active.collective == 0
        assert stats.inactive.individual == 0
        assert stats.inactive.collective == 0

        total_revenue = data.total_revenue

        assert total_revenue == 0.0


class GetOffererDetailsTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer.get_details"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            offerer = offerers_factories.UserOffererFactory().offerer
            return url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

    def test_get_history(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        action = history_factories.ActionHistoryFactory(offerer=offerer)
        history_factories.ActionHistoryFactory(offerer=offerers_factories.OffererFactory())  # other offerer

        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(rows) == 1
        assert rows[0]["Type"] == history_models.ActionType.COMMENT.value
        assert rows[0]["Commentaire"] == action.comment
        assert rows[0]["Auteur"] == action.authorUser.full_name

    def test_get_history_with_missing_authorId(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        action = history_factories.ActionHistoryFactory(
            offerer=offerer, actionType=history_models.ActionType.OFFERER_NEW, authorUser=None
        )

        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(rows) == 1
        assert rows[0]["Type"] == history_models.ActionType.OFFERER_NEW.value
        assert rows[0]["Commentaire"] == action.comment
        assert not rows[0]["Auteur"]

    def test_no_details_data(self, authenticated_client, offerer):
        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

        # if offerer is not removed from the current session, any get
        # query won't be executed because of this specific testing
        # environment. This would tamper the real database queries
        # count.
        db.session.expire(offerer)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data, parent_class="history-tab-pane") == 0

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
        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 200

        content = response.data.decode("utf-8")

        assert user_offerer_1.user.full_name not in content
        assert user_offerer_2.user.full_name in content

    def test_get_full_sorted_history(self, authenticated_client, legit_user):
        # given
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

        # when
        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=user_offerer.offerer.id)
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
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

    def test_get_pro_users(self, authenticated_client, offerer):
        # given
        uo1 = offerers_factories.UserOffererFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName=None, lastName=None)
        )
        uo2 = offerers_factories.UserOffererFactory(
            offerer=offerer, user=users_factories.ProFactory(firstName="Jean", lastName="Bon")
        )
        uo3 = offerers_factories.NotValidatedUserOffererFactory(offerer=offerer, user=users_factories.ProFactory())

        offerers_factories.UserOffererFactory(user=users_factories.ProFactory())

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data, "pro-users-tab-pane")
        assert len(rows) == 3

        assert rows[0]["ID"] == str(uo1.user.id)
        assert rows[0]["Statut"] == "Validé"
        assert rows[0]["Nom"] == ""
        assert rows[0]["Prénom"] == ""
        assert rows[0]["Email"] == uo1.user.email

        assert rows[1]["ID"] == str(uo2.user.id)
        assert rows[1]["Statut"] == "Validé"
        assert rows[1]["Nom"] == uo2.user.lastName
        assert rows[1]["Prénom"] == uo2.user.firstName
        assert rows[1]["Email"] == uo2.user.email

        assert rows[2]["ID"] == str(uo3.user.id)
        assert rows[2]["Statut"] == "Nouveau"
        assert rows[2]["Nom"] == uo3.user.lastName
        assert rows[2]["Prénom"] == uo3.user.firstName
        assert rows[2]["Email"] == uo3.user.email

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

        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200

        parsed_html = html_parser.get_soup(response.data)
        select = parsed_html.find("select", attrs={"name": "pro_user_id"})
        options = select.find_all("option")
        assert [option["value"] for option in options] == ["", str(user3.id), str(user2.id)]

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_get_managed_venues(self, authenticated_client, offerer):
        other_offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        educational_factories.CollectiveDmsApplicationFactory(venue=venue_2)
        offerers_factories.VenueFactory(managingOfferer=other_offerer)

        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, "managed-venues-tab-pane")
        assert len(rows) == 2

        # Sort before checking rows data to avoid flaky test
        rows = sorted(rows, key=lambda row: int(row["ID"]))

        assert rows[0]["ID"] == str(venue_1.id)
        assert rows[0]["SIRET"] == venue_1.siret
        assert rows[0]["Nom"] == venue_1.name
        assert rows[0]["Activité principale"] == venue_1.venueTypeCode.value
        assert not rows[0].get("Type de lieu")
        assert rows[0]["Statut du dossier DMS Adage"] == ""

        assert rows[1]["ID"] == str(venue_2.id)
        assert rows[1]["SIRET"] == venue_2.siret
        assert rows[1]["Nom"] == venue_2.name
        assert rows[1]["Activité principale"] == venue_2.venueTypeCode.value
        assert not rows[1].get("Type de lieu")
        assert rows[1]["Statut du dossier DMS Adage"] == "En construction"

    @override_features(WIP_ENABLE_NEW_ONBOARDING=False)
    def test_get_managed_venues_ff_off(self, authenticated_client, offerer):
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        url = url_for("backoffice_v3_web.offerer.get_details", offerer_id=offerer.id)

        response = authenticated_client.get(url)

        rows = html_parser.extract_table_rows(response.data, "managed-venues-tab-pane")
        assert rows[0]["Type de lieu"] == venue.venueTypeCode.value
        assert not rows[0].get("Activité principale")


class GetOffererHistoryDataTest:
    def test_one_action(self):
        user_offerer = offerers_factories.UserOffererFactory()
        action = history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 13, 1),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=user_offerer.user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment=None,
        )

        # load with joinedload
        offerer = offerers.get_offerer(user_offerer.offererId)

        with assert_num_queries(0):
            history = offerers.get_offerer_history_data(offerer)

        assert len(history) == 1

        found_action = history[0]

        assert found_action.actionType.value == action.actionType.value
        assert found_action.actionDate == action.actionDate
        assert found_action.authorUser.full_name == action.authorUser.full_name

    def test_no_action(self, offerer):
        assert not offerers.get_offerer_history_data(offerer)

    def test_many_actions(self):
        user_offerer = offerers_factories.UserOffererFactory()
        actions = history_factories.ActionHistoryFactory.create_batch(
            3,
            authorUser=user_offerer.user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
        )

        offerer = user_offerer.offerer

        history = offerers.get_offerer_history_data(offerer)
        assert len(history) == len(actions)

        found_comments = {event.comment for event in history}
        expected_comments = {event.comment for event in actions}

        assert found_comments == expected_comments


class CommentOffererTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf, unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.offerer.comment_offerer"
        endpoint_kwargs = {"offerer_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_add_comment(self, authenticated_client, legit_user, offerer):
        comment = "Code APE non éligible"
        response = self.send_comment_offerer_request(authenticated_client, offerer, comment)

        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id, _external=True)
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
        response = self.send_comment_offerer_request(authenticated_client, offerer, "")

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert "Les données envoyées comportent des erreurs" in redirected_response.data.decode("utf8")

    def send_comment_offerer_request(self, authenticated_client, offerer, comment):
        # generate and fetch (inside g) csrf token
        offerer_detail_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer.id)
        authenticated_client.get(offerer_detail_url)

        url = url_for("backoffice_v3_web.offerer.comment_offerer", offerer_id=offerer.id)
        form = {"comment": comment, "csrf_token": g.get("csrf_token", "")}

        return authenticated_client.post(url, form=form)


class ListOfferersToValidateUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.validation.list_offerers_to_validate"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ListOfferersToValidateTest:
    class ListOfferersToBeValidatedTest:
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
            # given
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

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", order=order, sort=sort)
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            # Without sort, table is ordered by dateCreated desc
            to_be_validated_offerers.sort(
                key=attrgetter(sort or "dateCreated"), reverse=(order == "desc") if sort else True
            )
            assert [row[row_key] for row in rows] == [
                offerer.dateCreated.strftime("%d/%m/%Y") for offerer in to_be_validated_offerers
            ]

        @pytest.mark.parametrize(
            "validation_status,expected_status",
            [
                (ValidationStatus.NEW, "Nouvelle"),
                (ValidationStatus.PENDING, "En attente"),
            ],
        )
        def test_payload_content(self, authenticated_client, validation_status, expected_status, top_acteur_tag):
            # given
            user_offerer = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
                offerer__validationStatus=validation_status,
                user__phoneNumber="+33610203040",
            )
            tag = offerers_factories.OffererTagFactory(label="Magic Tag")
            category = offerers_models.OffererTagCategory.query.filter(
                offerers_models.OffererTagCategory.name == "homologation"
            ).one()
            offerers_factories.OffererTagCategoryMappingFactory(tagId=tag.id, categoryId=category.id)
            offerers_factories.OffererTagMappingFactory(tagId=tag.id, offererId=user_offerer.offerer.id)

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

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(url_for("backoffice_v3_web.validation.list_offerers_to_validate"))

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Nom de la structure"] == user_offerer.offerer.name
            assert rows[0]["État"] == expected_status
            assert rows[0]["Top Acteur"] == ""  # no text
            assert rows[0]["Tags structure"] == tag.label
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Dernier commentaire"] == "Houlala"
            assert rows[0]["SIREN"] == user_offerer.offerer.siren
            assert rows[0]["Email"] == user_offerer.offerer.first_user.email
            assert rows[0]["Responsable Structure"] == user_offerer.offerer.first_user.full_name
            assert rows[0]["Ville"] == user_offerer.offerer.city

            dms_adage_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")
            assert dms_adage_data == []

        def test_payload_content_no_action(self, authenticated_client):
            # given
            user_offerer = offerers_factories.UserNotValidatedOffererFactory(
                offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
            )

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(url_for("backoffice_v3_web.validation.list_offerers_to_validate"))

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)
            assert rows[0]["Nom de la structure"] == user_offerer.offerer.name
            assert rows[0]["État"] == "Nouvelle"
            assert rows[0]["Date de la demande"] == "03/10/2022"
            assert rows[0]["Dernier commentaire"] == ""

        def test_dms_adage_additional_data(self, authenticated_client):
            # given
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
            educational_factories.CollectiveDmsApplicationFactory(venue=venue, state="accepte")
            other_venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
            educational_factories.CollectiveDmsApplicationFactory(venue=other_venue, state="accepte")

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(url_for("backoffice_v3_web.validation.list_offerers_to_validate"))

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert len(rows) == 1
            assert rows[0]["ID"] == str(user_offerer.offerer.id)

            dms_adage_data = html_parser.extract(response.data, tag="tr", class_="collapse accordion-collapse")[0]
            assert f"Nom : {venue.name}" in dms_adage_data
            assert f"SIRET : {venue.siret}" in dms_adage_data
            assert "Statut du dossier DMS Adage : Accepté" in dms_adage_data

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
            # given
            for _ in range(total_items):
                offerers_factories.UserNotValidatedOffererFactory()

            # when
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_to_validate", **pagination_config)
            )

            # then
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
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", regions=region_filter)
                )

            # then
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
            ),
        )
        def test_list_filtering_by_tags(
            self, authenticated_client, tag_filter, expected_offerer_names, offerers_to_be_validated
        ):
            # given
            tags = (
                offerers_models.OffererTag.query.filter(offerers_models.OffererTag.label.in_(tag_filter))
                .with_entities(offerers_models.OffererTag.id)
                .all()
            )
            tags_ids = [_id for _id, in tags]

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", tags=tags_ids)
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == expected_offerer_names

        def test_list_filtering_by_date(self, authenticated_client):
            # given
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

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for(
                        "backoffice_v3_web.validation.list_offerers_to_validate",
                        from_date="2022-11-05",
                        to_date="2022-11-08",
                    )
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert [int(row["ID"]) for row in rows] == [uo.offerer.id for uo in (user_offerer_3, user_offerer_2)]

        def test_list_filtering_by_invalid_date(self, authenticated_client):
            # given

            # when
            response = authenticated_client.get(
                url_for(
                    "backoffice_v3_web.validation.list_offerers_to_validate",
                    from_date="05/11/2022",
                )
            )

            # then
            assert response.status_code == 400
            assert "Date invalide" in response.data.decode("utf-8")

        @pytest.mark.parametrize("search", ["123004004", "  123004004 ", "123004004\n"])
        def test_list_search_by_siren(self, authenticated_client, offerers_to_be_validated, search):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", q=search)
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"D"}

        def test_list_search_by_postal_code(self, authenticated_client, offerers_to_be_validated):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", q="35400")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"E"}

        def test_list_search_by_department_code(self, authenticated_client, offerers_to_be_validated):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", q="35")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"A", "E"}

        def test_list_search_by_city(self, authenticated_client, offerers_to_be_validated):
            # Ensure that outerjoin does not cause too many rows returned
            offerers_factories.UserOffererFactory.create_batch(3, offerer=offerers_to_be_validated[1])

            # Search "quimper" => results include "Quimper" and "Quimperlé"
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", q="quimper")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"B", "D"}
            assert html_parser.extract_pagination_info(response.data) == (1, 1, 2)

        @pytest.mark.parametrize("search", ["1", "1234", "123456", "1234567", "12345678", "12345678912345", "  1234"])
        def test_list_search_by_invalid_number_of_digits(self, authenticated_client, search):
            # when
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_to_validate", q=search)
            )

            # then
            assert response.status_code == 400
            assert (
                "Le nombre de chiffres ne correspond pas à un SIREN, code postal ou département"
                in response.data.decode("utf-8")
            )

        def test_list_search_by_email(self, authenticated_client, offerers_to_be_validated):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", q="sadi@example.com")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"B"}

        def test_list_search_by_user_name(self, authenticated_client, offerers_to_be_validated):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", q="Felix faure")
                )

            # then
            assert response.status_code == 200
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Nom de la structure"] for row in rows} == {"C"}

        @pytest.mark.parametrize(
            "search_filter, expected_offerer_names",
            (
                ("cinema de la plage", {"Cinéma de la Petite Plage", "Cinéma de la Grande Plage"}),
                ("cinéma", {"Cinéma de la Petite Plage", "Cinéma de la Grande Plage", "Cinéma du Centre"}),
                ("Plage", {"Librairie de la Plage", "Cinéma de la Petite Plage", "Cinéma de la Grande Plage"}),
                ("Librairie du Centre", set()),
            ),
        )
        def test_list_search_by_name(self, authenticated_client, search_filter, expected_offerer_names):
            # given
            for name in (
                "Librairie de la Plage",
                "Cinéma de la Petite Plage",
                "Cinéma du Centre",
                "Cinéma de la Grande Plage",
            ):
                offerers_factories.NotValidatedOffererFactory(name=name)

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", q=search_filter)
                )

            # then
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
                (None, 200, {"A", "B", "C", "D", "E", "F"}),  # same as default
                ("OTHER", 400, set()),  # unknown value
                (["REJECTED", "OTHER"], 400, set()),
            ),
        )
        def test_list_filtering_by_status(
            self, authenticated_client, status_filter, expected_status, expected_offerer_names, offerers_to_be_validated
        ):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(
                    url_for("backoffice_v3_web.validation.list_offerers_to_validate", status=status_filter)
                )

            # then
            assert response.status_code == expected_status
            if expected_status == 200:
                rows = html_parser.extract_table_rows(response.data)
                assert {row["Nom de la structure"] for row in rows} == expected_offerer_names
            else:
                assert html_parser.count_table_rows(response.data) == 0

        def test_offerers_stats_are_displayed(self, authenticated_client, offerers_to_be_validated):
            # given
            offerers_factories.UserOffererFactory(offerer__validationStatus=ValidationStatus.PENDING)
            offerers_factories.UserOffererFactory(offerer__validationStatus=ValidationStatus.REJECTED)

            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(url_for("backoffice_v3_web.validation.list_offerers_to_validate"))

            # then
            assert response.status_code == 200
            cards = html_parser.extract_cards_text(response.data)
            assert "3 nouvelles structures" in cards
            assert "4 structures en attente" in cards
            assert "1 structure validée" in cards
            assert "2 structures rejetées" in cards

        def test_no_offerer(self, authenticated_client):
            # when
            with assert_no_duplicated_queries():
                response = authenticated_client.get(url_for("backoffice_v3_web.validation.list_offerers_to_validate"))

            # then
            assert response.status_code == 200
            cards = html_parser.extract_cards_text(response.data)
            assert "0 nouvelle structure" in cards
            assert "0 structure en attente" in cards
            assert "0 structure validée" in cards
            assert "0 structure rejetée" in cards
            assert html_parser.count_table_rows(response.data) == 0


class ValidateOffererUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.validate_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ValidateOffererTest:
    def test_validate_offerer(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.validate_offerer", offerer_id=user_offerer.offerer.id)
        response = send_request(authenticated_client, user_offerer.offererId, url)

        # then
        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.offerer.isValidated
        assert user_offerer.user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    def test_validate_offerer_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # when
        url = url_for("backoffice_v3_web.validation.validate_offerer", offerer_id=1)
        response = send_request(authenticated_client, 1, url)

        # then
        assert response.status_code == 404

    def test_cannot_validate_offerer_already_validated(self, authenticated_client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.validate_offerer", offerer_id=user_offerer.offerer.id)
        response = send_request(authenticated_client, user_offerer.offererId, url)

        # then
        assert response.status_code == 303

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà validée" in redirected_response.data.decode("utf8")


class GetRejectOffererFormUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.get_reject_offerer_form"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class GetRejectOffererFormTest:
    def test_get_reject_offerer_form(self, legit_user, authenticated_client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.get_reject_offerer_form", offerer_id=offerer.id)
        response = authenticated_client.get(url)

        # then
        # Rendering is not checked, but at least the fetched frame does not crash
        assert response.status_code == 200


class RejectOffererUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.reject_offerer"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class RejectOffererTest:
    def test_reject_offerer(self, legit_user, authenticated_client):
        # given
        user = users_factories.UserFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # deleted when rejected

        # when
        url = url_for("backoffice_v3_web.validation.reject_offerer", offerer_id=offerer.id)
        response = send_request(authenticated_client, offerer.id, url)

        # then
        assert response.status_code == 303

        db.session.refresh(user)
        db.session.refresh(offerer)
        assert not offerer.isValidated
        assert offerer.isRejected
        assert not user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

    def test_reject_offerer_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # when
        url = url_for("backoffice_v3_web.validation.reject_offerer", offerer_id=1)
        response = send_request(authenticated_client, 1, url)

        # then
        assert response.status_code == 404

    def test_cannot_reject_offerer_already_rejected(self, authenticated_client):
        # given
        offerer = offerers_factories.OffererFactory(validationStatus=ValidationStatus.REJECTED)

        # when
        url = url_for("backoffice_v3_web.validation.reject_offerer", offerer_id=offerer.id)
        response = send_request(authenticated_client, offerer.id, url)

        # then
        assert response.status_code == 303

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà rejetée" in redirected_response.data.decode("utf8")


class GetOffererPendingFormUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.get_offerer_pending_form"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class GetOffererPendingFormTest:
    def test_get_offerer_pending_form(self, legit_user, authenticated_client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.get_offerer_pending_form", offerer_id=offerer.id)
        response = authenticated_client.get(url)

        # then
        # Rendering is not checked, but at least the fetched frame does not crash
        assert response.status_code == 200


class SetOffererPendingUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.set_offerer_pending"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class SetOffererPendingTest:
    def test_set_offerer_pending(self, legit_user, authenticated_client, offerer_tags):
        # given
        non_homologation_tag = offerers_factories.OffererTagFactory(name="Tag conservé")
        offerer = offerers_factories.NotValidatedOffererFactory(
            tags=[non_homologation_tag, offerer_tags[0], offerer_tags[1]]
        )

        # when
        url = url_for("backoffice_v3_web.validation.set_offerer_pending", offerer_id=offerer.id)
        response = send_request(
            authenticated_client,
            offerer.id,
            url,
            {"comment": "En attente de documents", "tags": [offerer_tags[0].id, offerer_tags[2].id]},
        )

        # then
        assert response.status_code == 303

        db.session.refresh(offerer)
        assert not offerer.isValidated
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

    def test_set_offerer_pending_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # when
        url = url_for("backoffice_v3_web.validation.set_offerer_pending", offerer_id=1)
        response = send_request(authenticated_client, 1, url, {"comment": "Questionnaire"})
        # then
        assert response.status_code == 404


class ToggleTopActorUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.toggle_top_actor"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ToggleTopActorTest:
    def test_toggle_is_top_actor(self, authenticated_client, top_acteur_tag):
        # given
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer

        # when
        url = url_for("backoffice_v3_web.validation.toggle_top_actor", offerer_id=offerer.id)
        response = send_request(authenticated_client, offerer.id, url, {"is_top_actor": "on"})

        # then
        assert response.status_code == 303
        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == top_acteur_tag.id
        assert offerer_mappings[0].offererId == offerer.id

        # when
        url = url_for("backoffice_v3_web.validation.toggle_top_actor", offerer_id=offerer.id)
        response = send_request(authenticated_client, offerer.id, url)

        # then
        assert response.status_code == 303
        assert offerers_models.OffererTagMapping.query.count() == 0

    def test_toggle_is_top_actor_twice_true(self, authenticated_client, top_acteur_tag):
        # given
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer

        # when
        for _ in range(2):
            url = url_for("backoffice_v3_web.validation.toggle_top_actor", offerer_id=offerer.id)
            response = send_request(authenticated_client, offerer.id, url, {"is_top_actor": "on"})

            # then
            assert response.status_code == 303

        # then
        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == top_acteur_tag.id
        assert offerer_mappings[0].offererId == offerer.id

    def test_toggle_top_actor_returns_404_if_offerer_is_not_found(self, authenticated_client):
        # given

        # when
        url = url_for("backoffice_v3_web.validation.toggle_top_actor", offerer_id=1)
        response = send_request(authenticated_client, 1, url, {"is_top_actor": "on"})
        # then
        assert response.status_code == 404


class ListUserOffererToValidateUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.validation.list_offerers_attachments_to_validate"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ListUserOffererToValidateTest:
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
        # given
        to_be_validated = []
        for _ in range(2):
            validated_user_offerer = offerers_factories.UserOffererFactory()
            new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(offerer=validated_user_offerer.offerer)
            to_be_validated.append(new_user_offerer)
            pending_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
                offerer=validated_user_offerer.offerer, validationStatus=ValidationStatus.PENDING
            )
            to_be_validated.append(pending_user_offerer)

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", order=order, sort=sort)
            )

        # then
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

    @pytest.mark.parametrize(
        "validation_status,expected_status",
        [
            (ValidationStatus.NEW, "Nouveau"),
            (ValidationStatus.PENDING, "En attente"),
        ],
    )
    def test_payload_content(self, authenticated_client, validation_status, expected_status):
        # given
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 2, 11, 30),
            dateCreated=datetime.datetime(2022, 11, 2, 11, 59),
        )
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer,
            validationStatus=validation_status,
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
            comment="Bla blabla" if validation_status == ValidationStatus.NEW else "Premier",
        )
        if validation_status == ValidationStatus.PENDING:
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 11, 5, 14, 2),
                actionType=history_models.ActionType.USER_OFFERER_PENDING,
                authorUser=commenter,
                offerer=new_user_offerer.offerer,
                user=new_user_offerer.user,
                comment="Bla blabla",
            )

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID Compte pro"] == str(new_user_offerer.user.id)
        assert rows[0]["Email Compte pro"] == new_user_offerer.user.email
        assert rows[0]["Nom Compte pro"] == new_user_offerer.user.full_name
        assert rows[0]["État"] == expected_status
        assert rows[0]["Date de la demande"] == "03/11/2022"
        assert rows[0]["Dernier commentaire"] == "Bla blabla"
        assert rows[0]["Tél Compte pro"] == new_user_offerer.user.phoneNumber
        assert rows[0]["Nom Structure"] == owner_user_offerer.offerer.name
        assert rows[0]["Date de création Structure"] == "02/11/2022"
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["SIREN"] == owner_user_offerer.offerer.siren

    def test_payload_content_no_action(self, authenticated_client):
        # given
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 3), dateCreated=datetime.datetime(2022, 11, 24)
        )
        offerers_factories.UserOffererFactory(offerer=owner_user_offerer.offerer)  # other validated, not owner
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer, dateCreated=datetime.datetime(2022, 11, 25)
        )

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID Compte pro"] == str(new_user_offerer.user.id)
        assert rows[0]["Email Compte pro"] == new_user_offerer.user.email
        assert rows[0]["Nom Compte pro"] == new_user_offerer.user.full_name
        assert rows[0]["État"] == "Nouveau"
        assert rows[0]["Date de la demande"] == "25/11/2022"
        assert rows[0]["Dernier commentaire"] == ""
        assert rows[0]["Tél Compte pro"] == ""
        assert rows[0]["Nom Structure"] == owner_user_offerer.offerer.name
        assert rows[0]["Date de création Structure"] == "03/11/2022"
        assert rows[0]["Email Responsable"] == owner_user_offerer.user.email
        assert rows[0]["SIREN"] == owner_user_offerer.offerer.siren

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
        # given
        for _ in range(total_items):
            offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = authenticated_client.get(
            url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", **pagination_config)
        )

        # then
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
                {"a@example.com", "b@example.com", "c@example.com", "d@example.com", "e@example.com", "f@example.com"},
            ),  # same as default
            ("OTHER", 400, set()),  # unknown value
        ),
    )
    def test_list_filtering_by_status(
        self, authenticated_client, status_filter, expected_status, expected_users_emails, user_offerer_to_be_validated
    ):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", status=status_filter)
            )

        # then
        assert response.status_code == expected_status
        if expected_status == 200:
            rows = html_parser.extract_table_rows(response.data)
            assert {row["Email Compte pro"] for row in rows} == expected_users_emails
        else:
            assert html_parser.count_table_rows(response.data) == 0

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
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for(
                    "backoffice_v3_web.validation.list_offerers_attachments_to_validate",
                    offerer_status=offerer_status_filter,
                )
            )

        # then
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
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", regions=region_filter)
            )

        # then
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
        # given
        tags = (
            offerers_models.OffererTag.query.filter(offerers_models.OffererTag.label.in_(tag_filter))
            .with_entities(offerers_models.OffererTag.id)
            .all()
        )
        tags_ids = [_id for _id, in tags]

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", tags=tags_ids)
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == expected_users_emails

    def test_list_filtering_by_date(self, authenticated_client):
        # given
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

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for(
                    "backoffice_v3_web.validation.list_offerers_attachments_to_validate",
                    from_date="2022-11-25",
                    to_date="2022-11-25",
                )
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert [int(row["ID Compte pro"]) for row in rows] == [uo.user.id for uo in (user_offerer_3, user_offerer_2)]

    def test_list_search_by_postal_code(self, authenticated_client, user_offerer_to_be_validated):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", q="97100")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"b@example.com"}

    def test_list_search_by_department_code(self, authenticated_client, user_offerer_to_be_validated):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", q="972")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"a@example.com", "d@example.com"}

    def test_list_search_by_city(self, authenticated_client, user_offerer_to_be_validated):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", q="Fort De France")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"a@example.com"}

    def test_list_search_by_email(self, authenticated_client, user_offerer_to_be_validated):
        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(
                url_for("backoffice_v3_web.validation.list_offerers_attachments_to_validate", q="b@example.com")
            )

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert {row["Email Compte pro"] for row in rows} == {"b@example.com"}


class ValidateOffererAttachmentUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.validate_user_offerer"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class ValidateOffererAttachmentTest:
    def test_validate_offerer_attachment(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.validate_user_offerer", user_offerer_id=user_offerer.id)
        response = send_request(authenticated_client, user_offerer.offererId, url)

        # then
        assert response.status_code == 303

        db.session.refresh(user_offerer)
        assert user_offerer.isValidated
        assert user_offerer.user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == user_offerer.user.email
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value.__dict__
        )

    def test_validate_offerer_attachment_returns_404_if_offerer_is_not_found(self, authenticated_client, offerer):
        # when
        url = url_for("backoffice_v3_web.validation.validate_user_offerer", user_offerer_id=42)
        response = send_request(authenticated_client, offerer.id, url)

        # then
        assert response.status_code == 404

    def test_cannot_validate_offerer_attachment_already_validated(self, authenticated_client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.validate_user_offerer", user_offerer_id=user_offerer.id)
        response = send_request(authenticated_client, user_offerer.offererId, url)

        # then
        assert response.status_code == 303

        redirected_response = authenticated_client.get(response.headers["location"])
        assert "est déjà validé" in redirected_response.data.decode("utf8")


class GetRejectOffererAttachmentFormUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.get_reject_user_offerer_form"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class GetRejectOffererAttachmentFormTest:
    def test_get_reject_offerer_attachment_form(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.get_reject_user_offerer_form", user_offerer_id=user_offerer.id)
        response = authenticated_client.get(url)

        # then
        # Rendering is not checked, but at least the fetched frame does not crash
        assert response.status_code == 200


class RejectOffererAttachmentUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.reject_user_offerer"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class RejectOffererAttachmentTest:
    def test_reject_offerer_attachment(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.reject_user_offerer", user_offerer_id=user_offerer.id)
        response = send_request(authenticated_client, user_offerer.offererId, url)

        # then
        assert response.status_code == 303

        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 0

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == user_offerer.user.email
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_REJECTION.value.__dict__
        )

    def test_reject_offerer_returns_404_if_offerer_attachment_is_not_found(self, authenticated_client, offerer):
        # when
        url = url_for("backoffice_v3_web.validation.reject_user_offerer", user_offerer_id=42)
        response = send_request(authenticated_client, offerer.id, url)

        # then
        assert response.status_code == 404


class GetOffererAttachmentPendingFormUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.get_user_offerer_pending_form"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class GetOffererAttachmentPendingFormTest:
    def test_get_offerer_attachment_pending_form(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.get_user_offerer_pending_form", user_offerer_id=user_offerer.id)
        response = authenticated_client.get(url)

        # then
        # Rendering is not checked, but at least the fetched frame does not crash
        assert response.status_code == 200


class SetOffererAttachmentPendingUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.set_user_offerer_pending"
    endpoint_kwargs = {"user_offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class SetOffererAttachmentPendingTest:
    def test_set_offerer_attachment_pending(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        url = url_for("backoffice_v3_web.validation.set_user_offerer_pending", user_offerer_id=user_offerer.id)
        response = send_request(
            authenticated_client, user_offerer.offererId, url, {"comment": "En attente de documents"}
        )

        # then
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


class AddUserOffererAndValidateUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.offerer.add_user_offerer_and_validate"
    endpoint_kwargs = {"offerer_id": 1}
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class AddUserOffererAndValidateTest:
    endpoint = "backoffice_v3_web.offerer.add_user_offerer_and_validate"

    def test_add_user_offerer_and_validate(self, legit_user, authenticated_client):
        # given
        offerer = offerers_factories.UserOffererFactory().offerer
        user = users_factories.UserFactory()
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED,
            authorUser=legit_user,
            offerer=offerer,
            user=user,
        )

        # when
        response = send_request(
            authenticated_client,
            offerer.id,
            url_for(self.endpoint, offerer_id=offerer.id),
            {"pro_user_id": user.id, "comment": "Le rattachement avait été rejeté par erreur"},
        )

        # then
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
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value.__dict__
        )

    def test_add_existing_user_offerer(self, legit_user, authenticated_client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = send_request(
            authenticated_client,
            user_offerer.offererId,
            url_for(self.endpoint, offerer_id=user_offerer.offererId),
            {"pro_user_id": user_offerer.userId, "comment": "test"},
        )

        # then
        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == "Les données envoyées comportent des erreurs"

        assert offerers_models.UserOfferer.query.count() == 1  # existing before request
        assert history_models.ActionHistory.query.count() == 0
        assert len(mails_testing.outbox) == 0

    def test_add_user_not_related(self, legit_user, authenticated_client):
        # given
        offerer = offerers_factories.UserOffererFactory().offerer
        user = users_factories.UserFactory()

        # when
        response = send_request(
            authenticated_client,
            offerer.id,
            url_for(self.endpoint, offerer_id=offerer.id),
            {"pro_user_id": user.id, "comment": "test"},
        )

        # then
        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == "Les données envoyées comportent des erreurs"

    def test_add_user_empty(self, legit_user, authenticated_client):
        # given
        offerer = offerers_factories.UserOffererFactory().offerer
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED,
            authorUser=legit_user,
            offerer=offerer,
            user=users_factories.UserFactory(),
        )

        # when
        response = send_request(
            authenticated_client,
            offerer.id,
            url_for(self.endpoint, offerer_id=offerer.id),
            {"pro_user_id": 0, "comment": "test"},
        )

        # then
        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.headers["location"])
        assert html_parser.extract_alert(redirected_response.data) == "Les données envoyées comportent des erreurs"


class SetBatchOffererAttachmentPendingUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.batch_set_user_offerer_pending"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class SetBatchOffererAttachmentPendingTest:
    def test_batch_set_offerer_attachment_pending(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NotValidatedUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        url = url_for("backoffice_v3_web.validation.batch_set_user_offerer_pending")
        response = send_request(
            authenticated_client,
            user_offerers[0].offerer.id,
            url,
            {"object_ids": parameter_ids, "comment": "test comment"},
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


class BatchOffererAttachmentValidateUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.batch_validate_user_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class BatchOffererAttachmentValidateTest:
    def test_batch_set_offerer_attachment_validate(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NotValidatedUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        url = url_for("backoffice_v3_web.validation.batch_validate_user_offerer")
        response = send_request(
            authenticated_client,
            user_offerers[0].offerer.id,
            url,
            {"object_ids": parameter_ids, "comment": "test comment"},
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
        assert {mail.sent_data["To"] for mail in mails_testing.outbox} == {
            user_offerer.user.email for user_offerer in user_offerers
        }
        for mail in mails_testing.outbox:
            assert (
                mail.sent_data["template"]
                == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_VALIDATION.value.__dict__
            )


class BatchOffererAttachmentRejectUnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
    method = "post"
    endpoint = "backoffice_v3_web.validation.batch_reject_user_offerer"
    needed_permission = perm_models.Permissions.VALIDATE_OFFERER


class BatchOffererAttachmentRejectTest:
    def test_batch_set_offerer_attachment_reject(self, legit_user, authenticated_client):
        user_offerers = offerers_factories.NotValidatedUserOffererFactory.create_batch(10)
        parameter_ids = ",".join(str(user_offerer.id) for user_offerer in user_offerers)
        url = url_for("backoffice_v3_web.validation.batch_reject_user_offerer")
        response = send_request(
            authenticated_client,
            user_offerers[0].offerer.id,
            url,
            {"object_ids": parameter_ids, "comment": "test comment"},
        )

        assert response.status_code == 303
        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 0

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
            assert action.venueId is None

        assert len(mails_testing.outbox) == len(user_offerers)

        # emails are not sorted by user_offerers
        assert {mail.sent_data["To"] for mail in mails_testing.outbox} == {
            user_offerer.user.email for user_offerer in user_offerers
        }
        for mail in mails_testing.outbox:
            assert (
                mail.sent_data["template"]
                == sendinblue_template_ids.TransactionalEmail.OFFERER_ATTACHMENT_REJECTION.value.__dict__
            )


def send_request(authenticated_client, offerer_id, url, form_data=None):
    # generate and fetch (inside g) csrf token
    offerer_detail_url = url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_id)
    authenticated_client.get(offerer_detail_url)

    form_data = form_data if form_data else {}
    form = {"csrf_token": g.get("csrf_token", ""), **form_data}

    return authenticated_client.post(url, form=form)


class ListOffererTagsTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.offerer_tag.list_offerer_tags"
        needed_permission = perm_models.Permissions.MANAGE_OFFERER_TAG

    def test_list_offerer_tags(self, authenticated_client):
        # given
        category = offerers_factories.OffererTagCategoryFactory(label="indépendant")
        offerer_tag = offerers_factories.OffererTagFactory(
            name="scottish-tag",
            label="Taggy McTagface",
            description="FREEDOOOOOOOOOM",
            categories=[category],
        )

        # when
        with assert_no_duplicated_queries():
            response = authenticated_client.get(url_for("backoffice_v3_web.offerer_tag.list_offerer_tags"))

        # then
        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom"] == offerer_tag.name
        assert rows[0]["Libellé"] == offerer_tag.label
        assert rows[0]["Description"] == offerer_tag.description
        assert rows[0]["Catégories"] == category.label


class UpdateOffererTagTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offerer_tag.update_offerer_tag"
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
        response = self.update_offerer_tag(authenticated_client, offerer_tag_to_edit, base_form)
        assert response.status_code == 303

        # Test redirection
        expected_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags", _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(expected_url)

        rows = html_parser.extract_table_rows(response.data)
        assert html_parser.count_table_rows(response.data) == 2
        assert rows[0]["Nom"] == new_name
        assert rows[0]["Libellé"] == new_label
        assert rows[0]["Description"] == new_description
        assert rows[0]["Catégories"] == ", ".join([category_to_keep.label, category_to_add.label])

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
        response = self.update_offerer_tag(authenticated_client, offerer_tag_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags", _external=True)
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

        response = self.update_offerer_tag(authenticated_client, offerer_tag_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags", _external=True)
        response = authenticated_client.get(expected_url)

        assert html_parser.extract_alert(response.data) == "Ce nom de tag existe déjà"
        assert offerer_tag_to_edit.name == "a-silly-name"

    def update_offerer_tag(self, authenticated_client, offerer_tag_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags")
        authenticated_client.get(edit_url)

        url = url_for("backoffice_v3_web.offerer_tag.update_offerer_tag", offerer_tag_id=offerer_tag_to_edit.id)

        form["csrf_token"] = g.get("csrf_token", "")
        return authenticated_client.post(url, form=form)


class CreateOffererTagTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offerer_tag.create_offerer_tag"
        needed_permission = perm_models.Permissions.MANAGE_OFFERER_TAG

    def test_create_offerer(self, authenticated_client):
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
        response = self.create_offerer_tag(authenticated_client, base_form)
        assert response.status_code == 303

        # Test redirection
        expected_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags", _external=True)
        assert response.location == expected_url

        response = authenticated_client.get(expected_url)

        rows = html_parser.extract_table_rows(response.data)
        assert html_parser.count_table_rows(response.data) == 1
        assert rows[0]["Nom"] == name
        assert rows[0]["Libellé"] == label
        assert rows[0]["Description"] == description
        assert rows[0]["Catégories"] == category.label

    def test_create_with_wrong_data(self, authenticated_client):
        base_form = {
            "name": "",
            "label": "Mon nom est Personne",
        }
        response = self.create_offerer_tag(authenticated_client, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags", _external=True)
        response = authenticated_client.get(expected_url)

        assert "Les données envoyées comportent des erreurs" in html_parser.extract_alert(response.data)
        assert html_parser.count_table_rows(response.data) == 0

    def test_create_with_already_existing_tag(self, authenticated_client):
        offerers_factories.OffererTagFactory(
            name="i-was-here-first",
        )
        base_form = {
            "name": "i-was-here-first",
        }
        response = self.create_offerer_tag(authenticated_client, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags", _external=True)
        response = authenticated_client.get(expected_url)

        assert html_parser.extract_alert(response.data) == "Ce tag existe déjà"
        assert html_parser.count_table_rows(response.data) == 1

    def create_offerer_tag(self, authenticated_client, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.offerer_tag.list_offerer_tags")
        authenticated_client.get(edit_url)

        url = url_for("backoffice_v3_web.offerer_tag.create_offerer_tag")

        form["csrf_token"] = g.get("csrf_token", "")
        return authenticated_client.post(url, form=form)


class DeleteOffererTagTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        method = "post"
        endpoint = "backoffice_v3_web.offerer_tag.delete_offerer_tag"
        endpoint_kwargs = {"offerer_tag_id": 1}
        needed_permission = perm_models.Permissions.DELETE_OFFERER_TAG

    def test_delete_offerer_tag(self, authenticated_client):
        tags = offerers_factories.OffererTagFactory.create_batch(3)
        offerers_factories.OffererFactory(tags=tags[1:])

        response = self.delete_offerer_tag(authenticated_client, tags[1].id)

        assert response.status_code == 303
        assert set(offerers_models.OffererTag.query.all()) == {tags[0], tags[2]}
        assert offerers_models.Offerer.query.one().tags == [tags[2]]

    def test_delete_non_existing_tag(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory()

        response = self.delete_offerer_tag(authenticated_client, tag.id + 1)

        assert response.status_code == 404
        assert offerers_models.OffererTag.query.count() == 1

    def delete_offerer_tag(self, authenticated_client, offerer_tag_id):
        # generate csrf token
        authenticated_client.get(url_for("backoffice_v3_web.offerer_tag.list_offerer_tags"))

        form = {"csrf_token": g.get("csrf_token", "")}
        return authenticated_client.post(
            url_for("backoffice_v3_web.offerer_tag.delete_offerer_tag", offerer_tag_id=offerer_tag_id), form=form
        )
