import pcapi.core.offerers.factories as offerers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_no_physical_venue():  # type: ignore [no-untyped-def]
    user_offerer = offerers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
    return {"offerer": get_offerer_helper(user_offerer.offerer), "user": get_pro_helper(user_offerer.user)}
