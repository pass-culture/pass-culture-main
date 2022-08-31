import dataclasses
from enum import Enum

from pcapi import settings


@dataclasses.dataclass
class MailResult:
    sent_data: dict
    successful: bool


@dataclasses.dataclass
class EmailInfo:
    email: str
    name: str


class TransactionalSender(Enum):
    SUPPORT = EmailInfo(settings.SUPPORT_EMAIL_ADDRESS, "pass Culture")
    SUPPORT_PRO = EmailInfo(settings.SUPPORT_PRO_EMAIL_ADDRESS, "pass Culture")
    COMPLIANCE = EmailInfo(settings.COMPLIANCE_EMAIL_ADDRESS, "pass Culture")


@dataclasses.dataclass
class TransactionalAttachment:
    content: str
    name: str


@dataclasses.dataclass
class TransactionalWithoutTemplateEmailData:
    subject: str
    html_content: str
    sender: TransactionalSender = TransactionalSender.SUPPORT_PRO
    attachment: TransactionalAttachment | None = None
    reply_to: EmailInfo = None  # type: ignore [assignment]

    def __post_init__(self) -> None:
        if self.reply_to is None:
            self.reply_to = self.sender.value


@dataclasses.dataclass
class Template:
    id_prod: int
    id_not_prod: int
    tags: list[str] = dataclasses.field(default_factory=list)
    use_priority_queue: bool = False
    sender: TransactionalSender = TransactionalSender.SUPPORT

    @property
    def id(self) -> int:
        return self.id_prod if settings.IS_PROD else self.id_not_prod


@dataclasses.dataclass
class TemplatePro(Template):
    sender: TransactionalSender = TransactionalSender.SUPPORT_PRO


@dataclasses.dataclass
class TransactionalEmailData:
    template: Template
    params: dict = dataclasses.field(default_factory=dict)
    reply_to: EmailInfo = None  # type: ignore [assignment]

    def __post_init__(self) -> None:
        if self.reply_to is None:
            self.reply_to = self.template.sender.value
