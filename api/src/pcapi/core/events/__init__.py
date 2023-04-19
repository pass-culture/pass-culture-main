import dataclasses

from . import config


@dataclasses.dataclass
class Event:
    name: config.EventName
    payload: dict
    user_ids: list[int]
