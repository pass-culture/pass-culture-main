import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.repository import get_all_offerers_for_user
from pcapi.core.offerers.repository import get_all_venue_labels
from pcapi.core.offerers.repository import get_all_venue_types
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class GetAllVenueLabelsTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_all_venue_labels(self):
        label1 = offerers_factories.VenueLabelFactory()
        label2 = offerers_factories.VenueLabelFactory()

        assert set(get_all_venue_labels()) == {label1, label2}


@pytest.mark.usefixtures("db_session")
class GetAllVenueTypesTest:
    def test_get_all_venue_types(self):
        # Given
        type_1 = offerers_factories.VenueTypeFactory()
        type_2 = offerers_factories.VenueTypeFactory()

        # When
        venue_types = get_all_venue_types()

        # Then
        assert set(venue_types) == {type_1, type_2}


@pytest.mark.usefixtures("db_session")
class GetAllOfferersForUserTest:
    def should_return_all_offerers_for_an_admin(self) -> None:
        # Given
        admin = users_factories.AdminFactory()
        offerer = offers_factories.OffererFactory()

        # When
        offerers = get_all_offerers_for_user(user=admin, filters={})

        # Then
        assert len(offerers) == 1
        assert offerers[0].id == offerer.id

    def should_return_pro_offerers_only(self) -> None:
        # Given
        pro = users_factories.ProFactory()
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
        pro = users_factories.ProFactory()
        pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro, offerer__validationToken="Token")

        # When
        offerers = get_all_offerers_for_user(user=pro, filters={})

        # Then
        assert len(offerers) == 1
        offerers_ids = [offerer.id for offerer in offerers]
        assert pro_offerer_attachment.offerer.id in offerers_ids

    def should_return_offerers_with_non_validated_attachment_to_given_pro(self) -> None:
        # Given
        pro = users_factories.ProFactory()
        unvalidated_pro_offerer_attachment = offers_factories.UserOffererFactory(user=pro, validationToken="Token")

        # When
        offerers = get_all_offerers_for_user(user=pro, filters={})

        # Then
        assert len(offerers) == 1
        offerers_ids = [offerer.id for offerer in offerers]
        assert unvalidated_pro_offerer_attachment.offerer.id in offerers_ids

    def should_not_return_deactivated_offerers(self) -> None:
        # Given
        admin = users_factories.AdminFactory()
        offers_factories.OffererFactory(isActive=False)

        # When
        offerers = get_all_offerers_for_user(user=admin, filters={})

        # Then
        assert len(offerers) == 0

    class WithValidatedFilterTest:
        def should_return_all_pro_offerers_when_filter_is_none(self) -> None:
            # Given
            pro = users_factories.ProFactory()
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
            pro = users_factories.ProFactory()
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
            pro = users_factories.ProFactory()
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
            pro = users_factories.ProFactory()
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
            pro = users_factories.ProFactory()
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
            pro = users_factories.ProFactory()
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
