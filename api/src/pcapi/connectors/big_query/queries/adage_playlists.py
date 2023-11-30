import pydantic.v1 as pydantic_v1

from pcapi import settings

from .base import BaseQuery


class ClassroomPlaylistModel(pydantic_v1.BaseModel):
    offer_id: int
    distance_in_km: float


class ClassroomPlaylistQuery(BaseQuery):
    raw_query = f"""
        SELECT
            offer_id,
            distance_in_km
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_moving_offerers`
        WHERE
            institution_id = @institution_id
            distance_in_km <= 60
        LIMIT 10
    """

    model = ClassroomPlaylistModel
