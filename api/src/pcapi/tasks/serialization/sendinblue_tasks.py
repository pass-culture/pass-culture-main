import pydantic.v1

from pcapi.routes.serialization import BaseModel


class UpdateSendinblueContactRequest(BaseModel):
    email: str
    attributes: dict
    contact_list_ids: list[int] | None = None
    emailBlacklisted: bool | None = None


class SendTransactionalEmailRequest(BaseModel):
    recipients: list[str]
    bcc_recipients: list[str] = pydantic.v1.Field(default_factory=list)
    params: dict | None = None
    template_id: int | None = None
    tags: list[str] | None = None
    sender: dict
    subject: str | None = None
    html_content: str | None = None
    attachment: dict | None = None
    reply_to: dict
