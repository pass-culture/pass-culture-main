from datetime import datetime


class BookingRecapHistory:
    def __init__(self, booking_date: datetime, confirmation_date: datetime | None = None):
        self.booking_date = booking_date
        self.confirmation_date = confirmation_date


class BookingRecapConfirmedHistory(BookingRecapHistory):
    def __init__(self, cancellation_limit_date: datetime | None, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(**kwargs)
        self.date_confirmed = cancellation_limit_date


class BookingRecapValidatedHistory(BookingRecapConfirmedHistory):
    def __init__(self, date_used: datetime, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(**kwargs)
        self.date_used = date_used


class BookingRecapReimbursedHistory(BookingRecapValidatedHistory):
    def __init__(self, payment_date: datetime, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(**kwargs)
        self.payment_date = payment_date


class BookingRecapCancelledHistory(BookingRecapHistory):
    def __init__(self, cancellation_date: datetime, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(**kwargs)
        self.cancellation_date = cancellation_date


class BookingRecapPendingHistory(BookingRecapHistory):
    def __init__(self, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(**kwargs)
