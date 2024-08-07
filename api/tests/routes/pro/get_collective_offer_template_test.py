import pytest

from pcapi.core import testing
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_access_by_beneficiary(self, client):
        # Given
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(nationalProgramId=national_program.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        expected_num_queries = 8
        # collective_offer_template
        # session
        # user
        # offerer
        # user_offerer
        # collective_offer_template
        # google_places_info
        # national_program
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers-template/{offer.id}")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
        assert "stock" not in response_json
        assert "dateCreated" in response_json
        assert "educationalPriceDetail" in response_json
        assert response_json["imageCredit"] is None
        assert response_json["imageUrl"] is None
        assert response_json["name"] == offer.name
        assert response_json["id"] == offer.id
        assert response.json["nationalProgram"] == {"id": national_program.id, "name": national_program.name}
        assert response.json["dates"] == {
            "start": format_into_utc_date(offer.start),
            "end": format_into_utc_date(offer.end),
        }
        assert response.json["formats"] == offer.formats

    def test_performance(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client.with_session_auth(email="user@example.com")

        with testing.assert_no_duplicated_queries():
            client.get(f"/collective/offers-template/{offer.id}")


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email=pro_user.email)
        expected_num_queries = 5
        # collective_offer_template
        # session
        # user
        # offerer
        # user_offerer
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers-template/{offer.id}")
            assert response.status_code == 403
