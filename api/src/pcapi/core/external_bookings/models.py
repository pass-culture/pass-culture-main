from dataclasses import dataclass
from typing import Optional


@dataclass
class Ticket:
    barcode: str
    seat_number: Optional[str]


@dataclass
class Movie:
    id: str
    title: str
    duration: int  # duration in minutes
    description: str
    posterpath: str | None
    visa: str | None


class ExternalBookingsClientAPI:
    # Fixme (yacine, 2022-12-19) remove this method from ExternalBookingsClientAPI. Unlike CDS, on Boost API
    #  we can't get shows remaining places from list of shows ids
    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def cancel_booking(self, barcodes: list[str]) -> None:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def book_ticket(self, show_id: int, quantity: int) -> list[Ticket]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")
