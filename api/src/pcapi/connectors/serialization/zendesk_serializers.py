import pydantic
import pydantic.v1 as pydantic_v1


class WebhookRequest(pydantic_v1.BaseModel):
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
    requester_email: pydantic_v1.EmailStr | None
    requester_phone: str | None

    @pydantic_v1.validator("requester_phone")
    def check_email_or_phone(cls, requester_phone: str | None, values: dict) -> str | None:
        if not values.get("requester_email") and not requester_phone:
            raise ValueError("L'email ou le numéro de téléphone est obligatoire")
        return requester_phone


class WebhookFormRequest(pydantic.BaseModel):
    """
    JSON body in Zendesk configuration for the new ticket trigger:
    {
        "ticket_id": "{{ticket.id}}",
        "requester_id": "{{ticket.requester.id}}",
        "requester_email": "{{ticket.requester.email}}",
        "first_name": "{{ticket.requester.first_name}}",
        "dossier_dn": "{{ticket.ticket_field_360029090437}}"
    }
    Example for webhook test in Zendesk:
    {
        "ticket_id": "1",
        "requester_id": "2",
        "requester_email": "patrick@example.com",
        "first_name": "Patrick",
        "dossier_dn": "123"
    }
    """

    ticket_id: str
    requester_id: str
    requester_email: pydantic.EmailStr
    first_name: str
    dossier_dn: int | str | None
