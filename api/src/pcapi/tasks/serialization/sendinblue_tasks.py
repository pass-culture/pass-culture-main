import datetime

import pydantic.v1

from pcapi.routes.serialization import BaseModel


class UpdateSendinblueContactRequest(BaseModel):
    email: str
    attributes: dict
    contact_list_ids: list[int]
    emailBlacklisted: bool


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
    # 2023/11/27 warning: the scheduled_at field is in public beta. (https://developers.brevo.com/reference/sendtransacemail)
    scheduled_at: datetime.datetime | None = None
