import enum

import pydantic as pydantic_v2

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery


class ClosedVenueStatusEnum(enum.Enum):
    A = "A"
    F = "F"


class ClosedVenueSirenModel(pydantic_v2.BaseModel):
    siret: str
    status: ClosedVenueStatusEnum


class ClosedVenuesSirenQuery(BaseQuery):
    model = ClosedVenueSirenModel

    def __init__(self, days_count: int) -> None:
        self.days_count = days_count

    @property
    def raw_query(self) -> str:
        return f"""
            select
                siret,
                etatAdministratifUniteLegale as status,
            from
                -- TODO: table name might not the right
                `{settings.BIG_QUERY_CLEANED_TABLE_BASENAME}.siret_data`
            where
                DATE(dateDernierTraitementEtablissement) >= DATE_SUB(CURRENT_DATE(), INTERVAL {self.days_count} DAY)
        """
