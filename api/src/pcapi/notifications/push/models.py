from dataclasses import dataclass


@dataclass
class UpdateAttributeRequestResult:
    should_retry: bool
