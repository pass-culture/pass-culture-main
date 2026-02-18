from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery


class OfferQualityModel(BaseModelV2):
    offer_id: int
    completion_score: float


class OfferQualityQuery(BaseQuery):
    def __init__(self, start_from_id: int = 0):
        super().__init__()
        self.start_from_id = start_from_id

    @property
    def raw_query(self) -> str:
        return self._build_query()

    def _build_query(self) -> str:
        where_clause = ""
        if self.start_from_id > 0:
            where_clause = f"WHERE CAST(offer_id AS INT64) >= {self.start_from_id}"
        return f"""
            SELECT
                offer_id,
                completion_score
            FROM
                `{settings.BIG_QUERY_TABLE_BASENAME}.offer_quality`
            {where_clause}
            ORDER BY
                CAST(offer_id AS INT64) ASC
        """

    model = OfferQualityModel
