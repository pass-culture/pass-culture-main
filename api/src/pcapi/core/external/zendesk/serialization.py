# TODO (prouzet, 2026-01-05) We can remove .v1 when GCP task is removed from code; because of:
#   File "/usr/src/app/src/pcapi/tasks/decorator.py", line 35, in decorator
#     assert issubclass(payload_type, pydantic_v1.BaseModel)
from pydantic.v1 import BaseModel


class UpdateZendeskAttributesRequest(BaseModel):
    is_new_ticket: bool
    ticket_id: int
    zendesk_user_id: int
    email: str | None
    phone_number: str | None


class ZendeskCheckUpdateRequestStatus(BaseModel):
    ticket_id: int
    zendesk_user_id: int
    email: str
    first_name: str
    dossier_dn: int | str | None
