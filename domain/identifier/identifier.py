class Identifier():
    def __init__(self, identifier: int):
        self.identifier: int = identifier

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False

        return self.identifier == other.identifier
