from pcapi.routes.serialization import BaseModel


class UpdateSendinblueContactRequest(BaseModel):
    email: str
    attributes: dict
    contact_list_ids: list[int]
    emailBlacklisted: bool


class SendTransactionalEmailRequest(BaseModel):
    recipients: list[str]
    params: dict | None = None
    template_id: int | None = None
    tags: list[str] | None = None
    sender: dict
    subject: str | None = None
    html_content: str | None = None
    attachment: dict | None = None
    reply_to: dict


class UpdateProAttributesRequest(BaseModel):
    email: str
    time_id: str  # see comment in update_pro_attributes_task
