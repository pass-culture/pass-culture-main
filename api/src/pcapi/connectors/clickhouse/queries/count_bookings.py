import dataclasses

from pcapi.connectors.clickhouse.queries.base import BaseQuery
from pcapi.connectors.clickhouse.queries.base import ClickHouseBaseModel


class CountBookings(ClickHouseBaseModel):
    individual_bookings: int
    collective_bookings: int


@dataclasses.dataclass
class _Row:
    individual_bookings: int
    collective_bookings: int


class CountBookingsQuery(BaseQuery[CountBookings, _Row]):
    @property
    def model(self) -> type[CountBookings]:
        return CountBookings

    @property
    def raw_query(self) -> str:
        return """
            SELECT
            (
                SELECT
                    count(*)
                FROM
                    intermediate.booking
                WHERE
                    "venue_id" IN :venue_ids
            ) AS individual_bookings,
            (
                SELECT
                    count(*)
                FROM
                    intermediate.collective_booking
                WHERE
                    "venue_id" IN :venue_ids
            ) AS collective_bookings

        """
