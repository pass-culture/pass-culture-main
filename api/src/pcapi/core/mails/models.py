import dataclasses
from enum import Enum

from pcapi import settings


@dataclasses.dataclass
class EmailInfo:
    email: str
    name: str


class TransactionalSender(Enum):
    SUPPORT = EmailInfo(settings.SUPPORT_EMAIL_ADDRESS, "pass Culture")
    SUPPORT_PRO = EmailInfo(settings.SUPPORT_PRO_EMAIL_ADDRESS, "pass Culture")
    COMPLIANCE = EmailInfo(settings.COMPLIANCE_EMAIL_ADDRESS, "pass Culture")
    DEV = EmailInfo(settings.DEV_EMAIL_ADDRESS, "pass Culture")


@dataclasses.dataclass
class TransactionalAttachment:
    content: str
    name: str


@dataclasses.dataclass
class TransactionalWithoutTemplateEmailData:
    subject: str
    html_content: str
    reply_to: EmailInfo
    sender: TransactionalSender
    attachment: TransactionalAttachment | None

    def __init__(
        self,
        subject: str,
        html_content: str,
        sender: TransactionalSender = TransactionalSender.SUPPORT_PRO,
        attachment: TransactionalAttachment | None = None,
        reply_to: EmailInfo | None = None,
    ):
        self.subject = subject
        self.html_content = html_content
        self.sender = sender
        self.attachment = attachment
        self.reply_to = reply_to or self.sender.value


@dataclasses.dataclass
class Template:
    id_prod: int
    id_not_prod: int
    tags: list[str] = dataclasses.field(default_factory=list)
    use_priority_queue: bool = False
    sender: TransactionalSender = TransactionalSender.SUPPORT
    send_to_ehp: bool = True

    @property
    def id(self) -> int:
        return self.id_prod if settings.IS_PROD else self.id_not_prod


@dataclasses.dataclass
class TemplatePro(Template):
    sender: TransactionalSender = TransactionalSender.SUPPORT_PRO


@dataclasses.dataclass
class TransactionalEmailData:
    template: Template
    reply_to: EmailInfo
    params: dict

    def __init__(self, template: Template, params: dict | None = None, reply_to: EmailInfo | None = None):
        self.template = template
        self.params = params or {}
        self.reply_to = reply_to or template.sender.value
