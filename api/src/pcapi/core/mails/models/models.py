import dataclasses


@dataclasses.dataclass
class MailResult:
    sent_data: dict
    successful: bool
