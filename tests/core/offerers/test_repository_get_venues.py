import pytest

import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories


class GetFilteredVenuesForProUserTest:
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
    def test_return_value_and_order(self, app):
        # given
        pro_user = users_factories.UserFactory(email="user.pro@test.com", isBeneficiary=False)
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue_2 = offers_factories.VenueFactory(name="BB - name", managingOfferer=offerer)
        venue_1 = offers_factories.VenueFactory(name="AA - name", managingOfferer=offerer)
        venue_3 = offers_factories.VenueFactory(name="CC - name", managingOfferer=offerer)

        # when
        venue_list = offerers_repository.get_filtered_venues(pro_user_id=pro_user.id, user_is_admin=False)

        # then
        assert len(venue_list) == 3
        assert venue_list[0] == venue_1
        assert venue_list[1].name == venue_2.name
        assert venue_list[2].name == venue_3.name

    @pytest.mark.usefixtures("db_session")
    def test_empty_return_value(self, app):
        # given
        pro_user = users_factories.UserFactory(email="user.pro@test.com", isBeneficiary=False)

        # when
        venue_list = offerers_repository.get_filtered_venues(pro_user_id=pro_user.id, user_is_admin=False)

        # then
        assert len(venue_list) == 0

    @pytest.mark.usefixtures("db_session")
    def test_get_all_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        venue_list = offerers_repository.get_filtered_venues(pro_user_id=pro_user.id, user_is_admin=False)

        # then
        assert len(venue_list) == 5

        venue_ids = [venue.id for venue in venue_list]
        assert venues["owned_venue_validated"].id in venue_ids
        assert venues["owned_venue_not_validated"].id in venue_ids
        assert venues["owned_venue_validated_for_user"].id in venue_ids
        assert venues["owned_venue_not_validated_for_user"].id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=pro_user.id,
            user_is_admin=False,
            validated_offerer=True,
        )

        # then
        assert len(venue_list) == 4

        venue_ids = [venue.id for venue in venue_list]
        assert venues["owned_venue_validated"].id in venue_ids
        assert venues["owned_venue_validated_for_user"].id in venue_ids
        assert venues["owned_venue_not_validated_for_user"].id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_not_validated_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=pro_user.id,
            user_is_admin=False,
            validated_offerer=False,
        )

        # then
        assert len(venue_list) == 1

        venue_ids = [venue.id for venue in venue_list]
        assert venues["owned_venue_not_validated"].id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_venues_for_offerer_id(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)
        expected_venue = venues["owned_venue_validated"]

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=pro_user.id,
            user_is_admin=False,
            offerer_id=expected_venue.managingOfferer.id,
        )

        # then
        assert len(venue_list) == 1

        venue_ids = [venue.id for venue in venue_list]
        assert expected_venue.id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_for_user_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=pro_user.id,
            user_is_admin=False,
            validated_offerer_for_user=True,
        )

        # then
        assert len(venue_list) == 4

        venue_ids = [venue.id for venue in venue_list]
        assert venues["owned_venue_validated"].id in venue_ids
        assert venues["owned_venue_not_validated"].id in venue_ids
        assert venues["owned_venue_validated_for_user"].id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_not_validated_for_user_venues(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=pro_user.id,
            user_is_admin=False,
            validated_offerer_for_user=False,
        )

        # then
        assert len(venue_list) == 1

        venue_ids = [venue.id for venue in venue_list]
        assert venues["owned_venue_not_validated_for_user"].id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_venues_from_active_offerers_only(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=pro_user.id,
            user_is_admin=False,
            active_offerers_only=True,
        )

        # then
        assert len(venue_list) == 4

        venue_ids = [venue.id for venue in venue_list]
        assert venues["venue_from_inactive_offerer"].id not in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_venues_from_active_and_inactive_offerers(self, app):
        # given
        pro_user = users_factories.UserFactory(isBeneficiary=False)
        venues = self._setup_venues_for_pro_user(pro_user)

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=pro_user.id,
            user_is_admin=False,
            active_offerers_only=False,
        )

        # then
        assert len(venue_list) == 5

        venue_ids = [venue.id for venue in venue_list]
        assert venues["venue_from_inactive_offerer"].id in venue_ids


class GetFilteredVenuesForAdminTest:
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
        admin = users_factories.AdminFactory()
        venues = self._setup_venues_for_users()

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=admin.id,
            user_is_admin=True,
        )

        # then
        assert len(venue_list) == 4

        venue_ids = [venue.id for venue in venue_list]
        assert venues["venue"].id in venue_ids
        assert venues["venue_not_validated"].id in venue_ids
        assert venues["other_venue"].id in venue_ids
        assert venues["other_venue_not_validated"].id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_venues(self, app):
        # given
        admin = users_factories.AdminFactory()
        venues = self._setup_venues_for_users()

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=admin.id, user_is_admin=True, validated_offerer=True
        )

        # then
        assert len(venue_list) == 2

        venue_ids = [venue.id for venue in venue_list]
        assert venues["venue"].id in venue_ids
        assert venues["other_venue"].id in venue_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_not_validated_venues(self, app):
        # given
        admin = users_factories.AdminFactory()
        venues = self._setup_venues_for_users()

        # when
        venue_list = offerers_repository.get_filtered_venues(
            pro_user_id=admin.id, user_is_admin=True, validated_offerer=False
        )

        # then
        assert len(venue_list) == 2

        venue_ids = [venue.id for venue in venue_list]
        assert venues["venue_not_validated"].id in venue_ids
        assert venues["other_venue_not_validated"].id in venue_ids
