import pydantic


class WebhookRequest(pydantic.BaseModel):
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
    ticket_id: str
    requester_id: str
    requester_email: pydantic.EmailStr | None
    requester_phone: str | None

    @pydantic.validator("requester_phone")
    def check_email_or_phone(cls, requester_phone, values):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        if not values.get("requester_email") and not requester_phone:
            raise ValueError("L'email ou le numéro de téléphone est obligatoire")
        return requester_phone
