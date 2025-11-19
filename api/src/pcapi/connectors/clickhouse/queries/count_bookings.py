import pydantic.v1 as pydantic_v1

from pcapi.connectors.clickhouse.queries.base import BaseQuery


class CountIndividualBooking(pydantic_v1.BaseModel):
    quantity: int

    class Config:
        extra = "forbid"
        orm_mode = True


class CountIndividualBookingQuery(BaseQuery[CountIndividualBooking]):
    @property
    def model(self) -> type[CountIndividualBooking]:
        return CountIndividualBooking

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                count(*) AS quantity
            FROM intermediate.booking
            WHERE "venue_id" IN :venue_ids
        """


class CountCollectiveBooking(pydantic_v1.BaseModel):
    quantity: int

    class Config:
        extra = "forbid"
        orm_mode = True


class CountCollectiveBookingQuery(BaseQuery[CountCollectiveBooking]):
    @property
    def model(self) -> type[CountCollectiveBooking]:
        return CountCollectiveBooking

    @property
    def raw_query(self) -> str:
        return """
            SELECT
                count(*) AS quantity
            FROM intermediate.collective_booking
            WHERE "venue_id" IN :venue_ids
        """
