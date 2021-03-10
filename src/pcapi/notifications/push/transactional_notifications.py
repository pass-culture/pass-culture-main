from dataclasses import dataclass
from typing import List
from typing import Optional


@dataclass
class TransactionalNotificationMessage:
    body: str
    title: Optional[str] = None


@dataclass
class TransactionalNotificationData:
    group_id: str  # Name of the campaign, useful for analytics purpose
    user_ids: List[int]
    message: TransactionalNotificationMessage
