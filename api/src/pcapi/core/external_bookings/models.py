from dataclasses import dataclass
from typing import Optional


@dataclass
class Ticket:
    barcode: str
    seat_number: Optional[str]


class ExternalBookingsClientAPI:
    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def cancel_booking(self, barcodes: list[str]) -> None:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def book_ticket(self, show_id: int, quantity: int) -> list[Ticket]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")
