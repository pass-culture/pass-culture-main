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


def create_artist_offer_link(offer_id: int, artist_offer_link: artist_serialize.ArtistOfferResponseModel) -> None:
    artist_offer_link = models.ArtistOfferLink(
        offer_id=offer_id,
        artist_id=artist_offer_link.artist_id,
        artist_type=artist_offer_link.artist_type,
        custom_name=artist_offer_link.custom_name,
    )
    db.session.add(artist_offer_link)

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
