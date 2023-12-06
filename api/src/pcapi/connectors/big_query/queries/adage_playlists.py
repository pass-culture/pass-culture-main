import pydantic.v1 as pydantic_v1

from pcapi import settings

from .base import BaseQuery


class ClassroomPlaylistModel(pydantic_v1.BaseModel):
    collective_offer_id: str
    distance_in_km: float


class ClassroomPlaylistQuery(BaseQuery):
    raw_query = f"""
        SELECT
            distinct collective_offer_id,
            distance_in_km
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_moving_offerers`
        WHERE
            institution_id = @institution_id
        AND
            distance_in_km <= 60
        LIMIT 10
    """

    model = ClassroomPlaylistModel


class NewTemplateOffersPlaylistModel(pydantic_v1.BaseModel):
    collective_offer_id: str
    distance_in_km: float


class NewTemplateOffersPlaylist(BaseQuery):
    raw_query = f"""
        SELECT
            distinct collective_offer_id,
            distance_in_km
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_new_template_offers`
        WHERE
            institution_id = @institution_id
        AND
            distance_in_km <= 60
        ORDER BY distance_in_km ASC
        LIMIT 10
    """

    model = NewTemplateOffersPlaylistModel
