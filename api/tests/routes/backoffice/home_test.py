import functools

import pytest
from flask import flash
from flask import url_for
from werkzeug.exceptions import NotFound

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.routes.backoffice import utils

from tests.routes.backoffice.helpers import html_parser
from tests.routes.backoffice.helpers import url


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(name="override_homeview")
def override_homeview_fixture(app, request):
    called = False
    homeview_import_name = "backoffice_web.home"
    old_view = app.view_functions[homeview_import_name]

    def _decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal called
            called = True
            return func(*args, **kwargs)

        return wrapper

    def _set_view(new_view):
        app.view_functions[homeview_import_name] = _decorator(new_view)

    def _reset():
        app.view_functions[homeview_import_name] = old_view

    request.addfinalizer(_reset)

    yield _set_view
    assert called


class HomePageTest:
    # - session + user
    # - data inserted in cards (stats got in a single request)
    expected_num_queries = 2

    def test_view_home_page_as_anonymous(self, client):
        response = client.get(url_for("backoffice_web.home"))
        assert response.status_code == 200

    def test_view_home_page(self, authenticated_client):
        response = authenticated_client.get(url_for("backoffice_web.home"))
        assert response.status_code == 200

    def test_view_home_page_pending_offers(self, authenticated_client):
        validated_venue = offerers_factories.VenueFactory()
        not_validated_venue = offerers_factories.VenueFactory(managingOfferer=offerers_factories.NewOffererFactory())

        # pending offers from validated offerers
        offers_factories.OfferFactory.create_batch(
            2, validation=offer_mixin.OfferValidationStatus.PENDING, venue=validated_venue
        )
        educational_factories.CollectiveOfferFactory.create_batch(
            3, validation=offer_mixin.OfferValidationStatus.PENDING, venue=validated_venue
        )
        educational_factories.CollectiveOfferTemplateFactory.create_batch(
            4, validation=offer_mixin.OfferValidationStatus.PENDING, venue=validated_venue
        )

        # others should not be counted
        offers_factories.OfferFactory(venue=validated_venue)
        offers_factories.OfferFactory(validation=offer_mixin.OfferValidationStatus.PENDING, venue=not_validated_venue)
        educational_factories.CollectiveOfferFactory(venue=validated_venue)
        educational_factories.CollectiveOfferFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING, venue=not_validated_venue
        )
        educational_factories.CollectiveOfferTemplateFactory(venue=validated_venue)
        educational_factories.CollectiveOfferTemplateFactory(
            validation=offer_mixin.OfferValidationStatus.PENDING, venue=not_validated_venue
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.home"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert cards_text == [
            "2 offres individuelles en attente CONSULTER",
            "3 offres collectives en attente CONSULTER",
            "4 offres collectives vitrine en attente CONSULTER",
            "0 dossier DN non affecté CONSULTER",
            "0 dossier DN suivi CONSULTER",
        ]
        # No card for "entité juridique en attente de conformité" because tag "conformité" does not exist

    def test_view_home_page_pending_offerers_conformite(self, authenticated_client):
        tag = offerers_factories.OffererTagFactory(name="conformité", label="En attente de conformité")
        other_tag = offerers_factories.OffererTagFactory()

        offerers_factories.PendingOffererFactory(tags=[tag, other_tag])

        # others should not be counted
        offerers_factories.NewOffererFactory(tags=[tag])
        offerers_factories.OffererFactory(tags=[tag])
        offerers_factories.NewOffererFactory(tags=[other_tag])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.home"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert cards_text == [
            "0 offre individuelle en attente CONSULTER",
            "0 offre collective en attente CONSULTER",
            "0 offre collective vitrine en attente CONSULTER",
            "1 entité juridique en attente de conformité CONSULTER",
            "0 dossier DN non affecté CONSULTER",
            "0 dossier DN suivi CONSULTER",
        ]

    def test_view_home_page_with_user_account_update_requests_stats(self, legit_user, authenticated_client):
        users_factories.PhoneNumberUpdateRequestFactory.create_batch(2, lastInstructor=None)
        users_factories.FirstNameUpdateRequestFactory(lastInstructor=legit_user)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.home"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert cards_text == [
            "0 offre individuelle en attente CONSULTER",
            "0 offre collective en attente CONSULTER",
            "0 offre collective vitrine en attente CONSULTER",
            "2 dossiers DN non affectés CONSULTER",
            "1 dossier DN suivi CONSULTER",
        ]

    def test_view_home_page_without_user_account_update_requests_stats(self, legit_user, authenticated_client):
        legit_user.backoffice_profile.dsInstructorId = None
        db.session.flush()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for("backoffice_web.home"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert cards_text == [
            "0 offre individuelle en attente CONSULTER",
            "0 offre collective en attente CONSULTER",
            "0 offre collective vitrine en attente CONSULTER",
        ]


class MessagesTest:
    def test_anonymous_access(self, client):
        response = client.get(url_for("backoffice_web.get_messages"))
        assert response.status_code == 302
        url.assert_response_location(response, "backoffice_web.home")

    def test_empty_messages(self, authenticated_client):
        response = authenticated_client.get(url_for("backoffice_web.get_messages"))
        assert response.status_code == 200
        assert response.data == b""

    def test_regular_get(self, authenticated_client):
        with authenticated_client.session_transaction() as client_session:
            client_session["_flashes"] = [("danger", "error message"), ("warning", "warning message")]
        response = authenticated_client.get(url_for("backoffice_web.get_messages"))
        assert response.status_code == 200
        alerts = html_parser.extract_alerts(response.data)
        assert alerts == ["error message", "warning message"]

    @pytest.mark.parametrize(
        "headers,expected_alerts",
        [
            (
                {"hx-request": "true"},
                ["[global] Il semble que nous ayons des problèmes techniques :( On répare ça au plus vite."],
            ),
            ({}, []),
        ],
    )
    def test_error_500_flash_message(self, authenticated_client, override_homeview, headers, expected_alerts):
        def view():
            raise Exception()

        override_homeview(view)
        response = authenticated_client.get("/", headers=headers)
        assert response.status_code == 500

        response = authenticated_client.get(url_for("backoffice_web.get_messages"))
        assert response.status_code == 200
        alerts = html_parser.extract_alerts(response.data, raise_if_not_found=False)
        assert alerts == expected_alerts

    @pytest.mark.parametrize(
        "headers,expected_alerts",
        [
            ({"hx-request": "true"}, ["Objet non trouvé !"]),
            ({}, []),
        ],
    )
    def test_error_404_flash_message(self, authenticated_client, override_homeview, headers, expected_alerts):
        def view():
            raise NotFound()

        override_homeview(view)
        response = authenticated_client.get("/", headers=headers)
        assert response.status_code == 404

        response = authenticated_client.get(url_for("backoffice_web.get_messages"))
        assert response.status_code == 200
        alerts = html_parser.extract_alerts(response.data, raise_if_not_found=False)
        assert alerts == expected_alerts

    def test_error_404_existing_flash_message(self, authenticated_client, override_homeview):
        def view():
            flash("Offre 42 non trouvée !")
            raise NotFound()

        override_homeview(view)
        response = authenticated_client.get("/", headers={"hx-request": "true"})
        assert response.status_code == 404

        response = authenticated_client.get(url_for("backoffice_web.get_messages"))
        assert response.status_code == 200
        alerts = html_parser.extract_alerts(response.data)
        assert alerts == ["Offre 42 non trouvée !"]

    @pytest.mark.parametrize(
        "headers,expected_alerts",
        [
            ({"hx-request": "true"}, ["[global] permission manquante"]),
            ({}, []),
        ],
    )
    def test_error_403_flash_message(
        self, client, user_with_no_permissions, override_homeview, headers, expected_alerts
    ):
        @utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
        def view():
            return ""

        client = client.with_bo_session_auth(user_with_no_permissions)

        override_homeview(view)
        response = client.get("/", headers=headers)
        assert response.status_code == 403

        response = client.get(url_for("backoffice_web.get_messages"))
        assert response.status_code == 200
        alerts = html_parser.extract_alerts(response.data, raise_if_not_found=False)
        assert alerts == expected_alerts
