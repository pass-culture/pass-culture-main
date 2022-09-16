import logging
import re
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.admin.custom_views.venue_view import _format_venue_provider
from pcapi.connectors import sirene
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
from pcapi.core.users.factories import AdminFactory
import pcapi.core.users.testing as external_testing

from tests.conftest import TestClient
from tests.conftest import clean_database


def base_form_data(venue: Venue) -> dict:
    return dict(
        name=venue.name,
        siret=venue.siret,
        city=venue.city,
        postalCode=venue.postalCode,
        address=venue.address,
        publicName=venue.publicName,
        latitude=venue.latitude,
        longitude=venue.longitude,
        isPermanent=venue.isPermanent,
        adageId=venue.adageId,
    )


class EditVenueTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_update_adage_id(self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(adageId="123")

        data = base_form_data(venue) | dict(adageId="456")
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302
        venue_edited = Venue.query.get(venue.id)
        assert venue_edited.adageId == "456"
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_add_siret_to_venue_without_pricing_point(
        self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, caplog, app
    ):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(siret=None, comment="Pas de siret")
        data = base_form_data(venue) | dict(siret="88888888888888", comment=None)

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        with caplog.at_level(logging.INFO):
            response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302
        venue_edited = Venue.query.get(venue.id)
        assert venue_edited.siret == "88888888888888"
        assert venue_edited.current_pricing_point_id == venue_edited.id
        mocked_async_index_offers_of_venue_ids.assert_not_called()
        # A log from after_model_change() is written first
        assert caplog.records[1].message == "[ADMIN] The SIRET of a Venue has been modified"
        assert caplog.records[1].extra == {
            "venue_id": venue.id,
            "previous_siret": None,
            "new_siret": "88888888888888",
            "user_email": "user@example.com",
        }

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_edit_siret_with_self_pricing_point(
        self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, caplog, app
    ):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(siret="12345678901234", pricing_point="self")
        data = base_form_data(venue) | dict(siret="88888888888888")

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        with caplog.at_level(logging.INFO):
            response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302
        venue_edited = Venue.query.get(venue.id)
        assert venue_edited.siret == "88888888888888"
        assert venue_edited.current_pricing_point_id == venue_edited.id
        mocked_async_index_offers_of_venue_ids.assert_not_called()
        # A log from after_model_change() is written first
        assert caplog.records[1].message == "[ADMIN] The SIRET of a Venue has been modified"
        assert caplog.records[1].extra == {
            "venue_id": venue.id,
            "previous_siret": "12345678901234",
            "new_siret": "88888888888888",
            "user_email": "user@example.com",
        }

        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Venue", "id": venue.id}]

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    @patch("pcapi.connectors.sirene.get_siret", side_effect=sirene.SireneApiException)
    def test_unavailable_sirene_api_warning(
        self, _mocked_sirene_get_siret, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, caplog, app
    ):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(siret=None, comment="Pas de siret")
        data = base_form_data(venue) | dict(siret="88888888888888", comment=None)

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        with caplog.at_level(logging.INFO):
            response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data, follow_redirects=True)

        assert response.history[0].status_code == 302
        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "Ce SIRET n&#39;a pas pu être vérifié, mais la modification a néanmoins été effectuée" in content
        venue_edited = Venue.query.get(venue.id)
        assert venue_edited.siret == "88888888888888"
        assert venue_edited.current_pricing_point_id == venue_edited.id
        mocked_async_index_offers_of_venue_ids.assert_not_called()
        # A log from after_model_change() is written first
        assert caplog.records[1].message == "[ADMIN] The SIRET of a Venue has been modified"
        assert caplog.records[1].extra == {
            "venue_id": venue.id,
            "previous_siret": None,
            "new_siret": "88888888888888",
            "user_email": "user@example.com",
        }

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_cannot_remove_siret(self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(siret="12345678901234")
        data = base_form_data(venue) | dict(siret="")

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "Le champ SIRET ne peut pas être vide si ce lieu avait déjà un SIRET." in content
        refreshed_venue = Venue.query.get(venue.id)
        assert refreshed_venue.siret == "12345678901234"
        mocked_async_index_offers_of_venue_ids.assert_not_called()
        assert len(external_testing.zendesk_sell_requests) == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_cannot_set_not_all_digits_siret(
        self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, app
    ):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(siret="12345678901234")

        data = base_form_data(venue) | dict(siret="123456780ABCD")

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "Le SIRET doit être une série d&#39;exactement 14 chiffres." in content
        refreshed_venue = Venue.query.get(venue.id)
        assert refreshed_venue.siret == "12345678901234"
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_cannot_use_inactive_siret(self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(siret="12345678901234")

        data = base_form_data(venue) | dict(siret="22222222222222")
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        with patch("pcapi.connectors.sirene.get_siret") as mock_get_siret:
            mock_get_siret.return_value.active = False
            response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "Ce SIRET n&#39;est plus actif, on ne peut pas l&#39;attribuer à ce lieu" in content
        venue_edited = Venue.query.get(venue.id)
        assert venue_edited.siret == "12345678901234"
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_cannot_set_already_used_siret(
        self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, app
    ):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(siret="12345678901234")
        offerers_factories.VenueFactory(siret="22222222222222")

        data = base_form_data(venue) | dict(siret="22222222222222")

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(
            f"/pc/back-office/venue/edit/?id={venue.id}",
            form=data,
        )

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        # This is returned by the FA Unique validator
        assert "Already exists." in content
        refreshed_venue = Venue.query.get(venue.id)
        assert refreshed_venue.siret == "12345678901234"
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_cannot_add_siret_if_exisiting_pricing_point(
        self, mocked_async_index_offers_of_venue_ids, _mocked_validate_csrf_token, app
    ):
        AdminFactory(email="user@example.com")
        offerer = offerers_factories.OffererFactory()
        pricing_point = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer, siret=None, comment="Pas de SIRET", pricing_point=pricing_point
        )

        data = base_form_data(venue) | dict(siret="22222222222222")
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 200
        content = response.data.decode(response.charset)
        assert "Ce lieu a déjà un point de valorisation" in content
        refreshed_venue = Venue.query.get(venue.id)
        assert refreshed_venue.siret == None
        mocked_async_index_offers_of_venue_ids.assert_not_called()

        assert len(external_testing.zendesk_sell_requests) == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_venue_other_offer_id_at_provider(self, mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        business_unit = finance_factories.BusinessUnitFactory(siret="11111111111111")
        venue = offerers_factories.VenueFactory(siret="22222222222222", businessUnit=business_unit)
        id_at_providers = "id_at_provider_ne_contenant_pas_le_siret"
        stock = offers_factories.StockFactory(
            offer__venue=venue, idAtProviders=id_at_providers, offer__idAtProvider=id_at_providers
        )

        data = dict(
            name=venue.name,
            siret="88888888888888",
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude=venue.latitude,
            longitude=venue.longitude,
            isPermanent=venue.isPermanent,
            adageId=venue.adageId,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue_edited = Venue.query.get(venue.id)
        stock = offers_models.Stock.query.get(stock.id)
        offer = offers_models.Offer.query.get(stock.offer.id)

        assert venue_edited.siret == "88888888888888"
        assert stock.idAtProviders == "id_at_provider_ne_contenant_pas_le_siret"
        assert offer.idAtProvider == "id_at_provider_ne_contenant_pas_le_siret"

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_venue_without_siret(self, mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        business_unit = finance_factories.BusinessUnitFactory(siret="11111111111111")
        venue = offerers_factories.VenueFactory(
            siret=None, comment="comment to allow null siret", businessUnit=business_unit
        )

        data = dict(
            name=venue.name,
            siret="88888888888888",
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude=venue.latitude,
            longitude=venue.longitude,
            isPermanent=venue.isPermanent,
            adageId=venue.adageId,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Venue", "id": venue.id}]

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_update_venue_reindex_all(self, mocked_async_index_offers_of_venue_ids, mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(isPermanent=False)

        new_name = venue.name + "(updated)"
        data = dict(
            name=new_name,
            siret=venue.siret,
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude="42.01",
            longitude=venue.longitude,
            isPermanent=True,
            adageId=venue.adageId,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue = Venue.query.get(venue.id)
        assert venue.isPermanent
        assert venue.name == new_name

        mocked_async_index_offers_of_venue_ids.assert_called_once_with([venue.id])

        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Venue", "id": venue.id}]

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_update_venue_reindex_venue_only(
        self, mocked_async_index_venue_ids, mocked_async_index_offers_of_venue_ids, mocked_validate_csrf_token, app
    ):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(isPermanent=False)

        data = dict(
            name=venue.name,
            siret=venue.siret,
            city=venue.city,
            postalCode=venue.postalCode,
            address=venue.address,
            publicName=venue.publicName,
            latitude=venue.latitude,
            longitude=venue.longitude,
            isPermanent=True,
            adageId=venue.adageId,
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        venue = Venue.query.get(venue.id)
        assert venue.isPermanent

        mocked_async_index_venue_ids.assert_called_once_with([venue.id])
        mocked_async_index_offers_of_venue_ids.assert_not_called()

        assert external_testing.zendesk_sell_requests == [{"action": "update", "type": "Venue", "id": venue.id}]

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    @patch("pcapi.core.search.async_index_venue_ids")
    @patch("pcapi.core.search.reindex_venue_ids")
    def test_reindex_when_tags_updated(
        self,
        mocked_reindex_venue_ids,
        mocked_async_index_venue_ids,
        mocked_async_index_offers_of_venue_ids,
        mocked_validate_csrf_token,
        client,
    ):
        admin = AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(isPermanent=True)
        tag = criteria_factories.CriterionFactory()
        data = {
            "criteria": [tag.id],
            "name": venue.name,
            "siret": venue.siret,
            "city": venue.city,
            "postalCode": venue.postalCode,
            "address": venue.address,
            "publicName": venue.publicName,
            "latitude": venue.latitude,
            "longitude": venue.longitude,
            "isPermanent": True,
            "adageId": venue.adageId,
        }

        client = client.with_session_auth(admin.email)
        response = client.post(f"/pc/back-office/venue/edit/?id={venue.id}", form=data)

        assert response.status_code == 302

        mocked_reindex_venue_ids.assert_called_once_with([venue.id])
        mocked_async_index_venue_ids.assert_not_called()
        mocked_async_index_offers_of_venue_ids.assert_not_called()


class DeleteVenueTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_venue(self, mocked_validate_csrf_token, client):
        admin = AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory(bookingEmail="booking@example.com")
        user_offerer1 = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)
        user_offerer2 = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        api_client = client.with_session_auth(admin.email)
        response = api_client.post(
            "/pc/back-office/venue/delete/", form={"id": venue.id, "url": "/pc/back-office/venue/"}
        )

        assert response.status_code == 302
        assert len(Venue.query.all()) == 0
        assert len(external_testing.sendinblue_requests) == 3
        assert {req["email"] for req in external_testing.sendinblue_requests} == {
            user_offerer1.user.email,
            user_offerer2.user.email,
            "booking@example.com",
        }

    @pytest.mark.parametrize(
        "booking_status",
        [
            BookingStatus.PENDING,
            BookingStatus.USED,
            BookingStatus.CONFIRMED,
            BookingStatus.CANCELLED,
            BookingStatus.REIMBURSED,
        ],
    )
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_venue_rejected(self, mocked_validate_csrf_token, client, booking_status):
        admin = AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)
        BookingFactory(stock__offer__venue=venue, status=booking_status)

        api_client = client.with_session_auth(admin.email)
        response = api_client.post(
            "/pc/back-office/venue/delete/", form={"id": venue.id, "url": "/pc/back-office/venue/"}
        )

        assert response.status_code == 302

        list_response = api_client.get(response.headers["location"])
        assert "Impossible d&#39;effacer un lieu pour lequel il existe des réservations." in list_response.data.decode(
            "utf8"
        )

        assert len(Venue.query.all()) == 1
        assert len(external_testing.sendinblue_requests) == 0


class GetVenueProviderLinkTest:
    @pytest.mark.usefixtures("db_session")
    def test_return_empty_link_when_no_venue_provider(self, app):
        # Given
        venue = offerers_factories.VenueFactory()

        # When
        link = _format_venue_provider(None, None, venue, None)

        # Then
        assert not link

    @pytest.mark.usefixtures("db_session")
    def test_return_link_to_venue_provider(self, app):
        # Given
        venue_provider = providers_factories.VenueProviderFactory()
        venue = venue_provider.venue

        # When
        link = _format_venue_provider(None, None, venue, None)

        # Then
        assert str(venue.id) in link


class VenueForOffererSubviewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_list_venues_for_offerer(self, mocked_validate_csrf_token, client):
        admin = AdminFactory(email="user@example.com")
        offerer = offerers_factories.OffererFactory()
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueFactory()  # not expected result

        api_client = client.with_session_auth(admin.email)
        response = api_client.get(url_for("venue_for_offerer.index", id=offerer.id))

        assert response.status_code == 200

        # Check venues in html content
        regex = r'<td class="col-id">\s+(\d+)\s+</td>'
        venue_ids = re.findall(regex, response.data.decode("utf8"))

        assert sorted(venue_ids) == sorted([str(venue1.id), str(venue2.id)])

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_list_venues_for_offerer_not_found(self, mocked_validate_csrf_token, client):
        admin = AdminFactory(email="user@example.com")

        api_client = client.with_session_auth(admin.email)
        response = api_client.get(url_for("venue_for_offerer.index", id=42))

        assert response.status_code == 404
