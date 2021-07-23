import datetime

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in_and_has_no_deposit(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(
            civility="M.",
            address=None,
            city=None,
            needsToFillCulturalSurvey=False,
            departementCode="93",
            email="toto@example.com",
            firstName="Jean",
            lastName="Smisse",
            dateOfBirth=datetime.datetime(2000, 1, 1),
            phoneNumber="0612345678",
            postalCode="93020",
            publicName="Toto",
            isEmailValidated=True,
        )

        # When
        response = TestClient(app.test_client()).with_auth(email="toto@example.com").get("/users/current")

        # Then
        assert response.status_code == 200
        assert not any("password" in field.lower() for field in response.json)
        assert response.json == {
            "activity": None,
            "address": None,
            "city": None,
            "civility": "M.",
            "dateCreated": format_into_utc_date(user.dateCreated),
            "dateOfBirth": format_into_utc_date(user.dateOfBirth),
            "departementCode": "93",
            "email": "toto@example.com",
            "externalIds": {},
            "firstName": "Jean",
            "hasCompletedIdCheck": None,
            "hasPhysicalVenues": False,
            "hasSeenProTutorials": True,
            "id": humanize(user.id),
            "idPieceNumber": None,
            "isAdmin": False,
            "isBeneficiary": True,
            "isEmailValidated": True,
            "lastConnectionDate": None,
            "lastName": "Smisse",
            "needsToFillCulturalSurvey": False,
            "notificationSubscriptions": {"marketing_email": True, "marketing_push": True},
            "phoneNumber": "0612345678",
            "phoneValidationStatus": None,
            "postalCode": "93020",
            "publicName": "Toto",
            "roles": ["BENEFICIARY"],
        }

    @pytest.mark.usefixtures("db_session")
    def test_returns_has_physical_venues_and_has_offers(self, app):
        # Given
        user = users_factories.UserFactory(email="test@email.com")
        offerer = create_offerer()
        offerer2 = create_offerer(siren="123456788")
        user_offerer = create_user_offerer(user, offerer)
        user_offerer2 = create_user_offerer(user, offerer2)
        offerer_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offerer2_physical_venue = create_venue(offerer2, siret="12345678856734")
        offerer2_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offer = create_offer_with_thing_product(
            offerer_virtual_venue, thing_subcategory_id=subcategories.ABO_JEU_VIDEO.id, url="http://fake.url"
        )
        offer2 = create_offer_with_thing_product(offerer2_physical_venue)

        repository.save(offer, offer2, offerer2_virtual_venue, user_offerer, user_offerer2)

        # When
        response = TestClient(app.test_client()).with_auth("test@email.com").get("/users/current")

        # Then
        assert response.json["hasPhysicalVenues"] is True


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, app):
        # When
        response = TestClient(app.test_client()).get("/users/current")

        # Then
        assert response.status_code == 401
