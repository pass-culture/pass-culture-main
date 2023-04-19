from . import Event


class ExternalServiceBackend:
    def handle_event(self, event: Event) -> None:
        raise NotImplementedError()
