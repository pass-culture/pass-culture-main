import dataclasses
from decimal import Decimal

from pcapi import settings
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.offers.models import Offer
from pcapi.models.feature import FeatureToggle


def offer_app_link(offer: CollectiveOffer | Offer) -> str:
    # This link opens the mobile app if installed, the browser app otherwise
    return f"{settings.WEBAPP_V2_URL}/offre/{offer.id}"


def offer_app_redirect_link(offer: Offer) -> str:
    if FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION.is_active():
        return f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}"
    return offer_app_link(offer)


@dataclasses.dataclass
class CalculatedOfferAddress:
    city: str | None
    departmentCode: str | None
    label: str
    latitude: Decimal | None
    longitude: Decimal | None
    postalCode: str | None
    street: str | None


def get_offer_address(offer: Offer) -> CalculatedOfferAddress:
    offerer_address = offer.offererAddress or offer.venue.offererAddress
    if offerer_address:
        return CalculatedOfferAddress(
            city=offerer_address.address.city,
            departmentCode=offerer_address.address.departmentCode,
            label=offerer_address.label or offer.venue.name,
            latitude=offerer_address.address.latitude,
            longitude=offerer_address.address.longitude,
            postalCode=offerer_address.address.postalCode,
            street=offerer_address.address.street,
        )
    return CalculatedOfferAddress(
        city=None,
        departmentCode=None,
        label=offer.venue.name,
        latitude=None,
        longitude=None,
        postalCode=None,
        street=None,
    )
