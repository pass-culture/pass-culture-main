import humanize

from pcapi.domain.client_exceptions import ClientError
from pcapi.models import ApiErrors


class TooLateToDeleteStock(ClientError):
    def __init__(self):
        super().__init__(
            "global",
            "L'événement s'est terminé il y a plus de deux jours, la suppression est impossible.",
        )


class ImageValidationError(Exception):
    pass


class FileSizeExceeded(ImageValidationError):
    def __init__(self, max_size):
        super().__init__(f"Utilisez une image dont le poids est inférieur à {humanize.naturalsize(max_size)}")


class ImageTooSmall(ImageValidationError):
    def __init__(self, min_width, min_height):
        super().__init__(f"Utilisez une image plus grande (supérieure à {min_width}px par {min_height}px)")


class UnacceptedFileType(ImageValidationError):
    def __init__(self, accepted_types):
        super().__init__(f"Utilisez un format {', '.join(accepted_types)}")


class FailureToRetrieve(ImageValidationError):
    def __init__(self):
        super().__init__(
            "Nous n’avons pas pu récupérer cette image; vous pouvez la télécharger "
            'puis l’importer depuis l’onglet "Importer"'
        )


class MissingImage(ImageValidationError):
    def __init__(self):
        super().__init__("Nous n'avons pas réceptionné l'image, merci d'essayer à nouveau.")


class ThumbnailStorageError(ApiErrors):
    status_code = 500


class StockDoesNotExist(ApiErrors):
    status_code = 400


class WrongFormatInFraudConfigurationFile(Exception):
    pass
