from typing import Annotated

import pydantic as pydantic_v2

from pcapi.serialization.exceptions import PydanticError


IdField = Annotated[str, pydantic_v2.Field(pattern=r"^\d+$")] | int


class WebhookRequest(pydantic_v2.BaseModel):
    """
    JSON body in Zendesk configuration for the new ticket trigger:
    {
        "is_new_ticket": true,
        "ticket_id": "{{ticket.id}}",
        "requester_id": "{{ticket.requester.id}}",
        "requester_email": "{{ticket.requester.email}}",
        "requester_phone": "{{ticket.requester.phone}}"
    }

    Another trigger is created for ticket update notification, with the same body except:
        "is_new_ticket": false,
    """

    is_new_ticket: bool
    ticket_id: IdField
    requester_id: IdField
    requester_email: pydantic_v2.EmailStr | None
    requester_phone: str | None

    @pydantic_v2.field_validator("requester_phone")
    @classmethod
    def check_email_or_phone(cls, requester_phone: str | None, info: pydantic_v2.ValidationInfo) -> str | None:
        if not info.data.get("requester_email") and not requester_phone:
            raise PydanticError("L'email ou le numéro de téléphone est obligatoire")
        return requester_phone
