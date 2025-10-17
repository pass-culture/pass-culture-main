import sqlalchemy as sa

from pcapi.core.artist import models
from pcapi.core.offers import models as offers_models


def get_artist_search_eligibility_subquery() -> sa.ColumnElement[bool]:
    return sa.and_(
        sa.not_(models.Artist.is_blacklisted),
        sa.select(1)
        .select_from(models.ArtistProductLink)
        .join(offers_models.Product)
        .join(offers_models.Offer)
        .join(offers_models.Stock)
        .where(offers_models.Offer.is_eligible_for_search, models.ArtistProductLink.artist_id == models.Artist.id)
        .exists(),
    )
