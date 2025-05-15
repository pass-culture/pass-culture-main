import pydantic.v1 as pydantic_v1

import pcapi.core.educational.models as educational_models
from pcapi import settings

from .base import BaseQuery


class ClassroomPlaylistModel(pydantic_v1.BaseModel):
    institution_id: str
    collective_offer_id: str
    distance_in_km: float


class ClassroomPlaylistQuery(BaseQuery):
    raw_query = f"""
        SELECT
            collective_offer_id,
            distance_in_km,
            institution_id
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_moving_offerers`
        WHERE
            distance_in_km <= 60
        ORDER BY
            institution_id
    """

    model = ClassroomPlaylistModel


class NewTemplateOffersPlaylistModel(pydantic_v1.BaseModel):
    institution_id: str
    collective_offer_id: str
    distance_in_km: float


class NewTemplateOffersPlaylistQuery(BaseQuery):
    raw_query = f"""
        SELECT
            distinct collective_offer_id,
            distance_in_km,
            institution_id
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_new_template_offers`
        WHERE
            distance_in_km <= 60
        ORDER BY
            institution_id
    """

    model = NewTemplateOffersPlaylistModel


class LocalOfferersModel(pydantic_v1.BaseModel):
    institution_id: str
    venue_id: str
    distance_in_km: float


class LocalOfferersQuery(BaseQuery):
    raw_query = f"""
        SELECT
            institution_id,
            venue_id,
            MIN(distance_in_km) as distance_in_km
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_local_offerers`
        WHERE
            distance_in_km <= 60
        GROUP BY
            institution_id, venue_id
        ORDER BY
            institution_id, venue_id
    """

    model = LocalOfferersModel


class InstitutionRuralLevelModel(pydantic_v1.BaseModel):
    institution_id: int
    institution_rural_level: educational_models.InstitutionRuralLevel | None

    class Config:
        use_enum_values = True


class InstitutionRuralLevelQuery(BaseQuery):
    raw_query = f"""
        SELECT
            DISTINCT institution_id, institution_rural_level,
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_moving_offerers`
    """

    model = InstitutionRuralLevelModel


class NewOffererQuery(BaseQuery):
    raw_query = f"""
        SELECT
            institution_id,
            venue_id,
            MIN(distance_in_km) as distance_in_km
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_new_venues`
        WHERE
            distance_in_km <= 60
        GROUP BY
            institution_id, venue_id
        ORDER BY
            institution_id, venue_id
    """

    model = LocalOfferersModel
