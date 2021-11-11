from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_offer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_validated_user_with_at_least_one_visible_activated_offer():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    venue = offers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
    offer = offers_factories.OfferFactory(venue=venue, isActive=True)

    return {"offer": get_offer_helper(offer), "user": get_pro_helper(user_offerer.user)}


def get_existing_pro_validated_user_with_at_least_one_offer_with_at_least_one_thumbnail():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    venue = offers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
    offer = offers_factories.OfferFactory(venue=venue, isActive=True)
    offers_factories.MediationFactory(offer=offer, thumbCount=1)

    return {"offer": get_offer_helper(offer), "user": get_pro_helper(user_offerer.user)}
