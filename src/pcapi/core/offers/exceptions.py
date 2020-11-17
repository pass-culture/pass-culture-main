from pcapi.domain.client_exceptions import ClientError


class TooLateToDeleteStock(ClientError):
    def __init__(self):
        super().__init__(
            "global",
            "L'événement s'est terminé il y a plus de deux jours, la suppression est impossible.",
        )
