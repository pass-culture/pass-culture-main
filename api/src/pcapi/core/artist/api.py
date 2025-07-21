import sqlalchemy as sa

from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import ImageType
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import ProductMediation
from pcapi.models import db


def get_artist_image_url(artist: Artist) -> str | None:
    image_url = artist.image
    if not image_url:
        most_popular_product_mediation: ProductMediation = (
            db.session.query(ProductMediation)
            .join(Product)
            .filter(
                ProductMediation.productId.in_(
                    sa.select(ArtistProductLink.product_id).filter(ArtistProductLink.artist_id == artist.id)
                )
            )
            .filter(ProductMediation.imageType.in_([ImageType.POSTER, ImageType.RECTO]))
            .order_by(Product.last_30_days_booking.desc(), Product.id.desc())
            .first()
        )

        if most_popular_product_mediation:
            image_url = most_popular_product_mediation.url

    return image_url
