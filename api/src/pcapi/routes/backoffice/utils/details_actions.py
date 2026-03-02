from enum import StrEnum


class DetailsActions:
    def __init__(self, actions: type[StrEnum], *, threshold: int = 4) -> None:
        self.actions = actions
        self.threshold = threshold
        self.allowed_actions: list[StrEnum] = []

    def add_action(self, action_type: StrEnum) -> None:
        self.allowed_actions.append(action_type)

    def __contains__(self, action_type: StrEnum) -> bool:
        return action_type in self.allowed_actions

    @property
    def inline_actions(self) -> list[StrEnum]:
        return self.allowed_actions[: self.threshold]

    @property
    def additional_actions(self) -> list[StrEnum]:
        return self.allowed_actions[self.threshold :]
