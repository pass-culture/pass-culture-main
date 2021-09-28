import dataclasses
from enum import Enum

from pcapi import settings


@dataclasses.dataclass
class Template:
    id_prod: int
    id_not_prod: int
    tags: list[str] = dataclasses.field(default_factory=list)
    # Tag your emails to find them more easily cf doc https://developers.sendinblue.com/reference/sendtransacemail

    @property
    def id(self):
        return self.id_prod if settings.IS_PROD else self.id_not_prod


class TransactionalEmail(Enum):
    EMAIL_CONFIRMATION = Template(id_prod=201, id_not_prod=15, tags=["jeunes_confirmation_mail"])


@dataclasses.dataclass
class SendinblueTransactionalEmailData:
    template: Template
    params: dict
