import sqlalchemy as sa
from sqlalchemy import case
from sqlalchemy import func

from pcapi import settings
from pcapi.core.artist import models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


def get_artist_search_eligibility_subquery() -> sa.ColumnElement[bool]:
    return sa.and_(
        sa.not_(models.Artist.is_blacklisted),
        models.Artist.app_search_score >= settings.ALGOLIA_ARTIST_MIN_APP_SEARCH_SCORE,
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


def get_similar_artists_for_native(source_artist_id: str) -> list[models.Artist]:
    """Returns the top similar artists for the native app, in DS-defined order.

    Excludes the source artist, blacklisted artists, and artists without an eligible
    offer. Returns an empty list if the source artist is missing or blacklisted.
    """
    # Alias the source artist reference so the inner EXISTS uses a distinct alias from
    # the outer SELECT on `artist`, avoiding any ambiguity in the generated SQL.
    source_artist = sa.orm.aliased(models.Artist, name="source_artist")
    source_artist_is_active = sa.exists().where(
        source_artist.id == source_artist_id,
        sa.not_(source_artist.is_blacklisted),
    )

    return (
        db.session.query(models.Artist)
        .join(
            models.ArtistSimilarArtist,
            models.ArtistSimilarArtist.similar_artist_id == models.Artist.id,
        )
        .filter(
            models.ArtistSimilarArtist.artist_id == source_artist_id,
            models.Artist.id != source_artist_id,
            get_artist_search_eligibility_subquery(),
            source_artist_is_active,
        )
        .order_by(models.ArtistSimilarArtist.similarity_rank.asc())
        .limit(settings.NATIVE_SIMILAR_ARTISTS_MAX_COUNT)
        .all()
    )
