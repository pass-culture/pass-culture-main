import datetime
from unittest import mock

from dateutil.relativedelta import relativedelta
from flask import g
from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications.sms import testing as sms_testing
import pcapi.utils.email as email_utils

from .helpers import accounts as accounts_helpers
from .helpers import html_parser
from .helpers import search as search_helpers
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


def create_bunch_of_accounts():
    underage = users_factories.UnderageBeneficiaryFactory(
        firstName="Gédéon",
        lastName="Groidanlabénoir",
        email="gg@example.net",
        phoneNumber="+33123456789",
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
    )
    grant_18 = users_factories.BeneficiaryGrant18Factory(
        firstName="Abdel Yves Akhim",
        lastName="Flaille",
        email="ayaf@example.net",
        phoneNumber="+33756273849",
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
    )
    pro = users_factories.ProFactory(  # associated with no offerer
        firstName="Gérard", lastName="Mentor", email="gm@example.com", phoneNumber="+33246813579"
    )
    random = users_factories.UserFactory(
        firstName="Anne", lastName="Algézic", email="aa@example.net", phoneNumber="+33606060606"
    )
    no_address = users_factories.UserFactory(
        firstName="Jean-Luc",
        lastName="Delarue",
        email="jld@example.com",
        phoneNumber="+33234567890",
        city=None,
        address=None,
    )
    # Same first name as random:
    users_factories.UserFactory(
        firstName="Anne", lastName="Autre", email="autre@example.com", phoneNumber="+33780000000"
    )

    # Pro account should not be returned
    pro_user = users_factories.ProFactory(firstName="Gérard", lastName="Flaille", email="pro@example.net")
    offerers_factories.UserOffererFactory(user=pro_user)

    # Beneficiary which is also hired by a pro should be returned
    offerers_factories.UserOffererFactory(user=grant_18)

    return underage, grant_18, pro, random, no_address


def assert_user_equals(result_card_text: str, expected_user: users_models.User):
    assert f"{expected_user.firstName} {expected_user.lastName} " in result_card_text
    assert f"User ID : {expected_user.id} " in result_card_text
    assert f"E-mail : {expected_user.email} " in result_card_text
    if expected_user.phoneNumber:
        assert f"Tél : {expected_user.phoneNumber} " in result_card_text
    if users_models.UserRole.BENEFICIARY in expected_user.roles:
        assert "Pass 18 " in result_card_text
    if users_models.UserRole.UNDERAGE_BENEFICIARY in expected_user.roles:
        assert "Pass 15-17 " in result_card_text
    if not expected_user.isActive:
        assert "Suspendu " in result_card_text


class SearchPublicAccountsUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.public_accounts.search_public_accounts"
    needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT


class SearchPublicAccountsTest(search_helpers.SearchHelper):
    endpoint = "backoffice_v3_web.public_accounts.search_public_accounts"

    def test_search_result_page(self, authenticated_client, legit_user):  # type: ignore
        url = url_for(self.endpoint, terms=legit_user.email, order_by="", page=1, per_page=20)

        response = authenticated_client.get(url)

        assert response.status_code == 200, f"[{response.status}] {response.location}"
        assert legit_user.email in str(response.data)

    def test_malformed_query(self, authenticated_client, legit_user):  # type: ignore
        url = url_for(self.endpoint, terms=legit_user.email, order_by="unknown_field")

        response = authenticated_client.get(url)

        assert response.status_code == 400

    def test_can_search_public_account_by_id(self, authenticated_client):
        # given
        underage, _, _, _, _ = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=underage.id))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], underage)

    @pytest.mark.parametrize(
        "query,expected_found",
        [
            ("Yves", "Abdel Yves Akhim"),
            ("Abdel Akhim", "Abdel Yves Akhim"),
            ("Gérard", "Gérard"),
            ("Gerard", "Gérard"),
            ("Jean Luc", "Jean-Luc"),
        ],
    )
    def test_can_search_public_account_by_first_name(self, authenticated_client, query, expected_found):
        # given
        _, _, _, _, _ = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert expected_found in cards_text[0]

    @pytest.mark.parametrize("query", ["ALGÉZIC", "Algézic", "Algezic"])
    def test_can_search_public_account_by_name(self, authenticated_client, query):
        # given
        _, _, _, random, _ = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], random)

    def test_can_search_public_account_order_by_priority(self, authenticated_client):
        # given
        create_bunch_of_accounts()
        users_factories.BeneficiaryGrant18Factory(firstName="Théo", lastName="Dorant")
        users_factories.BeneficiaryGrant18Factory(firstName="Théodule", lastName="Dorantissime")
        users_factories.BeneficiaryGrant18Factory(firstName="Théos", lastName="Doranta")

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="Théo Dorant"))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 3
        assert " Théo Dorant " in cards_text[0]
        assert " Théodule Dorantissime " in cards_text[1]
        assert " Théos Doranta " in cards_text[2]

    def test_can_search_public_account_by_email(self, authenticated_client):
        # given
        _, _, _, random, _ = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=random.email))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], random)

    def test_can_search_public_account_by_email_domain(self, authenticated_client):
        # given
        underage, grant_18, _, random, _ = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="@example.net"))

        # then
        assert response.status_code == 200
        cards_titles = html_parser.extract_cards_titles(response.data)
        assert set(cards_titles) == {underage.full_name, grant_18.full_name, random.full_name}

    @pytest.mark.parametrize("query", ["+33756273849", "0756273849", "756273849"])
    def test_can_search_public_account_by_phone(self, authenticated_client, query):
        # given
        _, grant_18, _, _, _ = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], grant_18)

    def test_can_search_public_account_even_with_missing_city_address(self, authenticated_client):
        # given
        _, _, _, _, no_address = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=no_address.phoneNumber))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], no_address)

    @pytest.mark.parametrize("query", ["Abdel Yves Akhim Flaille", "Abdel Flaille", "Flaille Akhim", "Yves Abdel"])
    def test_can_search_public_account_by_both_first_name_and_name(self, authenticated_client, query):
        # given
        _, grant_18, _, _, _ = create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], grant_18)

    @pytest.mark.parametrize("query", ["Gédéon Flaille", "Abdal Flaille", "Autre Algézic"])
    def test_can_search_public_account_names_which_do_not_match(self, authenticated_client, query):
        # given
        create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 0

    def test_can_search_public_account_empty_query(self, authenticated_client):
        # given
        create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=""))

        # then
        assert response.status_code == 400

    @pytest.mark.parametrize("query", ["'", '""', "Ge*", "([{#/="])
    def test_can_search_public_account_unexpected(self, authenticated_client, query):
        # given
        create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=query))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 0

    def test_search_public_account_with_percent_is_forbidden(self, authenticated_client):
        # given
        create_bunch_of_accounts()

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms="%terms"))

        # then
        assert response.status_code == 400
        assert "Le caractère % n'est pas autorisé" in html_parser.extract_warnings(response.data)

    def test_can_search_public_account_young_but_also_pro(self, authenticated_client):
        # given
        # She has started subscription process, but is also hired by an offerer
        young_and_pro = users_factories.BeneficiaryGrant18Factory(
            firstName="Maud",
            lastName="Zarella",
            email="mz@example.com",
            dateOfBirth=datetime.date.today() - relativedelta(years=16, days=5),
        )
        offerers_factories.UserOffererFactory(user=young_and_pro)

        # when
        response = authenticated_client.get(url_for(self.endpoint, terms=young_and_pro.email))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], young_and_pro)


class GetPublicAccountTest(accounts_helpers.PageRendersHelper):
    endpoint = "backoffice_v3_web.public_accounts.get_public_account"

    class GetPublicAccountUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.public_accounts.get_public_account"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.READ_PUBLIC_ACCOUNT

    @pytest.mark.parametrize(
        "index,expected_badge",
        [(0, "Pass 15-17"), (1, "Pass 18"), (2, "Pro"), (3, None)],
    )
    def test_get_public_account(self, authenticated_client, index, expected_badge):
        # given
        users = create_bunch_of_accounts()
        user = users[index]

        # when
        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))

        # then
        assert response.status_code == 200
        content = html_parser.content_as_text(response.data)
        assert f"User ID : {user.id} " in content
        assert f"Nom {user.lastName.upper()} " in content
        assert f"Prénom {user.firstName} " in content
        assert f"Email {user.email} " in content
        assert f"Numéro de téléphone {user.phoneNumber} " in content
        if user.dateOfBirth:
            assert f"Date de naissance {user.dateOfBirth.strftime('%d/%m/%Y')} " in content
        assert f"Adresse {user.address} " in content
        if user.postalCode:
            assert f"Code postal {user.postalCode} " in content
        assert f"Ville {user.city} " in content
        if expected_badge:
            assert expected_badge in content
        assert "Suspendu" not in content

    def test_get_beneficiary_credit(self, authenticated_client):
        # given
        _, grant_18, _, _, _ = create_bunch_of_accounts()

        bookings_factories.IndividualBookingFactory(
            individualBooking__user=grant_18,
            stock__offer__product=offers_factories.DigitalProductFactory(),
            amount=12.5,
        )

        # when
        response = authenticated_client.get(url_for(self.endpoint, user_id=grant_18.id))

        # then
        assert response.status_code == 200
        cards_text = html_parser.extract_cards_text(response.data)
        # Remaining credit + Title + Initial Credit
        assert "287,50 € Crédit restant 300,00 €" in cards_text
        assert "87,50 € Crédit digital restant 100,00 €" in cards_text

    def test_get_non_beneficiary_credit(self, authenticated_client):
        # given
        _, _, pro, random, _ = create_bunch_of_accounts()

        # when
        responses = [authenticated_client.get(url_for(self.endpoint, user_id=user.id)) for user in (pro, random)]

        # then
        for response in responses:
            assert response.status_code == 200
            assert "Crédit restant" not in html_parser.content_as_text(response.data)

    def test_get_beneficiary_bookings(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        b1 = bookings_factories.CancelledBookingFactory(user=user, amount=12.5)
        b2 = bookings_factories.UsedBookingFactory(user=user, amount=20)
        bookings_factories.UsedBookingFactory()

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))

        bookings = html_parser.extract_table_rows(response.data, parent_id="bookings-tab-pane")
        assert len(bookings) == 2

        assert bookings[0]["Offreur"] == b2.offerer.name
        assert bookings[0]["Nom de l'offre"] == b2.stock.offer.name
        assert bookings[0]["Prix"] == "20,00 €"
        assert bookings[1]["Date de résa"].startswith(datetime.date.today().strftime("Le %d/%m/%Y"))
        assert bookings[0]["État"] == "Le jeune a consommé l'offre"
        assert bookings[0]["Contremarque"] == b2.token

        assert bookings[1]["Offreur"] == b1.offerer.name
        assert bookings[1]["Nom de l'offre"] == b1.stock.offer.name
        assert bookings[1]["Prix"] == "12,50 €"
        assert bookings[1]["Date de résa"].startswith(datetime.date.today().strftime("Le %d/%m/%Y"))
        assert bookings[1]["État"] == "L'offre n'a pas eu lieu"
        assert bookings[1]["Contremarque"] == b1.token

        text = html_parser.content_as_text(response.data)
        assert f"Utilisée le : {datetime.date.today().strftime('%d/%m/%Y')}" in text
        assert f"Annulée le : {datetime.date.today().strftime('%d/%m/%Y')}" in text
        assert "Motif d'annulation : Annulée par le bénéficiaire" in text

    def test_get_beneficiary_bookings_empty(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedBookingFactory()

        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))

        assert not html_parser.extract_table_rows(response.data, parent_id="bookings-tab-pane")
        assert "Aucune réservation à ce jour" in response.data.decode("utf-8")


class EditPublicAccountTest(accounts_helpers.PageRendersHelper):
    endpoint = "backoffice_v3_web.public_accounts.edit_public_account"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.public_accounts.edit_public_account"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_edit_public_account(self, authenticated_client):
        # given
        user = users_factories.BeneficiaryGrant18Factory()

        # when
        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))

        # then
        # form page is generated without exception
        assert response.status_code == 200


class UpdatePublicAccountTest:
    class UnauthorizedTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.public_accounts.update_public_account"
        endpoint_kwargs = {"user_id": 1}
        method = "post"
        form = {"first_name": "aaaaaaaaaaaaaaaaaaa"}

    def test_update_field(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()

        new_email = user_to_edit.email + ".UPDATE  "
        expected_new_email = email_utils.sanitize_email(new_email)
        expected_new_postal_code = "75000"
        expected_city = user_to_edit.city

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": new_email,
            "birth_date": user_to_edit.birth_date,
            "id_piece_number": user_to_edit.idPieceNumber,
            "address": user_to_edit.address,
            "postal_code": expected_new_postal_code,
        }

        response = self.update_account(authenticated_client, user_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for(
            "backoffice_v3_web.public_accounts.get_public_account", user_id=user_to_edit.id, _external=True
        )
        assert response.location == expected_url

        user_to_edit = users_models.User.query.get(user_to_edit.id)
        assert user_to_edit.email == expected_new_email
        assert user_to_edit.idPieceNumber == user_to_edit.idPieceNumber
        assert user_to_edit.postalCode == expected_new_postal_code
        assert user_to_edit.city == expected_city

    def test_unknown_field(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()
        base_form = {
            "first_name": user_to_edit.firstName,
            "unknown": "field",
        }

        response = self.update_account(authenticated_client, user_to_edit, base_form)
        assert response.status_code == 400

    def test_update_email_triggers_history_token_and_mail(self, authenticated_client):
        # given
        user, _, _, _, _ = create_bunch_of_accounts()

        # when
        response = self.update_account(authenticated_client, user, {"email": "Updated@example.com"})

        # then
        assert response.status_code == 303

        # check that email has been changed immediately after admin request
        db.session.refresh(user)
        assert user.email == "updated@example.com"
        assert not user.isEmailValidated

        # check that a line has been added in email history
        email_history: list[users_models.UserEmailHistory] = users_models.UserEmailHistory.query.filter(
            users_models.UserEmailHistory.userId == user.id
        ).all()
        assert len(email_history) == 1
        assert email_history[0].eventType == users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST
        assert email_history[0].oldEmail == "gg@example.net"
        assert email_history[0].newEmail == "updated@example.com"

        # check that a new token has been generated
        token: users_models.Token = users_models.Token.query.filter(users_models.Token.userId == user.id).one()
        assert token.type == users_models.TokenType.EMAIL_VALIDATION

        # check that email is sent
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == "updated@example.com"
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.EMAIL_CONFIRMATION.value.__dict__
        assert token.value in mails_testing.outbox[0].sent_data["params"]["CONFIRMATION_LINK"]

    def test_update_invalid_email(self, authenticated_client):
        # given
        user, _, _, _, _ = create_bunch_of_accounts()

        # when
        response = self.update_account(authenticated_client, user, {"email": "updated.example.com"})

        # then
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == ["Email obligatoire"]

    def test_email_already_exists(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()
        other_user = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": other_user.email,
        }

        response = self.update_account(authenticated_client, user_to_edit, base_form)
        assert response.status_code == 400
        assert html_parser.extract_warnings(response.data) == ["L'email est déjà associé à un autre utilisateur"]

        user_to_edit = users_models.User.query.get(user_to_edit.id)
        assert user_to_edit.email != other_user.email

    def test_invalid_postal_code(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "postal_code": "7500",
        }

        response = self.update_account(authenticated_client, user_to_edit, base_form)
        assert response.status_code == 400

    def test_empty_id_piece_number(self, authenticated_client):
        user_to_edit = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "id_piece_number": "",
        }

        response = self.update_account(authenticated_client, user_to_edit, base_form)
        assert response.status_code == 303

        user_to_edit = users_models.User.query.get(user_to_edit.id)
        assert user_to_edit.idPieceNumber is None

    def update_account(self, authenticated_client, user_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.public_accounts.edit_public_account", user_id=user_to_edit.id)
        authenticated_client.get(edit_url)

        url = url_for("backoffice_v3_web.public_accounts.update_public_account", user_id=user_to_edit.id)

        form["csrf_token"] = g.get("csrf_token", "")
        return authenticated_client.post(url, form=form)


class ResendValidationEmailTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.public_accounts.resend_validation_email"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    class MissingCsrfTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.public_accounts.resend_validation_email"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_resend_validation_email(self, authenticated_client):
        user = users_factories.UserFactory(isEmailValidated=False)
        response = self.send_resend_validation_email_request(authenticated_client, user)

        assert response.status_code == 303

        # check that validation is unchanged
        updated_user: users_models.User = users_models.User.query.get(user.id)
        assert updated_user.isEmailValidated is False

        # check that a new token has been generated
        token: users_models.Token = users_models.Token.query.filter(users_models.Token.userId == user.id).one()
        assert token.type == users_models.TokenType.EMAIL_VALIDATION

        # check that email is sent
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.EMAIL_CONFIRMATION.value.__dict__
        assert token.value in mails_testing.outbox[0].sent_data["params"]["CONFIRMATION_LINK"]

    @pytest.mark.parametrize("user_factory", [users_factories.AdminFactory, users_factories.ProFactory])
    def test_no_email_sent_if_admin_pro(self, authenticated_client, user_factory):
        user = user_factory()
        response = self.send_resend_validation_email_request(authenticated_client, user)

        assert response.status_code == 303
        assert not mails_testing.outbox

    def test_no_email_sent_if_already_validated(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory(isEmailValidated=True)
        response = self.send_resend_validation_email_request(authenticated_client, user)

        assert response.status_code == 303
        assert not mails_testing.outbox

    def send_resend_validation_email_request(self, authenticated_client, user):
        # generate csrf token
        account_detail_url = url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user.id)
        authenticated_client.get(account_detail_url)

        url = url_for("backoffice_v3_web.public_accounts.resend_validation_email", user_id=user.id)
        form = {"csrf_token": g.get("csrf_token", "")}

        return authenticated_client.post(url, form=form)


class SendValidationCodeTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.public_accounts.send_validation_code"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    class MissingCsrfTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.public_accounts.send_validation_code"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_send_validation_code(self, authenticated_client):
        user = users_factories.UserFactory(
            phoneValidationStatus=None, phoneNumber="+33601020304", isEmailValidated=True
        )
        response = self.send_request(authenticated_client, user)

        assert response.status_code == 303

        assert len(sms_testing.requests) == 1
        assert sms_testing.requests[0]["recipient"] == user.phoneNumber

        phone_validation_codes = users_models.Token.query.filter(
            users_models.Token.user == user,
            users_models.Token.type == users_models.TokenType.PHONE_VALIDATION,
        ).all()
        assert len(phone_validation_codes) == 1
        assert phone_validation_codes[0].expirationDate is None
        assert phone_validation_codes[0].isUsed is False

    def test_phone_validation_code_sending_ignores_limit(self, authenticated_client):
        # given
        user = users_factories.UserFactory(phoneValidationStatus=None, phoneNumber="+33612345678")

        # when
        with mock.patch("pcapi.core.fraud.phone_validation.sending_limit.is_SMS_sending_allowed") as limit_mock:
            limit_mock.return_value = False
            response = self.send_request(authenticated_client, user)

        # then
        assert limit_mock.call_count == 0
        assert response.status_code == 303
        assert users_models.Token.query.count() == 1

    def test_nothing_sent_use_cases(self, authenticated_client):
        other_user = users_factories.BeneficiaryGrant18Factory(
            phoneNumber="+33601020304",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        users = [
            # no phone number
            users_factories.UserFactory(phoneNumber=None),
            # phone number already validated
            users_factories.UserFactory(
                phoneNumber="+33601020304", phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
            ),
            # user is already beneficiary
            users_factories.BeneficiaryGrant18Factory(phoneNumber="+33601020304"),
            # email has not been validated
            users_factories.UserFactory(phoneNumber="+33601020304", isEmailValidated=False),
            # phone number is already used
            users_factories.UserFactory(phoneNumber=other_user.phoneNumber),
        ]

        for idx, user in enumerate(users):
            response = self.send_request(authenticated_client, user)

            assert response.status_code == 303, f"[{idx}] found: {response.status_code}, expected: 303"
            assert not sms_testing.requests, f"[{idx}] {len(sms_testing.requests)} sms sent"

    def send_request(self, authenticated_client, user):
        # generate csrf token
        account_detail_url = url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user.id)
        authenticated_client.get(account_detail_url)

        url = url_for("backoffice_v3_web.public_accounts.send_validation_code", user_id=user.id)
        form = {"csrf_token": g.get("csrf_token", "")}

        return authenticated_client.post(url, form=form)


class EditPublicAccountReviewTest(accounts_helpers.PageRendersHelper):
    endpoint = "backoffice_v3_web.public_accounts.edit_public_account_review"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.public_accounts.edit_public_account_review"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_edit_review(self, authenticated_client):
        # given
        user = users_factories.UserFactory()

        # when
        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))

        # then
        # form page is generated without exception
        assert response.status_code == 200


class UpdatePublicAccountReviewTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.public_accounts.review_public_account"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    class MissingCsrfTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.public_accounts.review_public_account"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT

    def test_add_new_fraud_review_to_account(self, authenticated_client, legit_user):
        user = users_factories.UserFactory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.add_new_review(authenticated_client, user, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.get(user.id)

        assert len(user.beneficiaryFraudReviews) == 1
        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.author == legit_user
        assert fraud_review.review == fraud_models.FraudReviewStatus.KO
        assert fraud_review.reason == "test"

        assert user.has_beneficiary_role is False

    def test_malformed_form(self, authenticated_client):
        user = users_factories.UserFactory()

        base_form = {
            "status": "invalid",
            "eligibility": "invalid",
            "reason": "test",
        }

        response = self.add_new_review(authenticated_client, user, base_form)
        assert response.status_code == 400

        user = users_models.User.query.get(user.id)
        assert not user.deposits

    def test_reason_not_compulsory(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.KO.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
        }

        response = self.add_new_review(authenticated_client, user, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user.id, _external=True)
        assert response.location == expected_url

        user = users_models.User.query.get(user.id)

        assert len(user.deposits) == 1
        assert len(user.beneficiaryFraudReviews) == 1

        fraud_review = user.beneficiaryFraudReviews[0]
        assert fraud_review.reason == None

    def test_missing_identity_fraud_check_filled(self, authenticated_client):
        # not a beneficiary, does not have any identity fraud check
        # filled by default.
        user = users_factories.UserFactory()

        base_form = {
            "status": fraud_models.FraudReviewStatus.OK.name,
            "eligibility": users_models.EligibilityType.AGE18.name,
            "reason": "test",
        }

        response = self.add_new_review(authenticated_client, user, base_form)
        assert response.status_code == 303

        user = users_models.User.query.get(user.id)
        assert not user.deposits

    def add_new_review(self, authenticated_client, user_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.public_accounts.edit_public_account", user_id=user_to_edit.id)
        response = authenticated_client.get(edit_url)

        assert response.status_code == 200

        url = url_for("backoffice_v3_web.public_accounts.review_public_account", user_id=user_to_edit.id)

        form["csrf_token"] = g.get("csrf_token", "")
        return authenticated_client.post(url, form=form)
