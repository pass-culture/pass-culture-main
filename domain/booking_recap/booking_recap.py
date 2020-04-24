import datetime


class BookingRecap:
    def __init__(self,
                 offer_name,
                 beneficiary_lastname,
                 beneficiary_firstname,
                 beneficiary_email,
                 booking_token,
                 booking_date
                 ):
        self.offer_name: str = offer_name
        self.beneficiary_lastname: str = beneficiary_lastname
        self.beneficiary_firstname: str = beneficiary_firstname
        self.beneficiary_email: str = beneficiary_email
        self.booking_token: str = booking_token
        self.booking_date: datetime = booking_date
