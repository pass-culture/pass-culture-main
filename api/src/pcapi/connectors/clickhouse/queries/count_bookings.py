import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery


class CountBookings(pydantic_v1.BaseModel):
    individual_bookings: int
    collective_bookings: int

    class Config:
        extra = "forbid"
        orm_mode = True


class CountBookingsQuery(BaseQuery[CountBookings]):
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
