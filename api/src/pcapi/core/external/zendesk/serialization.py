from pydantic import BaseModel as BaseModelV2


class UpdateZendeskAttributesRequest(BaseModelV2):
    is_new_ticket: bool
    ticket_id: int
    zendesk_user_id: int
    email: str | None
    phone_number: str | None
