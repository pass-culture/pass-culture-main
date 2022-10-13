import pydantic

from pcapi import settings
from pcapi.utils import chunks

from .base import BaseQuery
from .base import RowIterator


class FavoritesNotBookedModel(pydantic.BaseModel):
    offer_id: int
    offer_name: str
    user_ids: list[int]


class FavoritesNotBooked(BaseQuery):
    raw_query = f"""
        SELECT
            offer_id,
            offer_name,
            ARRAY_AGG(user_id) AS user_ids
        FROM
            `{settings.BIG_QUERY_NOTIFICATIONS_TABLE_BASENAME}.favorites_not_booked`
        WHERE
            execution_date >= CURRENT_DATE()
        GROUP BY
            offer_id, offer_name
    """

    model = FavoritesNotBookedModel

    def execute(self, page_size: int = 1_000) -> RowIterator:
        for row in super().execute(page_size):
            for chunk in chunks.get_chunks(row.user_ids, page_size):  # type: ignore [var-annotated]
                yield FavoritesNotBookedModel(offer_id=row.offer_id, offer_name=row.offer_name, user_ids=chunk)
