import datetime
import typing

from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer


Metadata = dict[str, typing.Any]


def _get_metadata_from_venue(venue: Venue) -> Metadata:
    return {
        "@type": "Place",
        "name": venue.name,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": venue.address,
            "postalCode": venue.postalCode,
            "addressLocality": venue.city,
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": str(venue.latitude),
            "longitude": str(venue.longitude),
        },
    }


def _get_common_metadata_from_offer(offer: Offer) -> Metadata:
    metadata = {
        "@type": "Product",
        "name": offer.name,
    }

    if offer.image:
        metadata["image"] = offer.image.url

    return metadata


def _get_event_metadata_from_offer(offer: Offer) -> Metadata:
    common_metadata = _get_common_metadata_from_offer(offer)

    event_metadata = {
        "@type": "Event",
        "location": _get_metadata_from_venue(offer.venue),
    }

    if offer.firstBeginningDatetime:
        firstBeginningDatetime: datetime.datetime = offer.firstBeginningDatetime  # type: ignore [assignment]
        event_metadata["startDate"] = firstBeginningDatetime.isoformat(timespec="minutes")

    return common_metadata | event_metadata


def get_metadata_from_offer(offer: Offer) -> Metadata:
    context = {
        "@context": "https://schema.org",
    }

    if offer.isEvent:
        return context | _get_event_metadata_from_offer(offer)

    return context | _get_common_metadata_from_offer(offer)
