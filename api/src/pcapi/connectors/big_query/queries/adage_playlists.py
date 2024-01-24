import pydantic.v1 as pydantic_v1

from pcapi import settings
import pcapi.core.educational.models as educational_models

from .base import BaseQuery


class ClassroomPlaylistModel(pydantic_v1.BaseModel):
    collective_offer_id: str
    distance_in_km: float


class ClassroomPlaylistQuery(BaseQuery):
    raw_query = f"""
        SELECT
            collective_offer_id,
            distance_in_km,
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_moving_offerers`
        WHERE
            institution_id = @institution_id
    """

    model = ClassroomPlaylistModel


class NewTemplateOffersPlaylistModel(pydantic_v1.BaseModel):
    collective_offer_id: str
    distance_in_km: float


class NewTemplateOffersPlaylistQuery(BaseQuery):
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


class LocalOfferersModel(pydantic_v1.BaseModel):
    venue_id: str
    distance_in_km: float


class LocalOfferersQuery(BaseQuery):
    raw_query = f"""
        SELECT
            distinct venue_id,
            distance_in_km
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.adage_home_playlist_local_offerers`
        WHERE
            distance_in_km <= @range
            and institution_id = @institution_id
        LIMIT
            10
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
