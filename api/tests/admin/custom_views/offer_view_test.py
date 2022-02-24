import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.admin.custom_views.offer_view import OfferView
from pcapi.admin.custom_views.offer_view import ValidationView
from pcapi.connectors.api_entreprises import ApiEntrepriseException
from pcapi.core import testing
import pcapi.core.bookings.factories as booking_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.api import import_offer_validation_config
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient
from tests.conftest import clean_database


class BeneficiaryUserViewTest:
    def test_max_one_searchable_on_offer_view(self, db_session):
        # Given
        offer_view = OfferView(Offer, db_session)

        # Then
        assert offer_view.column_searchable_list is None or len(offer_view.column_searchable_list) == 0


@pytest.mark.usefixtures("db_session")
class OfferValidationViewTest:
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    def test_approve_offer_and_go_to_next_offer(
        self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, app
    ):
        users_factories.AdminFactory(email="admin@example.com")
        venue = VenueFactory()
        offerer = venue.managingOfferer
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        # newest offer
        offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            isActive=True,
            venue__bookingEmail="email1@example.com",
            venue=venue,
            id=3,
        )
        currently_displayed_offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            isActive=True,
            venue__bookingEmail="email1@example.com",
            venue=venue,
            id=2,
        )
        oldest_offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            isActive=True,
            venue__bookingEmail="email2@example.com",
            venue=venue,
            id=1,
        )

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }

        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={currently_displayed_offer.id}", form=data)

        currently_displayed_offer = Offer.query.get(currently_displayed_offer.id)
        assert currently_displayed_offer.validation == OfferValidationStatus.APPROVED
        assert response.status_code == 302
        assert response.headers["location"] == f"http://localhost/pc/back-office/validation/edit/?id={oldest_offer.id}"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    def test_approve_last_pending_offer_and_go_to_the_next_offer_redirect_to_validation_page(
        self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, app
    ):
        users_factories.AdminFactory(email="admin@example.com")
        venue = VenueFactory()
        offerer = venue.managingOfferer

        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            isActive=True,
            venue__bookingEmail="email@example.com",
            venue=venue,
        )

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }

        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        assert offer.validation == OfferValidationStatus.APPROVED
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/validation/"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_status_update_email")
    def test_approve_virtual_offer_and_send_mail_to_managing_offerer(
        self,
        mocked_send_offer_validation_status_update_email,
        mocked_get_offerer_legal_category,
        mocked_validate_csrf_token,
        app,
    ):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        venue = VenueFactory(bookingEmail=None)
        offerer = venue.managingOfferer
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, isActive=True, venue=venue)

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")

        # When
        client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        # Then
        mocked_send_offer_validation_status_update_email.assert_called_once_with(
            offer, OfferValidationStatus.APPROVED, ["pro@example.com"]
        )

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_status_update_email")
    def test_approve_physical_offer_and_send_mail_to_venue_booking_email(
        self,
        mocked_send_offer_validation_status_update_email,
        mocked_get_offerer_legal_category,
        mocked_validate_csrf_token,
        app,
    ):
        # Given
        users_factories.AdminFactory(email="admin@example.com")

        venue = VenueFactory(bookingEmail="venue@example.com")

        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, isActive=True, venue=venue)

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save-and-go-next")
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")

        # When
        client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        # Then
        mocked_send_offer_validation_status_update_email.assert_called_once_with(
            offer, OfferValidationStatus.APPROVED, ["venue@example.com"]
        )

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES="super_admin@example.com")
    def test_import_validation_config(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="super_admin@example.com")
        config_yaml = """
                    minimum_score: 0.6
                    rules:
                       - name: "check offer name"
                         factor: 0
                         conditions:
                           - model: "Offer"
                             attribute: "name"
                             condition:
                                operator: "not in"
                                comparated: "REJECTED"
                       - name: "check offer max price"
                         factor: 0.7
                         conditions:
                           - model: "Offer"
                             attribute: "max_price"
                             condition:
                                operator: ">"
                                comparated: 100
                    """

        data = dict(specs=config_yaml, action="save")
        client = TestClient(app.test_client()).with_session_auth("super_admin@example.com")

        # When
        response = client.post("pc/back-office/fraud_rules_configuration/new/", form=data)
        saved_config = OfferValidationConfig.query.one()

        # Then
        assert response.status_code == 302
        assert saved_config.user.email == "super_admin@example.com"
        assert saved_config.dateCreated.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp(), rel=1)
        assert saved_config.specs == {
            "minimum_score": 0.6,
            "rules": [
                {
                    "name": "check offer name",
                    "factor": 0,
                    "conditions": [
                        {
                            "model": "Offer",
                            "attribute": "name",
                            "condition": {"operator": "not in", "comparated": "REJECTED"},
                        }
                    ],
                },
                {
                    "name": "check offer max price",
                    "factor": 0.7,
                    "conditions": [
                        {
                            "model": "Offer",
                            "attribute": "max_price",
                            "condition": {"comparated": 100, "operator": ">"},
                        }
                    ],
                },
            ],
        }

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES="super_admin@example.com")
    def test_import_validation_config_fail_with_wrong_value(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="super_admin@example.com")
        config_yaml = """
                    minimum_score: 0.6
                    parameters:
                        name:
                            model: "Offer"
                            attribute: "name"
                            condition:
                                operator: "wrong value"
                                comparated: "REJECTED"
                            factor: 0
                        price_all_types:
                            model: "Offer"
                            attribute: "max_price"
                            condition:
                                operator: ">"
                                comparated: 100
                            factor: 0.7
                    """

        data = dict(specs=config_yaml, action="save")
        client = TestClient(app.test_client()).with_session_auth("super_admin@example.com")

        # When
        response = client.post("pc/back-office/fraud_rules_configuration/new/", form=data)

        # Then
        assert response.status_code == 400

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES="super_admin@example.com")
    def test_import_validation_config_fail_when_user_is_not_super_admin(self, mocked_validate_csrf_token, app):
        # Given
        users_factories.AdminFactory(email="not_super_admin@example.com")
        config_yaml = """
                    minimum_score: 0.6
                    parameters:
                        name:
                            model: "Offer"
                            attribute: "name"
                            condition:
                                operator: "not in"
                                comparated: "REJECTED"
                            factor: 0
                        price_all_types:
                            model: "Offer"
                            attribute: "max_price"
                            condition:
                                operator: ">"
                                comparated: 100
                            factor: 0.7
                    """

        data = dict(specs=config_yaml, action="save")
        client = TestClient(app.test_client()).with_session_auth("not_super_admin@example.com")

        # When
        response = client.post("pc/back-office/fraud_rules_configuration/new/", form=data)

        # Then
        assert response.status_code == 403

    @freeze_time("2020-11-17 15:00:00")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_notification_to_administration")
    def test_approve_offer_and_send_mail_to_administration(
        self,
        mocked_send_offer_validation_notification_to_administration,
        mocked_get_offerer_legal_category,
        mocked_validate_csrf_token,
        app,
    ):
        # Given
        config_yaml = """
                    minimum_score: 0.6
                    rules:
                       - name: "check offer name"
                         factor: 0
                         conditions:
                           - model: "Offer"
                             attribute: "name"
                             condition:
                                operator: "not in"
                                comparated: "REJECTED"
                    """
        import_offer_validation_config(config_yaml)
        users_factories.AdminFactory(email="admin@example.com")
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, isActive=True)
        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.APPROVED.value, action="save")
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")

        # When
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/validation/"
        assert offer.validation == OfferValidationStatus.APPROVED
        mocked_send_offer_validation_notification_to_administration.assert_called_once_with(
            OfferValidationStatus.APPROVED, offer
        )
        assert offer.lastValidationDate == datetime.datetime(2020, 11, 17, 15)

    @freeze_time("2020-11-17 15:00:00")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_notification_to_administration")
    def test_reject_offer_and_send_mail_to_administration(
        self,
        mocked_send_offer_validation_notification_to_administration,
        mocked_get_offerer_legal_category,
        mocked_validate_csrf_token,
        app,
    ):
        # Given
        config_yaml = """
                    minimum_score: 0.6
                    rules:
                       - name: "check offer name"
                         factor: 0
                         conditions:
                           - model: "Offer"
                             attribute: "name"
                             condition:
                                operator: "not in"
                                comparated: "REJECTED"
                    """
        import_offer_validation_config(config_yaml)
        users_factories.AdminFactory(email="admin@example.com")
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }
        data = dict(validation=OfferValidationStatus.REJECTED.value, action="save")
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")

        # When
        response = client.post(f"/pc/back-office/validation/edit?id={offer.id}", form=data)

        # Then
        mocked_send_offer_validation_notification_to_administration.assert_called_once_with(
            OfferValidationStatus.REJECTED, offer
        )
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/validation/"
        assert offer.validation == OfferValidationStatus.REJECTED
        assert offer.isActive is False
        assert offer.lastValidationDate == datetime.datetime(2020, 11, 17, 15)

    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES="super_admin@example.com")
    def test_access_to_validation_page_with_super_admin_user_on_prod_env(self, app):
        users_factories.AdminFactory(email="super_admin@example.com")
        client = TestClient(app.test_client()).with_session_auth("super_admin@example.com")

        response = client.get("/pc/back-office/validation/")

        assert response.status_code == 200

    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES="super_admin@example.com")
    def test_access_to_validation_page_with_none_super_admin_user_on_prod_env(self, app):
        users_factories.AdminFactory(email="simple_admin@example.com")
        client = TestClient(app.test_client()).with_session_auth("simple_admin@example.com")

        response = client.get("/pc/back-office/validation/")

        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/"

    def test_get_query_and_count(self, db_session):
        offer_view = ValidationView(model=Offer, session=db_session)
        validated_offerer = offers_factories.OffererFactory()
        non_validated_offerer = offers_factories.OffererFactory(validationToken="token")
        offer_1 = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            venue__managingOfferer=validated_offerer,
        )
        offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            venue__managingOfferer=non_validated_offerer,
        )

        get_query_offers_list = offer_view.get_query().all()
        get_count_query_scalar = offer_view.get_count_query().scalar()

        assert get_query_offers_list == [offer_1]
        assert get_count_query_scalar == 1

    @clean_database
    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES="superadmin@example.com")
    def test_number_of_queries_for_offer_list(self, app):
        admin = users_factories.AdminFactory(email="superadmin@example.com")
        client = TestClient(app.test_client()).with_session_auth(admin.email)

        offers_factories.OfferValidationConfigFactory(
            specs={
                "minimum_score": 0.1,
                "rules": [
                    {
                        "conditions": [
                            {
                                "attribute": "max_price",
                                "condition": {"comparated": 1, "operator": ">"},
                                "model": "Offer",
                            },
                        ],
                        "factor": 0.8,
                        "name": "Vérification",
                    },
                ],
            }
        )
        for _ in range(5):
            offers_factories.StockFactory(offer__validation=OfferValidationStatus.PENDING)

        n_queries = testing.AUTHENTICATION_QUERIES
        n_queries += 1  # count
        n_queries += 1  # select offers
        with testing.assert_num_queries(n_queries):
            response = client.get("/pc/back-office/validation/")

        assert response.status_code == 200
        assert b"<h2>Validation des offres</h2>" in response.data

    @pytest.mark.parametrize(
        "action,expected", [("approve", OfferValidationStatus.APPROVED), ("reject", OfferValidationStatus.REJECTED)]
    )
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    def test_batch_approve_offers(
        self, mocked_get_offerer_legal_category, mocked_validate_csrf_token, action, expected, client, app
    ):
        users_factories.AdminFactory(email="admin@example.com")
        venue = VenueFactory()
        offerer = venue.managingOfferer
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offer1 = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            isActive=True,
            venue__bookingEmail="email1@example.com",
            venue=venue,
        )
        offer2 = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            isActive=True,
            venue__bookingEmail="email1@example.com",
            venue=venue,
        )

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }

        data = dict(rowid=[offer1.id, offer2.id], action=action)
        client.with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/validation/action/", form=data)

        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/validation/"

        assert Offer.query.get(offer1.id).validation == expected
        assert Offer.query.get(offer2.id).validation == expected

        # There is no status returned by the action, check flash message
        get_response = client.get(response.headers["location"])
        assert "2 offres ont été modifiées avec succès" in get_response.data.decode("utf8")

    @pytest.mark.parametrize("action", ["approve", "reject"])
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.connectors.api_entreprises.get_offerer_legal_category")
    @patch("pcapi.core.offers.api.update_pending_offer_validation")
    def test_batch_approve_reject_offers_not_updated(
        self,
        mocked_update_pending_offer_validation,
        mocked_get_offerer_legal_category,
        mocked_validate_csrf_token,
        action,
        client,
        app,
    ):
        users_factories.AdminFactory(email="admin@example.com")
        venue = VenueFactory()
        offerer = venue.managingOfferer
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            isActive=True,
            venue__bookingEmail="email1@example.com",
            venue=venue,
        )
        offers_factories.OfferValidationConfigFactory()

        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }

        mocked_update_pending_offer_validation.return_value = False

        data = dict(rowid=[offer.id], action=action)
        client.with_session_auth("admin@example.com")
        response = client.post("/pc/back-office/validation/action/", form=data)

        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost/pc/back-office/validation/"

        assert Offer.query.get(offer.id).validation == OfferValidationStatus.PENDING

        # There is no status returned by the action, check flash message
        get_response = client.get(response.headers["location"])
        assert (
            "Une erreur s&#39;est produite lors de la mise à jour du statut de validation des offres"
            in get_response.data.decode("utf8")
        )


class GetOfferValidationViewTest:
    CONFIG_YAML = """
                minimum_score: 0.6
                rules:
                   - name: "check offer name"
                     factor: 0
                     conditions:
                       - model: "Offerer"
                         attribute: "legal_category"
                         condition:
                            operator: "=="
                            comparated: "5202"
                """

    @clean_database
    @patch("pcapi.core.offerers.models.get_offerer_legal_category")
    def test_offer_validation_legal_category_api_calls(self, mocked_get_offerer_legal_category, app):
        import_offer_validation_config(self.CONFIG_YAML)
        users_factories.AdminFactory(email="admin@example.com")
        offerer = offers_factories.OffererFactory()
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=False, venue__managingOfferer=offerer
        )
        offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=False, venue__managingOfferer=offerer
        )
        offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=False, venue__managingOfferer=offerer
        )
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        mocked_get_offerer_legal_category.return_value = {
            "legal_category_code": 5202,
            "legal_category_label": "Société en nom collectif",
        }

        response_1 = client.get("/pc/back-office/validation/")
        response_2 = client.get("/pc/back-office/validation/")
        response_3 = client.get(f"/pc/back-office/validation/edit?id={offer.id}")

        assert response_1.status_code == response_2.status_code == response_3.status_code == 200
        assert mocked_get_offerer_legal_category.call_count == 1

    @clean_database
    @patch("pcapi.connectors.api_entreprises.get_by_offerer")
    def test_view_form_loads_if_wrong_siren(self, mocked_get_by_offerer, app, client, caplog):
        import_offer_validation_config(self.CONFIG_YAML)
        users_factories.AdminFactory(email="admin@example.com")
        offerer = offers_factories.OffererFactory()
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING, isActive=False, venue__managingOfferer=offerer
        )
        client = client.with_session_auth("admin@example.com")
        mocked_get_by_offerer.side_effect = ApiEntrepriseException(
            f"Error getting API entreprise DATA for SIREN:{offerer.siren}"
        )
        response = client.get(f"/pc/back-office/validation/edit?id={offer.id}")

        assert response.status_code == 200
        assert caplog.messages == ["Could not reach API Entreprise"]


class OfferViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_status_update_email")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_notification_to_administration")
    def test_reject_approved_offer(
        self,
        mocked_send_offer_validation_notification_to_administration,
        mocked_send_offer_validation_status_update_email,
        mocked_validate_csrf_token,
        app,
    ):
        users_factories.AdminFactory(email="admin@example.com")
        with freeze_time("2020-11-17 15:00:00") as frozen_time:
            offer = offers_factories.OfferFactory(
                validation=OfferValidationStatus.APPROVED, isActive=True, venue__bookingEmail="offerer@example.com"
            )
            frozen_time.move_to("2020-12-20 15:00:00")
            data = dict(validation=OfferValidationStatus.REJECTED.value)
            client = TestClient(app.test_client()).with_session_auth("admin@example.com")

            response = client.post(f"/pc/back-office/offer/edit/?id={offer.id}", form=data)

        assert response.status_code == 302
        assert offer.validation == OfferValidationStatus.REJECTED
        assert offer.lastValidationDate == datetime.datetime(2020, 12, 20, 15)

        mocked_send_offer_validation_notification_to_administration.assert_called_once_with(
            OfferValidationStatus.REJECTED, offer
        )
        mocked_send_offer_validation_status_update_email.assert_called_once_with(
            offer, OfferValidationStatus.REJECTED, ["offerer@example.com"]
        )

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_status_update_email")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_notification_to_administration")
    def test_approve_rejected_offer(
        self,
        mocked_send_offer_validation_notification_to_administration,
        mocked_send_offer_validation_status_update_email,
        mocked_validate_csrf_token,
        app,
    ):
        users_factories.AdminFactory(email="admin@example.com")
        with freeze_time("2020-11-17 15:00:00") as frozen_time:
            offer = offers_factories.OfferFactory(validation=OfferValidationStatus.REJECTED, isActive=True)
            frozen_time.move_to("2020-12-20 15:00:00")
            data = dict(validation=OfferValidationStatus.APPROVED.value)
            client = TestClient(app.test_client()).with_session_auth("admin@example.com")

            response = client.post(f"/pc/back-office/offer/edit/?id={offer.id}", form=data)

        assert response.status_code == 302
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationDate == datetime.datetime(2020, 12, 20, 15)

        mocked_send_offer_validation_notification_to_administration.assert_called_once_with(
            OfferValidationStatus.APPROVED, offer
        )
        assert mocked_send_offer_validation_status_update_email.call_count == 1

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_status_update_email")
    @patch("pcapi.admin.custom_views.offer_view.send_offer_validation_notification_to_administration")
    @patch("pcapi.admin.custom_views.offer_view.send_cancel_booking_notification.delay")
    def test_reject_approved_offer_with_bookings(
        self,
        mocked_send_cancel_booking_notification,
        mocked_send_offer_validation_notification_to_administration,
        mocked_send_offer_validation_status_update_email,
        mocked_validate_csrf_token,
        app,
    ):
        users_factories.AdminFactory(email="admin@example.com")
        with freeze_time("2020-11-17 15:00:00") as frozen_time:
            offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED, isActive=True)
            stock = offers_factories.StockFactory(offer=offer, price=10)
            unused_booking = booking_factories.IndividualBookingFactory(stock=stock)
            used_booking = booking_factories.UsedBookingFactory(stock=stock)
            frozen_time.move_to("2020-12-20 15:00:00")
            data = dict(validation=OfferValidationStatus.REJECTED.value)
            client = TestClient(app.test_client()).with_session_auth("admin@example.com")

            response = client.post(f"/pc/back-office/offer/edit/?id={offer.id}", form=data)

        assert response.status_code == 302
        assert offer.validation == OfferValidationStatus.REJECTED
        assert offer.lastValidationDate == datetime.datetime(2020, 12, 20, 15)
        assert unused_booking.status is BookingStatus.CANCELLED
        assert used_booking.status is not BookingStatus.CANCELLED

        mocked_send_cancel_booking_notification.assert_called_once_with([unused_booking.id])

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_change_to_draft_approved_offer(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="admin@example.com")
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.APPROVED, isActive=True)
        data = dict(validation=OfferValidationStatus.DRAFT.value)
        client = TestClient(app.test_client()).with_session_auth("admin@example.com")

        response = client.post(f"/pc/back-office/offer/edit/?id={offer.id}", form=data)

        assert response.status_code == 200
        assert offer.validation == OfferValidationStatus.APPROVED

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.reindex_offer_ids")
    def test_reindex_when_tags_updated(
        self,
        mocked_reindex_offer_ids,
        mocked_validate_csrf_token,
        client,
    ):
        offer = offers_factories.EventStockFactory().offer
        tag = offers_factories.CriterionFactory()
        data = {"criteria": [tag.id], "validation": OfferValidationStatus.APPROVED.value}

        admin = users_factories.AdminFactory(email="admin@example.com")
        client = client.with_session_auth(admin.email)

        response = client.post(f"/pc/back-office/offer/edit/?id={offer.id}", form=data)

        assert response.status_code == 302
        mocked_reindex_offer_ids.assert_called_once_with([offer.id])
