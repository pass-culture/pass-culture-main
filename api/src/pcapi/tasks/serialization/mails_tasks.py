from pcapi.routes.serialization import BaseModel


class WithdrawalChangedMailBookingDetail(BaseModel):
    recipients: list[str]
    user_first_name: str
    offer_name: str
    offer_token: str


class WithdrawalChangedMailRequest(BaseModel):
    offer_withdrawal_delay: str | None
    offer_withdrawal_details: str | None
    offer_withdrawal_type: str | None
    offerer_name: str
    venue_address: str
    bookers: list[WithdrawalChangedMailBookingDetail]
