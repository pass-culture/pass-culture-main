from typing import Optional

from pcapi.routes.serialization import BaseModel


class UpdateSendinblueContactRequest(BaseModel):
    email: str
    attributes: dict
    contact_list_ids: list[int]
    emailBlacklisted: bool


class SendTransactionalEmailRequest(BaseModel):
    recipients: list[str]
    params: Optional[dict] = None
    template_id: Optional[int] = None
    tags: Optional[list[str]] = None
    sender: dict
    subject: Optional[str] = None
    html_content: Optional[str] = None
    attachment: Optional[dict] = None


class UpdateProAttributesRequest(BaseModel):
    email: str
    time_id: str  # see comment in update_pro_attributes_task
