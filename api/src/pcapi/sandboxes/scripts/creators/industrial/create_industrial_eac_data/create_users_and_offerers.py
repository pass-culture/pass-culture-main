from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models


def create_users_offerers() -> list[offerers_models.Offerer]:
    offerers = []
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_1_lieu@example.com",
        offerer__name="eac_1_lieu",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_2_lieu@example.com",
        offerer__name="eac_2_lieu [BON EAC]",
        offerer__siren="123456782",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="squad-eac@passculture.app",
        offerer=user_offerer.offerer,
    )

    # user with 2 offerer 1 eac and 1 non eac
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="half_eac@example.com",
        offerer=user_offerer.offerer,
    )
    offerers_factories.UserOffererFactory(
        user=user_offerer.user,
        offerer__name="no_eac",
    )

    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_pending_bank_informations@example.com",
        offerer__name="eac_pending_bank_informations",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_no_cb@example.com",
        offerer__name="eac_no_cb",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_rejected@example.com",
        offerer__name="eac_rejected",
    )
    offerers.append(user_offerer.offerer)
    # DMS state
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_accepte@example.com",
        offerer__name="eac_accepte",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_sans_suite@example.com",
        offerer__name="eac_sans_suite",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_en_construction@example.com",
        offerer__name="eac_en_construction",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_refuse@example.com",
        offerer__name="eac_refuse",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_en_instruction@example.com",
        offerer__name="eac_en_instruction",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_complete_30d@example.com",
        offerer__name="eac_complete_30+d",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_complete_30-d@example.com",
        offerer__name="eac_complete_30-d",
    )
    offerers.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_with_two_adage_venues@example.com",
        offerer__name="eac_with_two_adage_venues",
    )
    offerers.append(user_offerer.offerer)

    return offerers
