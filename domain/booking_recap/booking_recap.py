import datetime


class BookingRecap:
    offer_name = str
    beneficiary_lastname = str
    beneficiary_firstname = str
    beneficiary_email = str
    booking_token = str
    booking_date = datetime

    def __init__(self,
                 offer_name,
                 beneficiary_lastname,
                 beneficiary_firstname,
                 beneficiary_email,
                 booking_token,
                 booking_date
                 ):
        self.offer_name = offer_name
        self.beneficiary_lastname = beneficiary_lastname
        self.beneficiary_firstname = beneficiary_firstname
        self.beneficiary_email = beneficiary_email
        self.booking_token = booking_token
        self.booking_date = booking_date
