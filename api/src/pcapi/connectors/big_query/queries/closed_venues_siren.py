import enum

import pydantic as pydantic_v2

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery


class ClosedVenueStatusEnum(enum.Enum):
    A = "A"
    F = "F"


class ClosedVenueSirenModel(pydantic_v2.BaseModel):
    venue_id: int
    status: ClosedVenueStatusEnum


def build_big_query_table_name() -> str:
    # the target table has a new/unusual namespace
    # it cannot use the regular settings.BIG_QUERY_TABLE_BASENAME env var
    if settings.IS_PROD:
        return "passculture-data-prod.clean_prod"
    elif settings.IS_STAGING:
        return "passculture-data-ehp.clean_stg"
    else:
        return "passculture-data-ehp.clean_dev"


BIG_QUERY_TABLE_BASENAME = build_big_query_table_name()


class ClosedVenuesSirenQuery(BaseQuery):
    raw_query = f"""
        select
            venue_id,
            etatAdministratifUniteLegale as status,
        from
            -- TODO: table name might not the right
            `{BIG_QUERY_TABLE_BASENAME}.siret_data`
        where
            DATE(dateDernierTraitementEtablissement) >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)
    """

    model = ClosedVenueSirenModel
