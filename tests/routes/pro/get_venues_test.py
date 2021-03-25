import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200ForProUser:
    def _setup_venues_for_pro_user(self, user):
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offers_factories.VenueFactory(name="owned_venue_validated", managingOfferer=offerer)

        offerer_not_validated = offers_factories.OffererFactory(validationToken="token")
        offers_factories.UserOffererFactory(user=user, offerer=offerer_not_validated)
        venue_not_validated = offers_factories.VenueFactory(
            name="owned_venue_not_validated", managingOfferer=offerer_not_validated
        )

        offerer_validated_for_user = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(offerer=offerer_validated_for_user)
        offers_factories.UserOffererFactory(user=user, offerer=offerer_validated_for_user)
        venue_validated_for_user = offers_factories.VenueFactory(
            name="owned_venue_validated_for_user", managingOfferer=offerer_validated_for_user
        )

        offerer_not_validated_for_user = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(offerer=offerer_not_validated_for_user)
        offers_factories.UserOffererFactory(
            user=user,
            offerer=offerer_not_validated_for_user,
            validationToken="user_token",
        )
        venue_not_validated_for_user = offers_factories.VenueFactory(
            name="owned_venue_not_validated_for_user",
            managingOfferer=offerer_not_validated_for_user,
        )

        inactive_offerer = offers_factories.OffererFactory(isActive=False)
        offers_factories.UserOffererFactory(user=user, offerer=inactive_offerer)
        venue_from_inactive_offerer = offers_factories.VenueFactory(
            name="venue_from_inactive_offerer",
            managingOfferer=inactive_offerer,
        )

        other_offerer = offers_factories.OffererFactory()
        other_user_offerer = offers_factories.UserOffererFactory(offerer=other_offerer)
        other_venue = offers_factories.VenueFactory(
            name="other_venue_user",
            managingOfferer=other_offerer,
        )

        other_offerer_not_validated = offers_factories.OffererFactory(validationToken="other_token")
        offers_factories.UserOffererFactory(user=other_user_offerer.user, offerer=other_offerer_not_validated)
        other_venue_not_validated = offers_factories.VenueFactory(
            name="other_venue_not_validated",
            managingOfferer=other_offerer_not_validated,
        )

        return {
            "owned_venue_validated": venue,
            "owned_venue_not_validated": venue_not_validated,
            "owned_venue_validated_for_user": venue_validated_for_user,
            "owned_venue_not_validated_for_user": venue_not_validated_for_user,
            "other_venue_user": other_venue,
            "other_venue_not_validated": other_venue_not_validated,
            "venue_from_inactive_offerer": venue_from_inactive_offerer,
        }

    @pytest.mark.usefixtures("db_session")
    def test_response_serializer(self, app):
        # given
        pro_user = users_factories.UserFactory(email="user.pro@test.com", isBeneficiary=False)
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue = offers_factories.VenueFactory(managingOfferer=offerer)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues")

        # then
        assert response.status_code == 200
        assert len(response.json) == 1
        expected_venue = {
            "id": humanize(venue.id),
            "managingOffererId": humanize(venue.managingOffererId),
            "name": venue.name,
            "offererName": offerer.name,
            "publicName": venue.publicName,
            "isVirtual": venue.isVirtual,
            "bookingEmail": venue.bookingEmail,
        }
        assert response.json[0] == expected_venue

    @pytest.mark.usefixtures("db_session")
    def test_get_all_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues")

        # then
        assert response.status_code == 200
        assert len(response.json) == 5

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["owned_venue_validated"].id) in venue_ids
        assert humanize(venues["owned_venue_not_validated"].id) in venue_ids
        assert humanize(venues["owned_venue_validated_for_user"].id) in venue_ids
        assert humanize(venues["owned_venue_not_validated_for_user"].id) in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues?validated=true")

        # then
        assert response.status_code == 200
        assert len(response.json) == 4

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["owned_venue_validated"].id) in venue_ids
        assert humanize(venues["owned_venue_validated_for_user"].id) in venue_ids
        assert humanize(venues["owned_venue_not_validated_for_user"].id) in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_not_validated_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues?validated=false")

        # then
        assert response.status_code == 200
        assert len(response.json) == 1

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["owned_venue_not_validated"].id) in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_for_user_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues?validatedForUser=true")

        # then
        assert response.status_code == 200
        assert len(response.json) == 4

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["owned_venue_validated"].id) in venue_ids
        assert humanize(venues["owned_venue_not_validated"].id) in venue_ids
        assert humanize(venues["owned_venue_validated_for_user"].id) in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_not_validated_for_user_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues?validatedForUser=false")

        # then
        assert response.status_code == 200
        assert len(response.json) == 1

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["owned_venue_not_validated_for_user"].id) in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_venues_from_active_offerers_only(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues?activeOfferersOnly=true")

        # then
        assert response.status_code == 200
        assert len(response.json) == 4

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["venue_from_inactive_offerer"].id) not in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_venues_from_active_and_inactive_offerers(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues?activeOfferersOnly=false")

        # then
        assert response.status_code == 200
        assert len(response.json) == 5

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["venue_from_inactive_offerer"].id) in venue_ids


class Returns200ForAdmin:
    def _setup_venues_for_users(self):
        offerer = offers_factories.OffererFactory()
        user_offerer = offers_factories.UserOffererFactory(offerer=offerer)
        venue = offers_factories.VenueFactory(name="venue", managingOfferer=offerer)

        offerer_not_validated = offers_factories.OffererFactory(validationToken="token")
        offers_factories.UserOffererFactory(user=user_offerer.user, offerer=offerer_not_validated)
        venue_not_validated = offers_factories.VenueFactory(
            name="venue_not_validated", managingOfferer=offerer_not_validated
        )

        other_offerer = offers_factories.OffererFactory()
        other_user_offerer = offers_factories.UserOffererFactory(offerer=other_offerer)
        other_venue = offers_factories.VenueFactory(name="other_venue", managingOfferer=other_offerer)

        other_offerer_not_validated = offers_factories.OffererFactory(validationToken="other_token")
        offers_factories.UserOffererFactory(user=other_user_offerer.user, offerer=other_offerer_not_validated)
        other_venue_not_validated = offers_factories.VenueFactory(
            name="other_venue_not_validated",
            managingOfferer=other_offerer_not_validated,
        )

        return {
            "venue": venue,
            "venue_not_validated": venue_not_validated,
            "other_venue": other_venue,
            "other_venue_not_validated": other_venue_not_validated,
        }

    @pytest.mark.usefixtures("db_session")
    def test_get_all_venues(self, app):
        # given
        admin = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        venues = self._setup_venues_for_users()

        # when
        response = TestClient(app.test_client()).with_auth(admin.email).get("/venues")

        # then
        assert response.status_code == 200
        assert len(response.json) == 4

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["venue"].id) in venue_ids
        assert humanize(venues["venue_not_validated"].id) in venue_ids
        assert humanize(venues["other_venue"].id) in venue_ids
        assert humanize(venues["other_venue_not_validated"].id) in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_venues(self, app):
        # given
        admin = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        venues = self._setup_venues_for_users()

        # when
        response = TestClient(app.test_client()).with_auth(admin.email).get("/venues?validated=true")

        # then
        assert response.status_code == 200
        assert len(response.json) == 2

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["venue"].id) in venue_ids
        assert humanize(venues["other_venue"].id) in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_not_validated_venues(self, app):
        # given
        admin = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        venues = self._setup_venues_for_users()

        # when
        response = TestClient(app.test_client()).with_auth(admin.email).get("/venues?validated=false")

        # then
        assert response.status_code == 200
        assert len(response.json) == 2

        venue_ids = [venue["id"] for venue in response.json]
        assert humanize(venues["venue_not_validated"].id) in venue_ids
        assert humanize(venues["other_venue_not_validated"].id) in venue_ids


class Returns403:
    @pytest.mark.usefixtures("db_session")
    def when_current_user_doesnt_have_rights(self, app):
        # given
        offerer = offers_factories.OffererFactory()
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venue = offers_factories.VenueFactory(name="venue", managingOfferer=offerer)

        # when
        response = TestClient(app.test_client()).with_auth(pro_user.email).get("/venues/%s" % humanize(venue.id))

        # then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
