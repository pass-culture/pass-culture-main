import logging
import typing
from dataclasses import dataclass
from functools import partial

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

from pcapi.core.artist import exceptions as artist_exceptions
from pcapi.core.artist import models
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.artist.models import ArtistType
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import ImageType
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import ProductMediation
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.routes.serialization import artist_serialize
from pcapi.utils.string import to_camelcase
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)

# the pro interface sends the pydantic v2 models, the public API the v1 ones
ArtistOfferLinkBody = artist_serialize.ArtistOfferLinkBodyModel | artist_serialize.ArtistOfferLinkBodyModelV2


@dataclass(frozen=True)
class ArtistOfferLinkKey:
    artist_type: ArtistType
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


def create_artist_offer_link(offer_id: int, artist_offer_link: ArtistOfferLinkKey) -> None:
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


def get_artist_offer_link_key(
    link: models.ArtistOfferLink | ArtistOfferLinkBody,
) -> ArtistOfferLinkKey:
    custom_name = link.artist_name if link.artist_id is None else None
    return ArtistOfferLinkKey(
        artist_type=link.artist_type,
        artist_id=link.artist_id,
        custom_name=custom_name,
    )


def check_artist_offer_links(
    artist_offer_links: typing.Sequence[ArtistOfferLinkBody], subcategory: subcategories.Subcategory
) -> None:
    for link in artist_offer_links:
        # TODO (tpommellet-pass): refacto once artists are no longer stored in extradata
        # Convert snake_case ArtistType values to camelCase to match conditional_fields keys (ArtistFieldEnum)
        if to_camelcase(link.artist_type.value) not in subcategory.conditional_fields:
            raise api_errors.ApiErrors(
                errors={"artistOfferLinks": ["Le type d'artiste n'est pas autorisé pour cette sous catégorie"]}
            )


def upsert_artist_offer_links(
    artist_offer_links: typing.Sequence[ArtistOfferLinkBody],
    offer: models.Offer,
    *,
    subcategory_id: str | None = None,
) -> tuple:
    """
    Update artist offer links for a specific offer based on a new list of artist offer links.
    - Deletes existing artist offer links that are not in the new list
    - Creates new artist offer links for entries that don't already exist
    """
    subcategory = subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id or offer.subcategoryId]
    check_artist_offer_links(artist_offer_links, subcategory)

    current_links_keys = {get_artist_offer_link_key(link) for link in offer.artistOfferLinks}
    incoming_links_keys = {get_artist_offer_link_key(link) for link in artist_offer_links}

    deleted_keys = []
    for current_link in offer.artistOfferLinks:
        current_key = get_artist_offer_link_key(current_link)
        if current_key not in incoming_links_keys:
            db.session.delete(current_link)
            deleted_keys.append(current_key)

    created_keys = []
    for incoming_key in incoming_links_keys:
        if incoming_key not in current_links_keys:
            create_artist_offer_link(offer.id, incoming_key)
            created_keys.append(incoming_key)

    db.session.flush()
    db.session.expire(offer, ["artistOfferLinks"])

    if deleted_keys:
        on_commit(
            partial(
                logger.info,
                "Artist offer links have been deleted",
                extra={"offer_id": offer.id, "venue_id": offer.venueId, "links": [str(k) for k in deleted_keys]},
                technical_message_id="offer.artistOfferLinks.deleted",
            )
        )
    if created_keys:
        on_commit(
            partial(
                logger.info,
                "Artist offer links have been created",
                extra={"offer_id": offer.id, "venue_id": offer.venueId, "links": [str(k) for k in created_keys]},
                technical_message_id="offer.artistOfferLinks.created",
            )
        )

    return (
        created_keys,
        deleted_keys,
    )
