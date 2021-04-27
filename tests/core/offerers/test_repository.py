import pytest

from pcapi.core.offerers.repository import get_all_offerers_for_user
from pcapi.core.offerers.repository import get_filtered_venues
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class GetAllOfferersForUserTest:
    def should_return_all_offerers_for_an_admin(self) -> None:
        # Given
        admin = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        offerer = offers_factories.OffererFactory()

        # When
        offerers = get_all_offerers_for_user(user=admin, filters={})

        # Then
        assert len(offerers) == 1
        assert offerers[0].id == offerer.id

    def should_return_pro_offerers_only(self) -> None:
        # Given
        pro = users_factories.UserFactory(isBeneficiary=False)
        pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro)
        other_offerer = offers_factories.OffererFactory()

        # When
        offerers = get_all_offerers_for_user(user=pro, filters={})

        # Then
        assert len(offerers) == 1
        offerers_ids = [offerer.id for offerer in offerers]
        assert pro_offerer_attachment.offerer.id in offerers_ids
        assert other_offerer.id not in offerers_ids

    def should_return_non_validated_offerers(self) -> None:
        # Given
        pro = users_factories.UserFactory(isBeneficiary=False)
        pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro, offerer__validationToken="Token")

        # When
        offerers = get_all_offerers_for_user(user=pro, filters={})

        # Then
        assert len(offerers) == 1
        offerers_ids = [offerer.id for offerer in offerers]
        assert pro_offerer_attachment.offerer.id in offerers_ids

    def should_return_offerers_with_non_validated_attachment_to_given_pro(self) -> None:
        # Given
        pro = users_factories.UserFactory(isBeneficiary=False)
        unvalidated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro, validationToken="Token")

        # When
        offerers = get_all_offerers_for_user(user=pro, filters={})

        # Then
        assert len(offerers) == 1
        offerers_ids = [offerer.id for offerer in offerers]
        assert unvalidated_pro_offerer_attachment.offerer.id in offerers_ids

    def should_not_return_deactivated_offerers(self) -> None:
        # Given
        admin = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        offers_factories.OffererFactory(isActive=False)

        # When
        offerers = get_all_offerers_for_user(user=admin, filters={})

        # Then
        assert len(offerers) == 0

    class WithValidatedFilterTest:
        def should_return_all_pro_offerers_when_filter_is_none(self) -> None:
            # Given
            pro = users_factories.UserFactory(isBeneficiary=False)
            pro_attachment_to_validated_offerer = offers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_unvalidated_offerer = offers_factories.UserOffererFactory(
                user=pro, offerer__validationToken="Token"
            )

            # When
            offerers = get_all_offerers_for_user(
                user=pro,
                filters={
                    "validated": None,
                },
            )

            # Then
            assert len(offerers) == 2
            offerers_ids = [offerer.id for offerer in offerers]
            assert pro_attachment_to_validated_offerer.offerer.id in offerers_ids
            assert pro_attachment_to_unvalidated_offerer.offerer.id in offerers_ids

        def should_return_only_validated_offerers_when_filter_is_true(self) -> None:
            # Given
            pro = users_factories.UserFactory(isBeneficiary=False)
            pro_attachment_to_validated_offerer = offers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_unvalidated_offerer = offers_factories.UserOffererFactory(
                user=pro, offerer__validationToken="Token"
            )

            # When
            offerers = get_all_offerers_for_user(
                user=pro,
                filters={
                    "validated": True,
                },
            )

            # Then
            assert len(offerers) == 1
            offerers_ids = [offerer.id for offerer in offerers]
            assert pro_attachment_to_validated_offerer.offerer.id in offerers_ids
            assert pro_attachment_to_unvalidated_offerer.offerer.id not in offerers_ids

        def should_return_only_unvalidated_offerers_when_filter_is_false(self) -> None:
            # Given
            pro = users_factories.UserFactory(isBeneficiary=False)
            pro_attachment_to_validated_offerer = offers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_unvalidated_offerer = offers_factories.UserOffererFactory(
                user=pro, offerer__validationToken="Token"
            )

            # When
            offerers = get_all_offerers_for_user(
                user=pro,
                filters={
                    "validated": False,
                },
            )

            # Then
            assert len(offerers) == 1
            offerers_ids = [offerer.id for offerer in offerers]
            assert pro_attachment_to_validated_offerer.offerer.id not in offerers_ids
            assert pro_attachment_to_unvalidated_offerer.offerer.id in offerers_ids

    class WithValidatedForUserFilterTest:
        def should_return_all_pro_offerers_when_filter_is_none(self) -> None:
            # Given
            pro = users_factories.UserFactory(isBeneficiary=False)
            validated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro)
            unvalidated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro, validationToken="Token")

            # When
            offerers = get_all_offerers_for_user(
                user=pro,
                filters={
                    "validated_for_user": None,
                },
            )

            # Then
            assert len(offerers) == 2
            offerers_ids = [offerer.id for offerer in offerers]
            assert validated_pro_offerer_attachment.offerer.id in offerers_ids
            assert unvalidated_pro_offerer_attachment.offerer.id in offerers_ids

        def should_return_only_offerers_with_validated_attachment_when_filter_is_true(self) -> None:
            # Given
            pro = users_factories.UserFactory(isBeneficiary=False)
            validated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro)
            unvalidated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro, validationToken="Token")

            # When
            offerers = get_all_offerers_for_user(
                user=pro,
                filters={
                    "validated_for_user": True,
                },
            )

            # Then
            assert len(offerers) == 1
            offerers_ids = [offerer.id for offerer in offerers]
            assert validated_pro_offerer_attachment.offerer.id in offerers_ids
            assert unvalidated_pro_offerer_attachment.offerer.id not in offerers_ids

        def should_return_only_offerers_with_unvalidated_attachment_when_filter_is_false(self) -> None:
            # Given
            pro = users_factories.UserFactory(isBeneficiary=False)
            validated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro)
            unvalidated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro, validationToken="Token")

            # When
            offerers = get_all_offerers_for_user(
                user=pro,
                filters={
                    "validated_for_user": False,
                },
            )

            # Then
            assert len(offerers) == 1
            offerers_ids = [offerer.id for offerer in offerers]
            assert validated_pro_offerer_attachment.offerer.id not in offerers_ids
            assert unvalidated_pro_offerer_attachment.offerer.id in offerers_ids


@pytest.mark.usefixtures("db_session")
class GetFilteredVenuesTest:
    def test_get_all_venue_by_pro_user(self) -> None:
        # Given
        user_offerer = offers_factories.UserOffererFactory(
            offerer__name="Gilbert Joseph",
            offerer__validationToken=None,
            user__isAdmin=False,
            user__isBeneficiary=False,
            validationToken=None,
        )
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            name="Librairie Kléber",
            isVirtual=False,
        )
        offers_factories.VenueFactory()

        # When
        venue_list = get_filtered_venues(pro_user_id=user_offerer.user.id, user_is_admin=False)

        # Then
        assert len(venue_list) == 1
        assert venue_list[0].id == venue.id
