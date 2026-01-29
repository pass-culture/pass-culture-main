from dataclasses import dataclass

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

from pcapi.core.artist import exceptions as artist_exceptions
from pcapi.core.artist import models
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import ImageType
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import ProductMediation
from pcapi.models import db
from pcapi.routes.serialization import artist_serialize


@dataclass(frozen=True)
class ArtistOfferLinkKey:
    artist_type: str
    artist_id: str | None
    custom_name: str | None


def get_artist_image_url(artist: Artist) -> str | None:
    image_url = artist.image
    if not image_url:
        most_popular_product_mediation: ProductMediation | None = (
            db.session.query(ProductMediation)
            .join(Product)
            .filter(
                ProductMediation.productId.in_(
                    sa.select(ArtistProductLink.product_id).filter(ArtistProductLink.artist_id == artist.id)
                )
            )
            .filter(ProductMediation.imageType.in_([ImageType.POSTER, ImageType.RECTO]))
            .order_by(Product.last_30_days_booking.desc().nulls_last(), Product.id.desc())
            .first()
        )

        if most_popular_product_mediation:
            image_url = most_popular_product_mediation.url

    return image_url


def create_artist_offer_link(offer_id: int, artist_offer_link: artist_serialize.ArtistOfferLinkBodyModel) -> None:
    link = models.ArtistOfferLink(
        offer_id=offer_id,
        artist_id=artist_offer_link.artist_id,
        artist_type=artist_offer_link.artist_type,
        custom_name=artist_offer_link.custom_name,
    )
    db.session.add(link)

    try:
        db.session.flush()
    except sa_exc.IntegrityError as error:
        error_str = str(error.orig)
        if "check_has_artist_or_custom_name" in error_str:
            raise artist_exceptions.MissingArtistDataException()
        if "unique_offer_artist_constraint" in error_str:
            raise artist_exceptions.DuplicateArtistException()
        if "unique_offer_custom_artist_constraint" in error_str:
            raise artist_exceptions.DuplicateCustomArtistException()
        if "artist_id" in error_str:
            raise artist_exceptions.InvalidArtistDataException()
        raise error


def _get_artist_offer_link_key(
    link: models.ArtistOfferLink | artist_serialize.ArtistOfferLinkBodyModel,
) -> ArtistOfferLinkKey:
    return ArtistOfferLinkKey(
        artist_type=link.artist_type.value,
        artist_id=link.artist_id,
        custom_name=link.custom_name,
    )


def upsert_artist_offer_links(
    artist_offer_links: list[artist_serialize.ArtistOfferLinkBodyModel], offer: models.Offer
) -> tuple:
    """
    Update artist offer links for a specific offer based on a new list of artist offer links.
    - Deletes existing artist offer links that are not in the new list
    - Creates new artist offer links for entries that don't already exist
    """
    current_links_keys = {_get_artist_offer_link_key(link) for link in offer.artistOfferLinks}
    incoming_links_keys = {_get_artist_offer_link_key(link) for link in artist_offer_links}

    deleted_keys = []
    for current_link in offer.artistOfferLinks:
        key = _get_artist_offer_link_key(current_link)
        if key not in incoming_links_keys:
            db.session.delete(current_link)
            deleted_keys.append(key)

    created_keys = []
    for incoming_link in artist_offer_links:
        key = _get_artist_offer_link_key(incoming_link)
        if key not in current_links_keys:
            create_artist_offer_link(offer.id, incoming_link)
            created_keys.append(key)

    db.session.flush()

    return (
        created_keys,
        deleted_keys,
    )
