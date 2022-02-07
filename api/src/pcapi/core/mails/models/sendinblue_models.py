import dataclasses
from enum import Enum
from typing import Optional

from pcapi import settings


@dataclasses.dataclass
class SenderInfo:
    email: str
    name: str


class SendinblueTransactionalSender(Enum):
    SUPPORT = SenderInfo(settings.SUPPORT_EMAIL_ADDRESS, "pass Culture")
    SUPPORT_PRO = SenderInfo(settings.SUPPORT_PRO_EMAIL_ADDRESS, "pass Culture")
    COMPLIANCE = SenderInfo(settings.COMPLIANCE_EMAIL_ADDRESS, "pass Culture")


@dataclasses.dataclass
class SendinblueTransactionalAttachment:
    content: str
    name: str


@dataclasses.dataclass
class SendinblueTransactionalWithoutTemplateEmailData:
    subject: str
    html_content: str
    sender: SendinblueTransactionalSender = SendinblueTransactionalSender.SUPPORT_PRO
    attachment: Optional[SendinblueTransactionalAttachment] = None


@dataclasses.dataclass
class Template:
    id_prod: int
    id_not_prod: int
    tags: list[str] = dataclasses.field(default_factory=list)
    use_priority_queue: bool = False
    sender: SendinblueTransactionalSender = SendinblueTransactionalSender.SUPPORT

    @property
    def id(self) -> int:
        return self.id_prod if settings.IS_PROD else self.id_not_prod


@dataclasses.dataclass
class TemplatePro(Template):
    sender: SendinblueTransactionalSender = SendinblueTransactionalSender.SUPPORT_PRO


@dataclasses.dataclass
class SendinblueTransactionalEmailData:
    template: Template
    params: dict = dataclasses.field(default_factory=dict)
