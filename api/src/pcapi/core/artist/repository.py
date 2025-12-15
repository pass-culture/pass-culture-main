import sqlalchemy as sa
from sqlalchemy import case
from sqlalchemy import func

from pcapi.core.artist import models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


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


def get_filtered_artists_for_search(search_value: str) -> list[models.Artist]:
    lower_unaccent_name = func.lower(func.immutable_unaccent(models.Artist.name))
    lower_unaccent_search = func.lower(func.immutable_unaccent(search_value))

    priority = case(
        (lower_unaccent_name == lower_unaccent_search, 0),  # exact match
        else_=1,  # partial match
    )
    return (
        db.session.query(models.Artist)
        .filter(
            sa.not_(models.Artist.is_blacklisted),
            models.Artist.wikidata_id.is_not(None),
            func.immutable_unaccent(models.Artist.name).ilike(func.immutable_unaccent(f"%{search_value}%")),
        )
        .order_by(priority, models.Artist.name)
        .limit(5)
        .all()
    )
