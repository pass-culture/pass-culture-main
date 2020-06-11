from domain.booking.booking import Booking


class BookingWithOfferer(Booking):
    def __init__(self, managing_offerer_id: int, **kwargs):
        super().__init__(**kwargs)
        self.managing_offerer_id = managing_offerer_id
