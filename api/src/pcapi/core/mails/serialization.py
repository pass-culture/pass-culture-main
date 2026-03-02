from pydantic import BaseModel as BaseModelV2
from pydantic import Field


class UpdateSendinblueContactRequest(BaseModelV2):
    email: str
    use_pro_subaccount: bool
    attributes: dict
    contact_list_ids: list[int] | None
    emailBlacklisted: bool


class SendTransactionalEmailRequest(BaseModelV2):
    recipients: list[str]
    bcc_recipients: list[str] = Field(default_factory=list)
    params: dict | None = None
    template_id: int | None = None
    tags: list[str] | None = None
    sender: dict | None = None
    subject: str | None = None
    html_content: str | None = None
    attachment: dict | None = None
    reply_to: dict | None = None
    enable_unsubscribe: bool | None = False
    use_pro_subaccount: bool | None = False  # or None to handle queued emails at deployment time
