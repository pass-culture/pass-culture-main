from typing import Iterable
from typing import Optional

from pydantic import BaseModel


class UpdateSendinblueContactRequest(BaseModel):
    email: str
    attributes: dict
    contact_list_ids: list[int]
    emailBlacklisted: bool


class SendTransactionalEmailRequest(BaseModel):
    recipients: Iterable
    params: dict
    template_id: int
    tags: Optional[list[str]]
