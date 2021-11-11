from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_offer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper
from pcapi.sandboxes.scripts.utils.helpers import get_stock_helper
from pcapi.sandboxes.scripts.utils.helpers import get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_no_stock():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    offers_factories.BankInformationFactory(offerer=user_offerer.offerer)
    venue = offers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
    offer = offers_factories.EventOfferFactory(venue=venue, isActive=True)

    return {
        "offer": get_offer_helper(offer),
        "offerer": get_offerer_helper(user_offerer.offerer),
        "user": get_pro_helper(user_offerer.user),
        "venue": get_venue_helper(venue),
    }


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    offers_factories.BankInformationFactory(offerer=user_offerer.offerer)
    venue = offers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
    offer = offers_factories.EventOfferFactory(venue=venue, isActive=True)
    stock = offers_factories.EventStockFactory(offer=offer)

    return {
        "offer": get_offer_helper(offer),
        "offerer": get_offerer_helper(user_offerer.offerer),
        "stock": get_stock_helper(stock),
        "user": get_pro_helper(user_offerer.user),
        "venue": get_venue_helper(venue),
    }


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_thing_offer_with_stock():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    offers_factories.BankInformationFactory(offerer=user_offerer.offerer)
    venue = offers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
    venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offer = offers_factories.ThingOfferFactory(venue=venue, isActive=True)
    stock = offers_factories.ThingStockFactory(offer=offer)

    return {
        "offer": get_offer_helper(offer),
        "offerer": get_offerer_helper(user_offerer.offerer),
        "stock": get_stock_helper(stock),
        "user": get_pro_helper(user_offerer.user),
        "venue": get_venue_helper(venue),
    }
