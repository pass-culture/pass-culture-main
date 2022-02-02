from typing import Optional

from pydantic import BaseModel


class UpdateSendinblueContactRequest(BaseModel):
    email: str
    attributes: dict
    contact_list_ids: list[int]
    emailBlacklisted: bool


class SendTransactionalEmailRequest(BaseModel):
    recipients: list[str]
    params: dict
    template_id: int
    tags: Optional[list[str]]
    sender: dict


class UpdateProAttributesRequest(BaseModel):
    email: str
    time_id: str  # see comment in update_pro_attributes_task
