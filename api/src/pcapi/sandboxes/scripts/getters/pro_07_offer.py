from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper
from pcapi.sandboxes.scripts.utils.helpers import get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offers_factories.OfferFactory(venue=venue, isActive=True)

    return {
        "offerer": get_offerer_helper(user_offerer.offerer),
        "user": get_pro_helper(user_offerer.user),
        "venue": get_venue_helper(venue),
    }
