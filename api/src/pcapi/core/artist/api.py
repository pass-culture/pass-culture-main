import sqlalchemy as sa
from sqlalchemy import func

from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.offers.models import ImageType
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import ProductMediation
from pcapi.models import db


def update_artists_image_from_products(artists: list[Artist]) -> None:
    if not artists:
        return

    artist_ids_to_update = [artist.id for artist in artists if artist.image is None]

    if not artist_ids_to_update:
        return

    ranked_mediations_sq = (
        sa.select(
            ArtistProductLink.artist_id,
            ProductMediation.url,
            func.row_number()
            .over(
                partition_by=ArtistProductLink.artist_id,
                order_by=[Product.last_30_days_booking.desc().nulls_last(), Product.id.desc()],
            )
            .label("rank"),
        )
        .join(Product, ArtistProductLink.product_id == Product.id)
        .join(ProductMediation, Product.id == ProductMediation.productId)
        .where(
            ArtistProductLink.artist_id.in_(artist_ids_to_update),
            ProductMediation.imageType.in_([ImageType.POSTER, ImageType.RECTO]),
        )
        .subquery()
    )

    top_mediations_sq = (
        sa.select(ranked_mediations_sq.c.artist_id, ranked_mediations_sq.c.url)
        .where(ranked_mediations_sq.c.rank == 1)
        .subquery()
    )

    update_query = (
        sa.update(Artist).where(Artist.id == top_mediations_sq.c.artist_id).values(image=top_mediations_sq.c.url)
    )

    db.session.execute(update_query)
