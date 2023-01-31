from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models


def create_users_offerers() -> list[offerers_models.Offerer]:
    offeres = []
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_1_lieu@example.com",
        offerer__name="eac_1_lieu",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_2_lieu@example.com",
        offerer__name="eac_2_lieu [BON EAC]",
        offerer__siren="123456782",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="squad-eac@passculture.app",
        offerer=user_offerer.offerer,
    )
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_3_lieu@example.com",
        offerer__name="eac_3_lieu",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_no_cb@example.com",
        offerer__name="eac_no_cb",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_rejected@example.com",
        offerer__name="eac_rejected",
    )
    offeres.append(user_offerer.offerer)
    return offeres
